using System;
using System.Threading.Tasks;
using Microsoft.Data.SqlClient;
using Microsoft.Extensions.Logging;

namespace Quix.SqlServer.Infrastructure.Shared
{
    public class SqlServerConnectionValidatorService
    {
        private readonly SqlConnection connection;
        //private readonly SqlServerDbConnection connection;
        private readonly ILogger<SqlServerConnectionValidatorService> logger;

        public SqlServerConnectionValidatorService(SqlConnection connection, ILoggerFactory loggerFactory)
        //public SqlServerConnectionValidatorService(SqlServerDbConnection connection, ILoggerFactory loggerFactory)
        {
            this.logger = loggerFactory.CreateLogger<SqlServerConnectionValidatorService>();
            this.connection = connection;
        }

        public void Validate()
        {
            this.logger.LogInformation($"Connecting to SqlServer database {connection.Database}");
            var openTask = Task.Run(() =>
            {
                connection.Open();
            });
            Task.WaitAny(openTask, Task.Delay(10000));
            if (openTask.IsFaulted) throw openTask.Exception ?? new Exception("Connection failed");
            if (!openTask.IsCompleted) throw new TimeoutException("Connection timed out"); 
            this.logger.LogInformation($"Connected to SqlServer database {connection.Database}");
            this.connection.ExecuteSqlServerStatement("SELECT 1");
        }
    }
}