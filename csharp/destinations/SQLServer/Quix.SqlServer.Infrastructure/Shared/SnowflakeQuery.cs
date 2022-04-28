using System;
using System.Data;

namespace Quix.Snowflake.Infrastructure.Shared
{
    public static class SnowflakeQueryExtensions
    {
        public static void QuerySnowflake(this IDbConnection dbConnection, string sql, Action<IDataReader> readerAction)
        {
            using var cmd = dbConnection.CreateCommand();
            cmd.CommandText = sql;
            using var reader = cmd.ExecuteReader();
            readerAction(reader);
        }

        public static int ExecuteSnowflakeStatement(this IDbConnection dbConnection, string sql)
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
                Console.WriteLine(e);
                throw;
            }
        }
    }
}