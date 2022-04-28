namespace Quix.SqlServer.Infrastructure.TimeSeries.Models
{
    /// <summary>
    /// SqlServer database connection configuration.
    /// </summary>
    public class SqlServerConnectionConfiguration
    {
        public string Locator { get; set; }
        public string Region { get; set; }
        public string User { get; set; }
        public string Password { get; set; }
        public string Database { get; set; }
        
        public string ConnectionString
        {
            get
            {
                //return "Server=localhost\\SQLEXPRESS;Database=test;Trusted_Connection=True;Trust Server Certificate=True;";
                return
                    "Server=tcp:steave-sql-test.database.windows.net,1433;Database=test;Uid=user;Pwd=RyQLXenSWQ4NPCEa;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;";
                return "jdbc:sqlserver://steave-sql-test.database.windows.net:1433;database=test;user=user@steave-sql-test;password=RyQLXenSWQ4NPCEa;encrypt=true;trustServerCertificate=false;hostNameInCertificate=*.database.windows.net;loginTimeout=30;";
                return $"account={Locator}.{Region};user={User};password={Password};db={Database}";
            }
        }
    }
}
