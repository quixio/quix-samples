namespace ReadCompleteExample
{
    /// <summary>
    /// The is configuration mapping to appsettings.json
    /// </summary>
    public class Configuration
    {
        public StreamingConfiguration Streaming { get; set; }
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

    /// <summary>
    /// The streaming configuration to describe which kafka to use and what topic
    /// </summary>
    public class StreamingConfiguration
    {
        /// <summary>
        /// The topic to connect to
        /// </summary>
        public string Topic { get; set; }
        
        /// <summary>
        /// The kafka broker configuration
        /// </summary>
        public BrokerConfiguration Broker { get; set; }
    }
}