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
                    case DeleteOneModel<T> deleteDefinition:
                        throw new NotImplementedException(); // TODO
                        break;
                    case InsertOneModel<T> insertDefinition:
                        statements.Add(GenerateInsertStatement(insertDefinition));
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

        private IEnumerable<string> SquashStatements(IEnumerable<string> statements)
        {
            var setRegex = new Regex("^UPDATE (.+) SET (.+) WHERE (.+)$", RegexOptions.Compiled);
            string previousStatement = null;
            Match previousMatch = null;
            
            foreach (var statement in statements)
            {
                var result = setRegex.Match(statement);
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
                            previousMatch = setRegex.Match(previousStatement);
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
            return GenerateUpdateModelStatement(model.Update, model.Filter);
        }
        
        private IEnumerable<string> GenerateUpdateModelStatement(UpdateDefinition<T> model, FilterDefinition<T> filterDefinition, string mainTableFilter = null)
        {
            var filter = mainTableFilter ?? GenerateFilterStatement(filterDefinition, false);
            if (!string.IsNullOrWhiteSpace(filter)) filter = " WHERE " + filter;
            switch (model)
            {
                case SetUpdateDefinition<T> setUpdateDefinition:
                    var memberExpression = Utils.GetMemberExpression(setUpdateDefinition.Selector);
                    if (this.schema.ForeignTables.TryGetValue(memberExpression.Member, out var foreignTable))
                    {
                        var fullFilter = GenerateFilterStatement(filterDefinition, true);
                        if (!string.IsNullOrWhiteSpace(fullFilter)) fullFilter = " AND " + fullFilter;
                        yield return $"DELETE FROM {foreignTable.ForeignTableName} using {this.schema.TableName} where {foreignTable.ForeignTableName}.{foreignTable.KeyInForeignTable} = {this.schema.TableName}.{this.schema.PrimaryKeyMemberInfo.Name}{fullFilter}";
                        if (foreignTable.ForeignMemberType.IsPrimitive || foreignTable.ForeignMemberType == typeof(string))
                        {
                            var columName = Utils.UnPluralize(foreignTable.ForeignMemberInfo.Name);
                            var values = new List<string>();
                            foreach (var value in setUpdateDefinition.Value as IEnumerable)
                            {
                                values.Add(GenerateSqlValueText(value));
                            }
                            
                            yield return $"INSERT INTO {foreignTable.ForeignTableName} ({columName}) VALUES ({string.Join("), (", values)})";
                            break;
                        }

                        var propertiesOrFields = foreignTable.ForeignMemberType.GetMembers(BindingFlags.Public | BindingFlags.Instance).Where(y=> y.MemberType == MemberTypes.Field || y.MemberType == MemberTypes.Property).ToList();
                        if (propertiesOrFields.Count == 0) throw new Exception($"Not able to save values for table {foreignTable.ForeignTableName} due to unhandled scenario");
                        var columnNames = propertiesOrFields.Select(y => y.Name).ToList();
                        var columnValues = new List<string>();
                        foreach (var value in setUpdateDefinition.Value as IEnumerable)
                        {
                            var rowValues = new List<string>();
                            foreach (var propertiesOrField in propertiesOrFields)
                            {
                                rowValues.Add(propertiesOrField.MemberType == MemberTypes.Field
                                    ? GenerateSqlValueText(((FieldInfo)propertiesOrField).GetValue(value))
                                    : GenerateSqlValueText(((PropertyInfo)propertiesOrField).GetValue(value)));
                            }
                            columnValues.Add(string.Join(", ", rowValues));
                        }

                        yield return $"INSERT INTO {foreignTable.ForeignTableName} ({string.Join(", ", columnNames)}) VALUES ({string.Join("), (", columnValues)})";
                        break;
                    }
                    
                    yield return $"UPDATE {schema.TableName} SET {memberExpression.Member.Name} = {GenerateSqlValueText(setUpdateDefinition.Value)}{filter}";
                    break;
                case MultipleUpdateDefinition<T> setUpdateDefinition:
                    foreach (var statement in setUpdateDefinition.UpdateDefinitions.SelectMany(model => GenerateUpdateModelStatement(model, filterDefinition, mainTableFilter)))
                    {
                        yield return statement;
                    }
                    break;
                default:
                    throw new NotImplementedException($"The update definition type {model.GetType()} is not supported");                
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
            return $"{foreignTable.ForeignTableName}.{memberInfo.Name}";
        }


        private string GenerateSqlValueText(object value)
        {
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
            };

            if (!typeDict.TryGetValue(memberInfoType, out var func)) return value.ToString();
            return func();
        }

        private string GenerateInsertStatement(InsertOneModel<T> model)
        {
            // depending on the type of update, generate the update//insert statement TODO
            throw new NotImplementedException();
        }
        
        public IQueryable<T> GetAll()
        {
            throw new System.NotImplementedException();
        }
    }
}