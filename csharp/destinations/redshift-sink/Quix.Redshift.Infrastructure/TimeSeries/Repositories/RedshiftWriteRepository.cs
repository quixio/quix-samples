using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Amazon;
using Amazon.RedshiftDataAPIService;
using Amazon.RedshiftDataAPIService.Model;
using Amazon.Runtime;
using Microsoft.Extensions.Logging;
using Quix.Redshift.Domain.Common;
using Quix.Redshift.Domain.TimeSeries.Models;
using Quix.Redshift.Domain.TimeSeries.Repositories;
using Quix.Redshift.Infrastructure.TimeSeries.Models;

namespace Quix.Redshift.Infrastructure.TimeSeries.Repositories
{
    /// <summary>
    /// Implementation of <see cref="ITimeSeriesWriteRepository"/> for Redshift
    /// </summary>
    public class RedshiftWriteRepository : ITimeSeriesWriteRepository, IRequiresSetup
    {
        private readonly ILogger<RedshiftWriteRepository> logger;
        private readonly RedshiftConnectionConfiguration redshiftConfiguration;
        private readonly AmazonRedshiftDataAPIServiceClient client;
        private const string ParameterValuesTableName = "parametervalues";
        private const string EventValuesTableName = "eventvalues";
        private const string NumericParameterColumnFormat = "n_{0}";
        private const string StringParameterColumnFormat = "s_{0}";
        private const string StringEventColumnFormat = "{0}";
        private const string TagFormat = "tag_{0}";
        private const string TimeStampColumn = "timestamp";
        private static readonly string StreamIdColumn = string.Format(TagFormat, "streamid");
        private const int RedShiftMaxQueryLength = 95000; // 100K in theory, but better be safe

        private readonly HashSet<string> parameterColumns = new HashSet<string>();
        private readonly HashSet<string> eventColumns = new HashSet<string>();

        public RedshiftWriteRepository(
            ILogger<RedshiftWriteRepository> logger,
            RedshiftConnectionConfiguration redshiftConfiguration)
        {
            this.logger = logger ?? throw new ArgumentNullException(nameof(logger));
            this.redshiftConfiguration = redshiftConfiguration;
            if (redshiftConfiguration == null) throw new ArgumentNullException(nameof(redshiftConfiguration));
            this.client = new AmazonRedshiftDataAPIServiceClient(new BasicAWSCredentials(redshiftConfiguration.AccessKeyId, redshiftConfiguration.SecretAccessKey), RegionEndpoint.EnumerableAllRegions.First(y=> y.SystemName == redshiftConfiguration.Region));
        }

        public async Task Setup()
        {
            this.logger.LogDebug("Checking tables...");
            var tables = await this.client.ListTablesAsync(new ListTablesRequest() { Database = redshiftConfiguration.DatabaseName});
            // todo handle more than 1 page
            if (tables.Tables.All(y => !y.Name.Equals(ParameterValuesTableName, StringComparison.InvariantCultureIgnoreCase)))
            {
                this.logger.LogInformation("Creating table " + ParameterValuesTableName);
                await this.client.ExecuteStatementAsync(new ExecuteStatementRequest() { Database = redshiftConfiguration.DatabaseName, Sql = $"CREATE TABLE {ParameterValuesTableName} ({TimeStampColumn} BIGINT, {StreamIdColumn} VARCHAR(256)) SORTKEY ({TimeStampColumn}, {StreamIdColumn})"});
                this.logger.LogInformation("Creating table " + ParameterValuesTableName);
                parameterColumns.Add(TimeStampColumn);
                parameterColumns.Add(StreamIdColumn);
            }
            else
            {
                var tableDetails = await this.client.DescribeTableAsync(new DescribeTableRequest() {Database = redshiftConfiguration.DatabaseName, Table = ParameterValuesTableName});
                foreach (var columnMetadata in tableDetails.ColumnList)
                {
                    parameterColumns.Add(columnMetadata.Name);
                }
            }

            if (tables.Tables.All(y => !y.Name.Equals(EventValuesTableName, StringComparison.InvariantCultureIgnoreCase)))
            {
                this.logger.LogInformation("Creating table " + EventValuesTableName);
                await this.client.ExecuteStatementAsync(new ExecuteStatementRequest() { Database = redshiftConfiguration.DatabaseName, Sql = $"CREATE TABLE {EventValuesTableName} (timestamp BIGINT, {StreamIdColumn} VARCHAR(256)) SORTKEY ({TimeStampColumn}, {StreamIdColumn})"});
                this.logger.LogInformation("Created table " + EventValuesTableName);
                eventColumns.Add(TimeStampColumn);
                eventColumns.Add(StreamIdColumn);
            }
            else
            {
                var tableDetails = await this.client.DescribeTableAsync(new DescribeTableRequest() {Database = redshiftConfiguration.DatabaseName, Table = EventValuesTableName});
                foreach (var columnMetadata in tableDetails.ColumnList)
                {
                    eventColumns.Add(columnMetadata.Name);
                }
            }
            this.logger.LogInformation("Tables verified");
        }

        public async Task WriteTelemetryData(string topicId, IEnumerable<KeyValuePair<string, IEnumerable<ParameterDataRowForWrite>>> streamParameterData)
        {
            var sqlInserts = new Dictionary<string, List<string>>();
            
            var uniqueColumns = new Dictionary<string, string>();

            var totalVals = PrepareParameterSqlInserts(streamParameterData, uniqueColumns, sqlInserts);
            this.logger.LogTrace($"Saving {totalVals} parameter values to Redshift db");

            await VerifyColumns(uniqueColumns, parameterColumns, ParameterValuesTableName);

            var sqlInsertStatements = new List<string>();
            foreach (var statementPair in sqlInserts)
            {
                var sb = new StringBuilder();
                sb.Append(statementPair.Key);
                sb.Append(" ");
                foreach (var line in statementPair.Value)
                {
                    if (sb.Length > RedShiftMaxQueryLength)
                    {
                        sb.Remove(sb.Length - 1, 1);
                        sqlInsertStatements.Add(sb.ToString());
                        
                        sb = new StringBuilder();
                        sb.Append(statementPair.Key);
                        sb.Append(" ");                        
                    }
                    sb.Append(line);
                    sb.Append(',');
                }

                sb.Remove(sb.Length - 1, 1);
                sqlInsertStatements.Add(sb.ToString());
            }
            
            await this.client.BatchExecuteStatementAsync(new BatchExecuteStatementRequest() {  Database = redshiftConfiguration.DatabaseName, Sqls = sqlInsertStatements});
            
            this.logger.LogTrace($"Saved {totalVals} parameter values to Redshift db");
        }

        private static int PrepareParameterSqlInserts(IEnumerable<KeyValuePair<string, IEnumerable<ParameterDataRowForWrite>>> streamParameterData, Dictionary<string, string> uniqueColumns, Dictionary<string, List<string>> sqlInserts)
        {
            var totalValues = 0;
            foreach (var streamRows in streamParameterData)
            {
                foreach (var row in streamRows.Value)
                {
                    var numericValueCount = 0;
                    var stringValueCount = 0;

                    var headerSb = new StringBuilder();
                    headerSb.Append($"insert into {ParameterValuesTableName} ({TimeStampColumn},{StreamIdColumn}");

                    var valueSb = new StringBuilder();
                    valueSb.Append($"({row.Epoch + row.Timestamp},'{streamRows.Key}'");

                    if (row.TagValues != null && row.TagValues.Count > 0)
                    {
                        for (var index = 0; index < row.TagValues.Count; index++)
                        {
                            var kPair = row.TagValues[index];
                            if (string.IsNullOrEmpty(kPair.Value)) continue;
                            var name = string.Format(TagFormat, kPair.Key);
                            if (name.Equals(StreamIdColumn, StringComparison.InvariantCultureIgnoreCase)) continue;

                            valueSb.Append(",");
                            valueSb.Append($"'{kPair.Value}'");
                            
                            headerSb.Append(",");
                            headerSb.Append(name);
                            uniqueColumns[name] = "tag";
                        }
                    }

                    if (row.NumericValueCount > 0)
                    {
                        for (var i = 0; i < row.NumericValueCount; i++)
                        {
                            var name = string.Format(NumericParameterColumnFormat, row.NumericParameters[i]);
                            var value = row.NumericValues[i];
                            if (
                                double.IsNaN(value) ||
                                double.IsInfinity(value) ||
                                double.IsNegativeInfinity(value))
                            {
                                // NaNs or Infinity are ignored for this 
                                continue;
                            }

                            valueSb.Append(",");
                            valueSb.Append(value);

                            headerSb.Append(",");
                            headerSb.Append(name);
                            uniqueColumns[name] = "number";

                            numericValueCount++;
                        }
                    }

                    if (row.StringValueCount > 0)
                    {
                        for (var i = 0; i < row.StringValueCount; i++)
                        {
                            var name = string.Format(StringParameterColumnFormat, row.StringParameters[i]);
                            var value = row.StringValues[i];

                            valueSb.Append(",");
                            valueSb.Append($"'{value}'");

                            headerSb.Append(",");
                            headerSb.Append(name);
                            uniqueColumns[name] = "string";

                            stringValueCount++;
                        }
                    }

                    if (numericValueCount == 0 && stringValueCount == 0) continue; // non-persistable values only

                    headerSb.Append(") values");
                    valueSb.Append(")");

                    var header = headerSb.ToString();
                    if (!sqlInserts.TryGetValue(header, out var lines))
                    {
                        lines = new List<string>();
                        sqlInserts[header] = lines;
                    }
                    lines.Add(valueSb.ToString());
                    
                    totalValues += numericValueCount;
                    totalValues += stringValueCount;
                }
            }

            return totalValues;
        }

        private async Task VerifyColumns(Dictionary<string, string> columnsToHave, HashSet<string> existingColumns, string tableToVerify)
        {
            var columnsToAdd = columnsToHave.Keys.Except(existingColumns, StringComparer.InvariantCultureIgnoreCase).ToList();
            if (columnsToAdd.Count == 0) return;
            List<string> sqlStatements = new List<string>();
            foreach (var col in columnsToAdd)
            {
                switch (columnsToHave[col])
                {
                    case "string":
                        if (existingColumns.Add(col)) sqlStatements.Add($"ALTER TABLE {tableToVerify} ADD {col} VARCHAR(MAX)");
                        break;
                    case "tag":
                        if (existingColumns.Add(col)) sqlStatements.Add($"ALTER TABLE {tableToVerify} ADD {col} VARCHAR(512)");
                        break;
                    case "number":
                        if (existingColumns.Add(col)) sqlStatements.Add($"ALTER TABLE {tableToVerify} ADD {col} FLOAT8");
                        break;
                }
            }

            if (sqlStatements.Count == 0) return; // this is really just safe coding, not likely to ever happen
            await this.client.BatchExecuteStatementAsync(new BatchExecuteStatementRequest() {  Database = redshiftConfiguration.DatabaseName, Sqls = sqlStatements});
        }

        public async Task WriteTelemetryEvent(string topicId, IEnumerable<KeyValuePair<string, IEnumerable<EventDataRow>>> streamEventData)
        {
            var sqlInserts = new Dictionary<string, List<string>>();
            
            var uniqueColumns = new Dictionary<string, string>();

            var totalVals = PrepareEventSqlInserts(streamEventData, uniqueColumns, sqlInserts);
            this.logger.LogTrace($"Saving {totalVals} event values to Redshift db");

            await VerifyColumns(uniqueColumns, eventColumns, EventValuesTableName);

            var sqlInsertStatements = new List<string>();
            foreach (var statementPair in sqlInserts)
            {
                var sb = new StringBuilder();
                sb.Append(statementPair.Key);
                sb.Append(" ");
                foreach (var line in statementPair.Value)
                {
                    if (sb.Length > RedShiftMaxQueryLength)
                    {
                        sb.Remove(sb.Length - 1, 1);
                        sqlInsertStatements.Add(sb.ToString());
                        
                        sb = new StringBuilder();
                        sb.Append(statementPair.Key);
                        sb.Append(" ");                        
                    }
                    sb.Append(line);
                    sb.Append(',');
                }

                sb.Remove(sb.Length - 1, 1);
                sqlInsertStatements.Add(sb.ToString());
            }
            
            await this.client.BatchExecuteStatementAsync(new BatchExecuteStatementRequest() {  Database = redshiftConfiguration.DatabaseName, Sqls = sqlInsertStatements});
            
            this.logger.LogTrace($"Saved {totalVals} event values to Redshift db");

        }
        
        
        private static int PrepareEventSqlInserts(IEnumerable<KeyValuePair<string, IEnumerable<EventDataRow>>> streamEventData, Dictionary<string, string> uniqueColumns, Dictionary<string, List<string>> sqlInserts)
        {
            var totalValues = 0;
            foreach (var streamRows in streamEventData)
            {
                foreach (var row in streamRows.Value)
                {
                    var headerSb = new StringBuilder();
                    headerSb.Append($"insert into {EventValuesTableName} ({TimeStampColumn},{StreamIdColumn}");

                    var valueSb = new StringBuilder();
                    valueSb.Append($"({row.Timestamp},'{streamRows.Key}'");

                    if (row.TagValues != null && row.TagValues.Count > 0)
                    {
                        foreach(var kPair in row.TagValues)
                        {
                            if (string.IsNullOrEmpty(kPair.Value)) continue;
                            var name = string.Format(TagFormat, kPair.Key);
                            if (name.Equals(StreamIdColumn, StringComparison.InvariantCultureIgnoreCase)) continue;

                            valueSb.Append(",");
                            valueSb.Append($"'{kPair.Value}'");
                            
                            headerSb.Append(",");
                            headerSb.Append(name);
                            uniqueColumns[name] = "tag";
                        }
                    }

                    var eventColumnName = string.Format(StringEventColumnFormat, row.EventId);
                    var value = row.Value;

                    valueSb.Append(",");
                    valueSb.Append($"'{value}'");

                    headerSb.Append(",");
                    headerSb.Append(eventColumnName);
                    uniqueColumns[eventColumnName] = "string"; // will matter because of column verification

                    headerSb.Append(") values");
                    valueSb.Append(")");

                    var header = headerSb.ToString();
                    if (!sqlInserts.TryGetValue(header, out var lines))
                    {
                        lines = new List<string>();
                        sqlInserts[header] = lines;
                    }
                    lines.Add(valueSb.ToString());

                    totalValues++;
                }
            }

            return totalValues;
        }
    }
}
