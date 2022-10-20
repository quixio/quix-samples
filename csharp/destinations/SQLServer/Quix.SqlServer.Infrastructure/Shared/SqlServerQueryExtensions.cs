using System;
using System.Data;

namespace Quix.SqlServer.Infrastructure.Shared
{
    public static class SqlServerQueryExtensions
    {
        public static void QuerySqlServer(this IDbConnection dbConnection, string sql, Action<IDataReader> readerAction)
        {
            using var cmd = dbConnection.CreateCommand();
            cmd.CommandText = sql;
            using var reader = cmd.ExecuteReader();
            readerAction(reader);
        }

        public static int ExecuteSqlServerStatement(this IDbConnection dbConnection, string sql, bool suppressErrorLogging = false)
        {
            try
            {
                if (dbConnection.State == ConnectionState.Closed)
                {
                    
                }
                using var cmd = dbConnection.CreateCommand();
                cmd.CommandText = sql;
                cmd.CommandTimeout = 30;
                return cmd.ExecuteNonQuery();
            }
            catch (Exception e)
            {
                if (!suppressErrorLogging)
                {
                    Console.WriteLine($"Sql statement failed: {sql}.");
                    Console.WriteLine(e);
                }
                throw;
            }
        }
    }
}