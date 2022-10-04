using System;
using System.Data;

namespace Quix.SqlServer.Infrastructure.Shared
{
    public static class SqlServerQueryExtensions
    {
        public static void QuerySqlServer(this IDbConnection dbConnection, string sql, Action<IDataReader> readerAction)
        {
            Console.WriteLine("QuerySqlServer::Connection hash=" + dbConnection.GetHashCode());

            using var cmd = dbConnection.CreateCommand();
            cmd.CommandText = sql;
            if (dbConnection.State != ConnectionState.Open)
            {
                dbConnection.Close();
                dbConnection.Open();
            }
            using var reader = cmd.ExecuteReader();
            readerAction(reader);
        }

        public static int ExecuteSqlServerStatement(this IDbConnection dbConnection, string sql, bool suppressErrorLogging = false, bool retry = true)
        {
            try
            {
                Console.WriteLine("ExecuteSqlServerStatement::Connection hash=" + dbConnection.GetHashCode());
                
                if (dbConnection.State != ConnectionState.Open)
                {
                    Console.WriteLine("Connection is not Open. Attempting to open it...");
                    dbConnection.Close();
                    dbConnection.Open();
                    Console.WriteLine("Connection Opened!");
                }

                using var cmd = dbConnection.CreateCommand();
                cmd.CommandText = sql;
                cmd.CommandTimeout = 30;
                return cmd.ExecuteNonQuery();
            }
            catch (TimeoutException e)
            {
                if (!retry)
                {
                    Console.WriteLine("Failed to execute SqlServer statement:{0}{1}", Environment.NewLine, sql);
                    throw;
                }

                if (dbConnection.State == ConnectionState.Open)
                {
                    Console.WriteLine("Cycling connection before retrying..");
                    dbConnection.Close();
                    dbConnection.Open();
                }

                //try 1 more time..
                ExecuteSqlServerStatement(dbConnection, sql, false, false);

                Console.WriteLine("Retry succeeded");

                if (!suppressErrorLogging) Console.WriteLine(e);
                throw;
            }
            catch (Exception ex)
            {
                if (!suppressErrorLogging) Console.WriteLine(ex);
                throw;
            }
        }
    }
}