using System;
using System.Data;

namespace Quix.Snowflake.Infrastructure.Shared
{
    public static class SnowflakeQueryExtensions
    {
        public static IDataReader QuerySnowflake(this IDbConnection dbConnection, string sql)
        {
            IDbCommand cmd = dbConnection.CreateCommand();
            cmd.CommandText = sql;
            return cmd.ExecuteReader();
        }

        public static int ExecuteSnowflakeStatement(this IDbConnection dbConnection, string sql)
        {
            try
            {
                IDbCommand cmd = dbConnection.CreateCommand();
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