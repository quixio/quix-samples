using System.Collections.Generic;
using Amazon.RedshiftDataAPIService.Model;
using Quix.Redshift.Infrastructure.TimeSeries.Models;

namespace Quix.Redshift.Infrastructure.TimeSeries.Factories
{
    public class RedshiftQueryFactory
    {
        private readonly RedshiftConnectionConfiguration configuration;

        public RedshiftQueryFactory(RedshiftConnectionConfiguration configuration)
        {
            this.configuration = configuration;
        }

        public ExecuteStatementRequest ExecuteStatementRequest(string sql)
        {
            var request = new ExecuteStatementRequest
            {
                Database = this.configuration.DatabaseName,
                Sql = sql
            };

            if (this.configuration.ClusterIdentifier != null)
            {
                request.ClusterIdentifier = this.configuration.ClusterIdentifier;
                request.DbUser = this.configuration.DbUser;
            }

            return request;
        }

        public ListTablesRequest ListTablesRequest()
        {
            var request = new ListTablesRequest
            {
                Database = this.configuration.DatabaseName,
            };

            if (this.configuration.ClusterIdentifier != null)
            {
                request.ClusterIdentifier = this.configuration.ClusterIdentifier;
                request.DbUser = this.configuration.DbUser;
            }
            return request;
        }

        public DescribeTableRequest DescribeTableRequest(string table)
        {
            var request = new DescribeTableRequest
            {
                Database = this.configuration.DatabaseName,
                Table = table
            };

            if (this.configuration.ClusterIdentifier != null)
            {
                request.ClusterIdentifier = this.configuration.ClusterIdentifier;
                request.DbUser = this.configuration.DbUser;
            }
            return request;
        }

        public BatchExecuteStatementRequest BatchExecuteStatementRequest(List<string> sqls)
        {
            var request = new BatchExecuteStatementRequest
            {
                Database = this.configuration.DatabaseName,
                Sqls = sqls
            };

            if (this.configuration.ClusterIdentifier != null)
            {
                request.ClusterIdentifier = this.configuration.ClusterIdentifier;
                request.DbUser = this.configuration.DbUser;
            }

            return request;
        }

    }
}
