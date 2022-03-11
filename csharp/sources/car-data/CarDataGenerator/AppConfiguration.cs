namespace CarDataGeneratorConnector
{
    /// <summary>
    /// The is configuration mapping the the parameters injected by your connector
    /// </summary>
    public class AppConfiguration : ConnectorConfiguration
    {
        /// <summary>
        /// Data Frequency
        /// </summary>
        public int DataFrequency { get; set; }

        /// <summary>
        /// Topic Name to connect to
        /// </summary>
        public string Topic { get; set; }
    }
}