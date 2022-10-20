namespace Quix.SqlServer.Infrastructure.TimeSeries.Models
{
    /// <summary>
    /// SqlServer database connection configuration.
    /// </summary>
    public class SqlServerConnectionConfiguration
    {
        public string User { get; set; }
        public string Password { get; set; }
        public string Server { get; set; }
        public string Port { get; set; }
        public string Database { get; set; }
        
        public string ConnectionString
        {
            get
            {
                return
                    $"Server={Server},{Port};Database={Database};Uid={User};Pwd={Password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;MultipleActiveResultSets=True;";
            }
        }
    }
}