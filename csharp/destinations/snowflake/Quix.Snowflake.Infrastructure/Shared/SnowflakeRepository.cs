using System;
using System.Collections;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using Quix.Snowflake.Domain.Common;
using Quix.Snowflake.Domain.Models;

namespace Quix.Snowflake.Infrastructure.Shared
{
    public abstract class SnowflakeRepository<T>
    {
        protected readonly IDbConnection dbConnection;
        protected readonly ILogger logger;
        private readonly SnowflakeModelSchema schema;

        protected SnowflakeRepository(IDbConnection dbConnection, ILogger logger)
        {
            this.dbConnection = dbConnection;
            this.logger = logger;
            this.schema = this.ValidateSchema();
        }

        private SnowflakeModelSchema ValidateSchema()
        {
            if (!SnowflakeSchemaRegistry.Registry.TryGetValue(typeof(T), out var snowflakeModelSchema)) throw new Exception($"Type {typeof(T)} has no snowflake schema registration");
            // TODO could do automatic validation of tables there etc
            return snowflakeModelSchema;
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

            var sb = new StringBuilder();
            var first = true;
            foreach (var statement in squashedStatements)
            {
                if (!first) sb.AppendLine(";");
                first = false;
                sb.Append(statement);
            }

            var updateStatement = sb.ToString();
            // TODO do something with it
            this.logger.LogInformation("Snowflake queries:{0}{1}", Environment.NewLine, updateStatement);
            return Task.CompletedTask;
        }

        private IEnumerable<string> GenerateDeleteStatement(DeleteManyModel<T> deleteDefinition)
        {
            var filterStatement = GenerateFilterStatement(deleteDefinition.Filter, true);
            List<KeyValuePair<MemberInfo, SnowflakeForeignTableSchema>> foreignTablesInvolved;
            foreignTablesInvolved = !string.IsNullOrWhiteSpace(filterStatement) ? this.schema.ForeignTables.Where(y => filterStatement.Contains($" {y.Value.ForeignTableName}.")).ToList() : new List<KeyValuePair<MemberInfo, SnowflakeForeignTableSchema>>();

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
                    sb.Append(this.schema.PrimaryKeyMemberInfo.Name);
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
                    yield return $"DELETE FROM {pair.Value.ForeignTableName} USING {this.schema.TableName} WHERE {pair.Value.ForeignTableName}.{pair.Value.KeyInForeignTable} = {this.schema.TableName}.{this.schema.PrimaryKeyMemberInfo.Name}";
                    continue;
                }
                yield return $"DELETE FROM {pair.Value.ForeignTableName} USING (select {this.schema.PrimaryKeyMemberInfo.Name} as {this.schema.PrimaryKeyMemberInfo.Name} from {this.schema.TableName} WHERE {filterStatement}) as {this.schema.TableName} WHERE {pair.Value.ForeignTableName}.{pair.Value.KeyInForeignTable} = {this.schema.TableName}.{this.schema.PrimaryKeyMemberInfo.Name}";
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
            var filter = mainTableFilter ?? $"{this.schema.PrimaryKeyMemberInfo.Name} = {GenerateSqlValueText(Utils.GetFieldOrPropValue(this.schema.PrimaryKeyMemberInfo, primaryModel))}";
            switch (updateDefinition)
            {
                case SetUpdateDefinition<T> setUpdateDefinition:
                    var memberExpression = Utils.GetMemberExpression(setUpdateDefinition.Selector);
                    if (!this.schema.ForeignTables.TryGetValue(memberExpression.Member, out var foreignTable))
                    {
                        var filterToUse = string.IsNullOrWhiteSpace(filter) ? filter : " WHERE " + filter;
                        yield return $"UPDATE {schema.TableName} SET {memberExpression.Member.Name} = {GenerateSqlValueText(setUpdateDefinition.Value)}{filterToUse}";
                        yield break;
                    }

                    var fullFilter = mainTableFilter ?? $"{this.schema.TableName}.{filter}";
                    if (!string.IsNullOrWhiteSpace(fullFilter)) fullFilter = " AND " + fullFilter;
                    yield return $"DELETE FROM {foreignTable.ForeignTableName} using {this.schema.TableName} where {foreignTable.ForeignTableName}.{foreignTable.KeyInForeignTable} = {this.schema.TableName}.{this.schema.PrimaryKeyMemberInfo.Name}{fullFilter}";
                    yield return GenerateForeignTableInsertStatement(foreignTable, setUpdateDefinition.Value as IEnumerable, Utils.GetFieldOrPropValue(this.schema.PrimaryKeyMemberInfo, primaryModel));
                    yield break;
                case MultipleUpdateDefinition<T> setUpdateDefinition:
                    foreach (var statement in setUpdateDefinition.UpdateDefinitions.SelectMany(updateDefinition => GenerateUpdateModelStatement(primaryModel, updateDefinition, mainTableFilter)))
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
                    break;
                case AndFilterDefinition<T> andFilter:
                    return string.Join(" AND ", andFilter.FilterDefinitions.Select(y=> GenerateFilterStatement(y, includeTable)));
                    break;                
                default:
                    throw new NotImplementedException($"The filter type {filter.GetType()} is not supported");
            }
            // TODO
            throw new NotImplementedException();
        }

        private string GetMemberExpressionNameForColumn(MemberInfo memberInfo, bool includeTable)
        {
            if (!includeTable) return memberInfo.Name;
            if (memberInfo.DeclaringType == typeof(T)) return $"{this.schema.TableName}.{memberInfo.Name}";
            if (!this.schema.ForeignTables.TryGetValue(memberInfo, out var foreignTable)) throw new Exception("Missing foreign table to build name expression");
            throw new NotImplementedException("Foreign table conditions are not yet properly supported");
            return $"{foreignTable.ForeignTableName}.{memberInfo.Name}";
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
                sb.Append(schemaColumnMemberInfo.Name);
            }
            
            sb.Append(") VALUES (");
            
            first = true;
            foreach (var value in values)
            {
                if (!first) sb.Append(", ");
                first = false;
                sb.Append(GenerateSqlValueText(value));
            }

            sb.Append(")");
            yield return sb.ToString();
            
            // Add foreign elements
            foreach (var pair in this.schema.ForeignTables)
            {
                var value = Utils.GetFieldOrPropValue(pair.Value.ForeignMemberInfo, model.Model);
                if (value == null) continue;
                yield return GenerateForeignTableInsertStatement(pair.Value, value as IEnumerable, Utils.GetFieldOrPropValue(this.schema.PrimaryKeyMemberInfo, model.Model));
            }
        }

        private string GenerateForeignTableInsertStatement(SnowflakeForeignTableSchema foreignTable, IEnumerable elements, object keyValueInForeignTable)
        {
            var keyValue = GenerateSqlValueText(keyValueInForeignTable);
            if (foreignTable.ColumnMemberInfos == null)
            {
                var columName = Utils.UnPluralize(foreignTable.ForeignMemberInfo.Name);
                var values = new List<string>();
                foreach (var element in elements)
                {
                    var rowValues = new List<string> { keyValue, GenerateSqlValueText(element) };
                    values.Add(string.Join(", ", rowValues));
                }

                return $"INSERT INTO {foreignTable.ForeignTableName} ({foreignTable.KeyInForeignTable}, {columName}) VALUES ({string.Join("), (", values)})";
            }
            
            if (foreignTable.ColumnMemberInfos.Count == 0) throw new Exception($"Not able to save values for table {foreignTable.ForeignTableName} due to unhandled scenario");
            var columnNames = foreignTable.ColumnMemberInfos.Select(y => y.Name).ToList();
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

            return $"INSERT INTO {foreignTable.ForeignTableName} ({foreignTable.KeyInForeignTable}, {string.Join(", ", columnNames)}) VALUES ({string.Join("), (", columnValues)})";
        }
        
        public IQueryable<T> GetAll()
        {
            throw new System.NotImplementedException();
        }
    }
}