using System;
using System.Threading;
using System.Threading.Tasks;
using MQTTnet;
using MQTTnet.Client;

namespace Mqtt {
    public class MqttProvider {
        public static async Task<IMqttClient> CreateMqttClient() {
        
            var host = Environment.GetEnvironmentVariable("mqtt_server");
            var port = int.Parse(Environment.GetEnvironmentVariable("mqtt_port"));
            var username = Environment.GetEnvironmentVariable("mqtt_username");
            var password = Environment.GetEnvironmentVariable("mqtt_password");

            var mqttOptions = new MqttClientOptionsBuilder()
                    .WithTcpServer(host, port) // MQTT broker address and port
                    .WithClientId("mqtt_quix") // MQTT client ID
                    .WithCredentials(username, password) // MQTT credentials (if required
                    .WithTls(o => {
                        o.CertificateValidationHandler = _ => true;
                    })
                    .Build();

            var mqttClient = new MqttFactory().CreateMqttClient();

            await mqttClient.ConnectAsync(mqttOptions, CancellationToken.None);

            return mqttClient;
        }

        public static async Task SubscribeAsync(IMqttClient mqttClient, Func<MqttApplicationMessageReceivedEventArgs, Task> func) {
            var mqttFactory = new MqttFactory();

                var topics = Environment.GetEnvironmentVariable("mqtt_topic");
            foreach(var topic in topics.Split(',')) {
                var mqttSubscribeOptions = mqttFactory.CreateSubscribeOptionsBuilder()
                    .WithTopicFilter(
                        f =>
                        {
                            f.WithTopic(topic);
                        })
                    .Build();

                await mqttClient.SubscribeAsync(mqttSubscribeOptions, CancellationToken.None);
            }

            mqttClient.ApplicationMessageReceivedAsync += e =>
            {
                return func.Invoke(e);
            };
        }
    }
}