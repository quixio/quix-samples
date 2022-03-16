namespace Quix.Redshift.Infrastructure.TimeSeries.Models
{
    /// <summary>
    /// Redshift database connection configuration.
    /// </summary>
    public class RedshiftConnectionConfiguration
    {
        public string AccessKeyId { get; set; }
        public string SecretAccessKey { get; set; }

        /// <summary>
        /// The system name of the region
        /// Example: "us-east-1" 
        /// </summary>
        public string Region { get; set; }

        public string DatabaseName { get; set; }
    }
}
