using Microsoft.Extensions.Configuration;
using System.IO;

namespace CarDataGeneratorConnector
{
    /// <summary>
    /// The is the configuration mapping the environment variables injected by Quix Portal
    /// </summary>
    public class ConnectorConfiguration
    {
        public ConnectorConfiguration()
        {
            var builder = new ConfigurationBuilder()
                .SetBasePath(Directory.GetCurrentDirectory())
                .AddJsonFile("appsettings.json")
                .AddEnvironmentVariables();

            //var configuration = new AppConfiguration();
            var config = builder.Build();
            config.Bind(this);
        }
    }
}