using System;
using System.Collections;
using System.Collections.Generic;
using System.Data;
using System.Diagnostics;
using System.Linq;
using System.Linq.Expressions;
using System.Reflection;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using Quix.Snowflake.Domain.Common;

namespace Quix.Snowflake.Infrastructure.Shared
{
    public abstract class SnowflakeRepository<T> where T : new()
    {
        protected readonly IDbConnection SnowflakeDbConnection;
        protected readonly ILogger logger;
        private readonly SnowflakeModelSchema schema;
        private const string InformationSchema = "PUBLIC"; // Maybe this could come from config ?
        private const int MaxQueryByteSize = 1024 * 1024 * 8 - 1024*64; // 1 MB, -64 KB for safety margin

        protected SnowflakeRepository(IDbConnection snowflakeDbConnection, ILogger logger)
        {
            this.SnowflakeDbConnection = snowflakeDbConnection;
            this.logger = logger;
            this.schema = this.ValidateSchema();
            Initialize();
        }

        public Task BulkWrite(IEnumerable<WriteModel<T>> writeModels)
        {
            // iterate the updates
            var statements = new List<string>();
            foreach (var models in writeModels)
            {
                switch (models)
                {
                    case UpdateOneModel<T> updateDefinition:
                        statements.AddRange(GenerateUpdateStatement(updateDefinition));
                        break;
                    case DeleteManyModel<T> deleteDefinition:
                        statements.AddRange(GenerateDeleteStatement(deleteDefinition));
                        break;
                    case InsertOneModel<T> insertDefinition:
                        statements.AddRange(GenerateInsertStatement(insertDefinition));
                        break;
                }
            }

            var squashedStatements = SquashStatements(statements);

            ExecuteStatements(squashedStatements);
            return Task.CompletedTask;
        }

        private void ExecuteStatements(IEnumerable<string> statements)
        {
            var totalStatementSize = 0;
            var sb = new StringBuilder();
            var first = true;
            var begin = "BEGIN\n";
            var end = ";\nEND";
            var beginEndLength = Encoding.UTF8.GetByteCount(begin) + Encoding.UTF8.GetByteCount(end);
            var separator = ";\n"; // \n so it is somewhat human readable in console
            var separatorSize = Encoding.UTF8.GetByteCount(separator);
            var segmentCount = 0;
            foreach (var statement in statements)
            {
                var statementSize = Encoding.UTF8.GetByteCount(statement);
                if (!first)
                {
                    sb.Append(separator);
                    statementSize += separatorSize;

                    // check if we would be over the limit with the new statement
                    if (statementSize + totalStatementSize + beginEndLength > MaxQueryByteSize)
                    {
                        // if so, send it already
                        sb.Insert(0, begin);
                        sb.Append(end);
                        ExecuteStatement(sb.ToString());
                        sb.Clear();
                        totalStatementSize = 0;
                        segmentCount = 0;
                        first = true;
                    }
                }
                else first = false;

                sb.Append(statement);
                totalStatementSize += statementSize;
                segmentCount++;
            }

            if (segmentCount > 1)
            {
                sb.Insert(0, begin);
                sb.Append(end);
            }
            ExecuteStatement(sb.ToString());
        }

        private void ExecuteStatement(string statement)
        {
            if (string.IsNullOrWhiteSpace(statement)) return;
            IDisposable timer = null;

            var sw = Stopwatch.StartNew();
            void setTimer()
            {
                timer = InaccurateSharedTimer.Instance.Subscribe(10, () =>
                {
                    this.logger.LogInformation("Executing data write Snowflake statement is taking longer ({0:g}) than expected...", sw.Elapsed);
                    timer.Dispose();
                    setTimer();
                });
            }
            setTimer();
            
            this.logger.LogTrace("Executing Snowflake statement:{0}{1}", Environment.NewLine, statement);
            try
            {
                SnowflakeDbConnection.ExecuteSnowflakeStatement(statement);
            }
            catch (Exception ex)
            {
                this.logger.LogError("Failed to execute Snowflake statement:{0}{1}", Environment.NewLine, statement);
                throw;
            }
            finally
            {
                timer.Dispose();
            }

            sw.Stop();
            this.logger.LogDebug("Executed Snowflake statement in {0:g}:{1}{2}", sw.Elapsed, Environment.NewLine, statement);
        }

        public Task<IList<T>> Get(FilterDefinition<T> filter)
        {
            var filterStatement = GenerateFilterStatement(filter, false);
            if (!string.IsNullOrWhiteSpace(filterStatement)) filterStatement = $" WHERE {filterStatement}";
            
            // Primary Table
            var primaryfieldMap = this.schema.ColumnMemberInfos.ToDictionary(y => y, GetColumName).ToList(); // Guarantee AN order
            var columns = string.Join(", ", primaryfieldMap.Select(y=> y.Value));
            var selectStatement = $"SELECT {columns} FROM {this.schema.TableName}{filterStatement}";
            this.logger.LogTrace("Snowflake query statement: {0}", selectStatement);
            var sw = Stopwatch.StartNew();
            List<T> result = null;
            SnowflakeDbConnection.QuerySnowflake(selectStatement, reader =>
            {
                sw.Stop();
                this.logger.LogDebug("Executed Snowflake query statement in {0:g}: {1}", sw.Elapsed, selectStatement);
                result = ParseModels<T>(reader, primaryfieldMap, this.schema.TypeMapFrom).ToList();
            });

            // TODO set foreign table values ... Would reduce the updates on first encounter, but after that it is cached anyway...

            return Task.FromResult(result as IList<T>);
        }

        private IEnumerable<TK> ParseModels<TK>(IDataReader reader, List<KeyValuePair<MemberInfo, string>> keyValuePairs, Dictionary<MemberInfo, Dictionary<object, object>> memberMap) where TK : new()
        {
            var values = new object[keyValuePairs.Count];
            
            while (reader.Read())
            {
                var model = new TK();
                reader.GetValues(values);
                var counter = 0;
                foreach (var field in keyValuePairs)
                {
                    var value = values[counter];
                    if (memberMap != null && memberMap.TryGetValue(field.Key, out var map))
                    {
                        value = map[value];
                    }

                    if (value == DBNull.Value) value = null;
                    try
                    {
                        Utils.SetFieldOrPropValue(field.Key, model, value);
                    }
                    catch (Exception ex)
                    {
                        if (value == null) logger.LogError("Failed to set field {0} to value {1}", field.Key.Name, value);
                        else
                        {
                            var valType = value.GetType();
                            var targetType = Utils.GetMemberInfoType(field.Key);
                            if (valType == targetType)
                            {
                                logger.LogError("Failed to set field {0} to value {1}", field.Key.Name, value);
                            }

                            var asNullable = Nullable.GetUnderlyingType(targetType);
                            if (asNullable != null) targetType = asNullable;

                            value = Convert.ChangeType(value, targetType);
                            Utils.SetFieldOrPropValue(field.Key, model, value);
                        }

                    }

                    counter++;
                }
                yield return model;
            }
        }

        private IEnumerable<string> GenerateDeleteStatement(DeleteManyModel<T> deleteDefinition)
        {
            var filterStatement = GenerateFilterStatement(deleteDefinition.Filter, true);
            List<KeyValuePair<MemberInfo, SnowflakeForeignTableSchema>> foreignTablesInvolved;
            foreignTablesInvolved = !string.IsNullOrWhiteSpace(filterStatement)
                ? this.schema.ForeignTables.Where(y => filterStatement.Contains($" {y.Value.ForeignTableName}.")).ToList()
                : new List<KeyValuePair<MemberInfo, SnowflakeForeignTableSchema>>();

            if (this.schema.ForeignTables.Any(y => filterStatement.Contains($" {y.Value.ForeignTableName}.")))
            {
                throw new NotImplementedException(); // Not yet properly handled later in cascade delete etc
                var sb = new StringBuilder();
                sb.Append("DELETE FROM ");
                sb.Append(this.schema.TableName);
                sb.Append(" USING ");
                var first = true;
                foreach (var pair in foreignTablesInvolved)
                {
                    if (!first) sb.Append(", ");
                    first = false;
                    sb.Append(pair.Value.ForeignTableName);
                }

                sb.Append(" WHERE ");
                first = true;
                foreach (var pair in foreignTablesInvolved)
                {
                    if (!first) sb.Append(", ");
                    first = false;
                    sb.Append(pair.Value.ForeignTableName);
                    sb.Append(".");
                    sb.Append(pair.Value.KeyInForeignTable);
                    sb.Append(" = ");
                    sb.Append(this.schema.TableName);
                    sb.Append(".");
                    sb.Append(GetColumName(this.schema.PrimaryKeyMemberInfo));
                }

                yield return sb.ToString();
            }
            else
            {
                filterStatement = GenerateFilterStatement(deleteDefinition.Filter, false);
                var filterToUse = string.IsNullOrWhiteSpace(filterStatement) ? filterStatement : $" WHERE {filterStatement}";
                yield return $"DELETE FROM {this.schema.TableName}{filterToUse}";
            }

            // cascade delete Foreign Table entries
            if (this.schema.ForeignTables.Count == 0) yield break;
            foreach (var pair in this.schema.ForeignTables)
            {
                if (string.IsNullOrWhiteSpace(filterStatement))
                {
                    yield return $"DELETE FROM {pair.Value.ForeignTableName} USING {this.schema.TableName} WHERE {pair.Value.ForeignTableName}.{pair.Value.KeyInForeignTable} = {this.schema.TableName}.{GetColumName(this.schema.PrimaryKeyMemberInfo)}";
                    continue;
                }

                yield return $"DELETE FROM {pair.Value.ForeignTableName} USING (select {GetColumName(this.schema.PrimaryKeyMemberInfo)} as {GetColumName(this.schema.PrimaryKeyMemberInfo)} from {this.schema.TableName} WHERE {filterStatement}) as {this.schema.TableName} WHERE {pair.Value.ForeignTableName}.{pair.Value.KeyInForeignTable} = {this.schema.TableName}.{GetColumName(this.schema.PrimaryKeyMemberInfo)}";
            }
        }

        private IEnumerable<string> SquashStatements(IEnumerable<string> statements)
        {
            var updateRegex = new Regex("^UPDATE (.+) SET (.+) WHERE (.+)$", RegexOptions.Compiled);
            string previousStatement = null;
            Match previousMatch = null;

            foreach (var statement in statements)
            {
                var result = updateRegex.Match(statement);
                if (previousStatement != null)
                {
                    if (!previousMatch.Success)
                    {
                        yield return previousStatement;
                    }
                    else
                    {
                        if (!result.Success)
                        {
                            yield return previousStatement;
                        }
                        else if (result.Groups[1].Value == previousMatch.Groups[1].Value && result.Groups[3].Value == previousMatch.Groups[3].Value)
                        {
                            var prevSet = previousMatch.Groups[2].Value;
                            var currSet = result.Groups[2].Value;
                            if (prevSet.Contains(currSet)) continue; // just ignore it, exact same set...
                            previousStatement = $"UPDATE {result.Groups[1]} SET {prevSet}, {currSet} WHERE {result.Groups[3].Value}";
                            previousMatch = updateRegex.Match(previousStatement);
                            continue;
                        }
                        else
                        {
                            yield return previousStatement;
                        }
                    }
                }

                previousMatch = result;
                previousStatement = statement;
            }

            yield return previousStatement;
        }


        private IEnumerable<string> GenerateUpdateStatement(UpdateOneModel<T> model)
        {
            return GenerateUpdateModelStatement(model.ModelToUpdate, model.Update);
        }

        private IEnumerable<string> GenerateUpdateModelStatement(T primaryModel, UpdateDefinition<T> updateDefinition, string mainTableFilter = null)
        {
            var filter = mainTableFilter ?? $"{GetColumName(this.schema.PrimaryKeyMemberInfo)} = {GenerateSqlValueText(Utils.GetFieldOrPropValue(this.schema.PrimaryKeyMemberInfo, primaryModel))}";
            switch (updateDefinition)
            {
                case SetUpdateDefinition<T> setUpdateDefinition:
                    MemberExpression memberExpression = null;
                    try
                    {
                        memberExpression = Utils.GetMemberExpression(setUpdateDefinition.Selector);
                    }
                    catch (Exception ex)
                    {
                        
                    }

                    if (!this.schema.ForeignTables.TryGetValue(memberExpression.Member, out var foreignTable))
                    {
                        var filterToUse = string.IsNullOrWhiteSpace(filter) ? filter : " WHERE " + filter;
                        yield return $"UPDATE {schema.TableName} SET {GetColumName(memberExpression.Member)} = {GenerateSqlValueText(setUpdateDefinition.Value)}{filterToUse}";
                        yield break;
                    }

                    var fullFilter = mainTableFilter ?? $"{this.schema.TableName}.{filter}";
                    if (!string.IsNullOrWhiteSpace(fullFilter)) fullFilter = " AND " + fullFilter;
                    yield return
                        $"DELETE FROM {foreignTable.ForeignTableName} using {this.schema.TableName} where {foreignTable.ForeignTableName}.{foreignTable.KeyInForeignTable} = {this.schema.TableName}.{GetColumName(this.schema.PrimaryKeyMemberInfo)}{fullFilter}";
                    
                    var vals =  GenerateForeignTableInsertStatement(foreignTable, setUpdateDefinition.Value as IEnumerable, Utils.GetFieldOrPropValue(this.schema.PrimaryKeyMemberInfo, primaryModel));
                    if (!string.IsNullOrWhiteSpace(vals)) yield return vals;
                    yield break;
                case MultipleUpdateDefinition<T> setUpdateDefinition:
                    foreach (var statement in setUpdateDefinition.UpdateDefinitions.SelectMany(updateDefinition =>
                                 GenerateUpdateModelStatement(primaryModel, updateDefinition, mainTableFilter)))
                    {
                        yield return statement;
                    }

                    yield break;
                default:
                    throw new NotImplementedException($"The update definition type {updateDefinition.GetType()} is not supported");
            }
        }


        private string GenerateFilterStatement(FilterDefinition<T> filter, bool includeTable)
        {
            if (filter == null) return string.Empty;

            switch (filter)
            {
                case EqFilterDefinition<T> eqFilter:
                    var memberExpression = Utils.GetMemberExpression(eqFilter.Selector);
                    return GetMemberExpressionNameForColumn(memberExpression.Member, includeTable) + " = " + GenerateSqlValueText(eqFilter.Value);
                case AndFilterDefinition<T> andFilter:
                    return string.Join(" AND ", andFilter.FilterDefinitions.Select(y => GenerateFilterStatement(y, includeTable)));
                case InFilterDefinition<T> inFilter:
                    var vals = GenerateValueListStatement(inFilter.Values);
                    if (string.IsNullOrWhiteSpace(vals)) return "FALSE";
                    memberExpression = Utils.GetMemberExpression(inFilter.Selector);
                    return $"{GetMemberExpressionNameForColumn(memberExpression.Member, includeTable)} IN ({vals})";
                case NotFilterDefinition<T> notFilter:
                    switch (notFilter.Filter)
                    {
                        case InFilterDefinition<T>:
                            return $"NOT {GenerateFilterStatement(notFilter.Filter, includeTable)}";
                        case EqFilterDefinition<T>:
                            var statement = GenerateFilterStatement(notFilter.Filter, includeTable);
                            var firstEq = statement.IndexOf(" = ");
                            statement = statement.Substring(0, firstEq) + " != " + statement.Substring(firstEq + 3);
                            return statement;
                    }

                    return $"NOT ({GenerateFilterStatement(notFilter.Filter, includeTable)})";
                default:
                    throw new NotImplementedException($"The filter type {filter.GetType()} is not supported");
            }
        }

        private string GetMemberExpressionNameForColumn(MemberInfo memberInfo, bool includeTable)
        {
            if (!includeTable) return GetColumName(memberInfo);
            if (memberInfo.DeclaringType == typeof(T)) return $"{this.schema.TableName}.{GetColumName(memberInfo)}";
            if (!this.schema.ForeignTables.TryGetValue(memberInfo, out var foreignTable)) throw new Exception("Missing foreign table to build name expression");
            throw new NotImplementedException("Foreign table conditions are not yet properly supported");
            return $"{foreignTable.ForeignTableName}.{GetColumName(memberInfo)}";
        }


        private static string GenerateSqlValueText(object value)
        {
            if (value == null) return "NULL";
            var memberInfoType = Utils.GetMemberInfoType(value.GetType());

            if (memberInfoType.IsGenericType)
            {
                memberInfoType = memberInfoType.GenericTypeArguments.First(); // dirty but works for us
            }

            if (memberInfoType.IsEnum)
            {
                return "'" + value + "'";
            }

            var typeDict = new Dictionary<Type, Func<string>>()
            {
                {
                    typeof(string), () => "'" + value.ToString().Replace("'", "\\'") + "'"
                },
                {
                    typeof(DateTime), () => "'" + ((DateTime)value).ToString("O").Replace("'", "\\'") + "'"
                },
            };

            if (!typeDict.TryGetValue(memberInfoType, out var func)) return value.ToString();
            return func();
        }

        private IEnumerable<string> GenerateInsertStatement(InsertOneModel<T> model)
        {
            var sb = new StringBuilder();
            sb.Append($"INSERT INTO ");
            sb.Append(this.schema.TableName);
            sb.Append(" (");
            var first = true;
            var values = new List<object>();
            foreach (var schemaColumnMemberInfo in this.schema.ColumnMemberInfos)
            {
                var value = Utils.GetFieldOrPropValue(schemaColumnMemberInfo, model.Model);
                if (value == null) continue;
                values.Add(value);
                if (!first) sb.Append(", ");
                first = false;
                sb.Append(GetColumName(schemaColumnMemberInfo));
            }

            sb.Append(") VALUES (");
            GenerateValueListStatement(values, sb);
            sb.Append(")");
            yield return sb.ToString();

            // Add foreign elements
            foreach (var pair in this.schema.ForeignTables)
            {
                var value = Utils.GetFieldOrPropValue(pair.Value.ForeignMemberInfo, model.Model);
                if (value == null) continue;
                var vals = GenerateForeignTableInsertStatement(pair.Value, value as IEnumerable, Utils.GetFieldOrPropValue(this.schema.PrimaryKeyMemberInfo, model.Model));
                if (!string.IsNullOrWhiteSpace(vals)) yield return vals;
            }
        }

        private static void GenerateValueListStatement(IEnumerable values, StringBuilder sb)
        {
            var first = true;
            foreach (var value in values)
            {
                if (!first) sb.Append(", ");
                first = false;
                sb.Append(GenerateSqlValueText(value));
            }
        }

        private static string GenerateValueListStatement(IEnumerable values)
        {
            var sb = new StringBuilder();
            GenerateValueListStatement(values, sb);
            return sb.ToString();
        }

        private string GenerateForeignTableInsertStatement(SnowflakeForeignTableSchema foreignTable, IEnumerable elements, object keyValueInForeignTable)
        {
            var keyValue = GenerateSqlValueText(keyValueInForeignTable);
            if (foreignTable.ColumnMemberInfos == null)
            {
                var columName = Utils.UnPluralize(GetColumName(foreignTable.ForeignMemberInfo));
                var values = new List<string>();
                foreach (var element in elements)
                {
                    values.Add(GenerateValueListStatement(new[] { keyValue, element }));
                }

                if (values.Count == 0) return null;

                return $"INSERT INTO {foreignTable.ForeignTableName} ({foreignTable.KeyInForeignTable}, {columName}) VALUES ({string.Join("), (", values)})";
            }

            if (foreignTable.ColumnMemberInfos.Count == 0) throw new Exception($"Not able to save values for table {foreignTable.ForeignTableName} due to unhandled scenario");
            var columnNames = foreignTable.ColumnMemberInfos.Select(GetColumName).ToList();
            var columnValues = new List<string>();
            foreach (var value in elements)
            {
                var rowValues = new List<string> { keyValue };
                foreach (var propertiesOrField in foreignTable.ColumnMemberInfos)
                {
                    var underlyingType = Utils.GetMemberInfoType(propertiesOrField);
                    if (typeof(IEnumerable).IsAssignableFrom(underlyingType) && typeof(string) != underlyingType) throw new Exception("Foreign table to a foreign table is not supported");
                    rowValues.Add(GenerateSqlValueText(Utils.GetFieldOrPropValue(propertiesOrField, value)));
                }

                columnValues.Add(string.Join(", ", rowValues));
            }

            if (columnValues.Count == 0) return null;

            return $"INSERT INTO {foreignTable.ForeignTableName} ({foreignTable.KeyInForeignTable}, {string.Join(", ", columnNames)}) VALUES ({string.Join("), (", columnValues)})";
        }

        private static string GetColumName(MemberInfo memberInfo)
        {
            if (memberInfo == null) return null;
            return ConvertToSnowflakeColumnName(memberInfo.Name);
        }
        
        private static string ConvertToSnowflakeColumnName(string name)
        {
            return $"\"{name.ToUpperInvariant()}\"";
        }

#region Initialize

        private SnowflakeModelSchema ValidateSchema()
        {
            if (!SnowflakeSchemaRegistry.Registry.TryGetValue(typeof(T), out var snowflakeModelSchema))
                throw new Exception($"Type {typeof(T)} has no snowflake schema registration");
            return snowflakeModelSchema;
        }

        private void Initialize()
        {
            this.logger.LogDebug("Checking tables...");

            // verify tables exist, if not create them
            VerifyTables();

            this.logger.LogInformation("Tables verified");
        }

        private bool TableExists(string table)
        {
            var checkForTableSql = $"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = '{InformationSchema}' AND table_name = '{table.ToUpperInvariant()}')";
            var exists = false;
            SnowflakeDbConnection.QuerySnowflake(checkForTableSql, existingTablesReader =>
            {
                while (existingTablesReader.Read())
                {
                    if (existingTablesReader.GetString(0) == "1")
                        exists = true;
                }
            });

            return exists;
        }

        private void VerifyTables()
        {
            var expectedColumns = this.schema.ColumnMemberInfos.ToDictionary(GetColumName, y => MapDotnetTypeToSnowflakeType(Utils.GetMemberInfoType(y)));

            VerifyTable(this.schema.TableName, expectedColumns, GetColumName(this.schema.ClusterKeyMemberInfo));

            foreach (var foreignTableSchema in this.schema.ForeignTables)
            {

                var ftExpectedColumns = foreignTableSchema.Value.ColumnMemberInfos != null
                        ? foreignTableSchema.Value.ColumnMemberInfos.ToDictionary(GetColumName, y => MapDotnetTypeToSnowflakeType(Utils.GetMemberInfoType(y)))
                        : new Dictionary<string, string>() {{Utils.UnPluralize(GetColumName(foreignTableSchema.Value.ForeignMemberInfo)), MapDotnetTypeToSnowflakeType(foreignTableSchema.Value.ForeignMemberType)}};
                ftExpectedColumns[ConvertToSnowflakeColumnName(foreignTableSchema.Value.KeyInForeignTable)] = MapDotnetTypeToSnowflakeType(Utils.GetMemberInfoType(this.schema.PrimaryKeyMemberInfo));

                VerifyTable(foreignTableSchema.Value.ForeignTableName, ftExpectedColumns, ConvertToSnowflakeColumnName(foreignTableSchema.Value.KeyInForeignTable));
            }
        }

        private void VerifyTable(string tableName, Dictionary<string, string> columnToTypes, string clusterColumn)
        {
            if (!TableExists(tableName))
            {
                // if not
                // create the table
                SnowflakeDbConnection.ExecuteSnowflakeStatement(
                    $"CREATE TABLE {InformationSchema}.{tableName} ({string.Join(", ", columnToTypes.Select(y => $"{y.Key} {y.Value}"))})");

                if (!string.IsNullOrEmpty(clusterColumn)) SnowflakeDbConnection.ExecuteSnowflakeStatement($"ALTER TABLE {InformationSchema}.{tableName} CLUSTER BY ({clusterColumn})");

                this.logger.LogInformation($"Table {tableName} created");
            }
            else
            {
                // otherwise
                // get the tables existing column names and add them to the list
                var sql = $"SELECT COLUMN_NAME FROM information_schema.columns WHERE table_name = '{tableName.ToUpperInvariant()}'";
                SnowflakeDbConnection.QuerySnowflake(sql, existingColumnNameReader =>
                {

                    var cols = new List<string>();
                    while (existingColumnNameReader.Read())
                    {
                        cols.Add(ConvertToSnowflakeColumnName(existingColumnNameReader.GetString(0)));
                    }
                    if (cols.Intersect(columnToTypes.Keys).OrderBy(y=> y).Count() != columnToTypes.Count) throw new NotImplementedException($"Table {tableName} does not have the expected columns");
                });
                

                this.logger.LogInformation($"Table {tableName} verified");
            }
        }

        private string MapDotnetTypeToSnowflakeType(Type type)
        {
            if (type.IsGenericType)
            {
                var nullableType = Nullable.GetUnderlyingType(type);
                if (nullableType != null) type = nullableType;
            }
            
            if (typeof(Enum).IsAssignableFrom(type))
            {
                return "VARCHAR(100)";
            }

            if (typeof(string).IsAssignableFrom(type))
            {
                return "VARCHAR";
            }

            if (typeof(DateTime).IsAssignableFrom(type))
            {
                return "DATETIME";
            }

            if (typeof(bool).IsAssignableFrom(type))
            {
                return "BOOLEAN";
            }

            if (typeof(long).IsAssignableFrom(type))
            {
                return "NUMBER(" + long.MaxValue.ToString().Length + ",0)";
            }
            
            if (typeof(Int32).IsAssignableFrom(type))
            {
                return "NUMBER(" + Int32.MaxValue.ToString().Length + ",0)";
            }     
            
            if (typeof(double).IsAssignableFrom(type))
            {
                return "NUMBER";
            }

            throw new NotImplementedException($"Type {type.FullName} is not implemented for snowflake storage");
        }

#endregion
    }
}