namespace Service
{
    /// <summary>
    /// The is configuration mapping to appsettings.json
    /// </summary>
    public class Configuration
    {
        public string Topic { get; set; }

        public AwairConfiguration Awair { get; set; }
    }
    
    /// <summary>
    /// The security configuration used to connect to Kafka
    /// </summary>
    public class SecurityConfiguration
    {
        /// <summary>
        /// Folder/file that contains the certificate authority certificate(s) to validate the ssl connection.
        /// </summary>
        public string CACertificatePath { get; set; }
        
        /// <summary>
        /// SASL username
        /// </summary>
        public string Username { get; set; }
        
        /// <summary>
        /// SASL password
        /// </summary>
        public string Password { get; set; }
    }

    /// <summary>
    /// The kafka broker configuration
    /// </summary>
    public class BrokerConfiguration
    {
        /// <summary>
        /// The kafka broker address
        /// </summary>
        public string Address { get; set; }
        
        /// <summary>
        /// The kafka security configuration
        /// </summary>
        public SecurityConfiguration Security { get; set; }
    }

    public class AwairConfiguration
    {
        public string Token { get; set; }
    }
}