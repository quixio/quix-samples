using System;
using System.Data;

namespace Quix.Snowflake.Infrastructure.Shared
{
    public class SnowflakeQuery
    {
        public static IDataReader ExecuteSnowflakeRead(IDbConnection dbConnection, string sql)
        {
            IDbCommand cmd = dbConnection.CreateCommand();
            cmd.CommandText = sql;
            return cmd.ExecuteReader();
        }

        public static int ExecuteSnowFlakeNonQuery(IDbConnection dbConnection, string sql)
        {
            try
            {
                IDbCommand cmd = dbConnection.CreateCommand();
                cmd.CommandText = sql;
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