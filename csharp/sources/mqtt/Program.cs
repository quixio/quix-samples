using System;
using Quix.Sdk.Streaming;
using Quix.Sdk.Streaming.Models;
using System.Threading.Tasks;
using System.Text;

namespace Mqtt
{
    class Program
    {
        /// <summary>
        /// The service entry point
        /// </summary>
        static async Task Main(string[] args)
        {
            var client = new QuixStreamingClient();
            var mqttClient = await MqttProvider.CreateMqttClient();
           
            var outputTopicName = Environment.GetEnvironmentVariable("output");
            using var outputTopic = client.OpenOutputTopic(outputTopicName);
            var streamWriter = outputTopic.CreateStream();
            
            await MqttProvider.SubscribeAsync(mqttClient, async e =>
              {
                  // Parse received MQTT message
                  var payload = Encoding.UTF8.GetString(e.ApplicationMessage.Payload);

                  var ed = new EventData("Measurement", DateTime.UtcNow, payload);
                  streamWriter.Events.Write(ed);
              });

            App.Run(beforeShutdown:() =>
            {
                Console.WriteLine("Shutting down...");
            });
        }
    }
}