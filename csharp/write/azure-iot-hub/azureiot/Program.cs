using System;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Azure.Messaging.EventHubs.Consumer;
using Quix.Sdk.Streaming;

namespace azureIot
{
    class Program
    {
        // Asynchronously create a PartitionReceiver for a partition and then start
        // reading any messages sent from the simulated client.
        private static async Task ReceiveMessagesFromDeviceAsync(CancellationToken cancellationToken)
        {
            var outputTopicName = Environment.GetEnvironmentVariable("output");
            var endpoint = Environment.GetEnvironmentVariable("eventHubsEndpoint");
            var hubName = Environment.GetEnvironmentVariable("eventHubName");
            var sasKeyName = Environment.GetEnvironmentVariable("iotSasKeyName");
            var sasKey = Environment.GetEnvironmentVariable("iotSasKey");

            
            // Create a client factory. Factory helps you create StreamingClient (see below) a little bit easier
            var client = new Quix.Sdk.Streaming.QuixStreamingClient();
            
            // Create a StreamingClient (using the factory) in order to easily create new streams for the above configured topic
            using var outputTopic = client.OpenOutputTopic(outputTopicName);

            // Event Hub-compatible endpoint
            // az iot hub show --query properties.eventHubEndpoints.events.endpoint --name {your IoT Hub name}
            var eventHubsCompatibleEndpoint = endpoint;

            // Event Hub-compatible name
            // az iot hub show --query properties.eventHubEndpoints.events.path --name {your IoT Hub name}
            var eventHubName = hubName;

            // az iot hub policy show --name service --query primaryKey --hub-name {your IoT Hub name}
            var iotHubSasKeyName = sasKeyName;
            var iotHubSasKey = sasKey;

            // If you chose to copy the "Event Hub-compatible endpoint" from the "Built-in endpoints" section
            // of your IoT Hub instance in the Azure portal, you can set the connection string to that value
            // directly and remove the call to "BuildEventHubsConnectionString".
            string connectionString =
                BuildEventHubsConnectionString(eventHubsCompatibleEndpoint, iotHubSasKeyName, iotHubSasKey);

            // Create the consumer using the default consumer group using a direct connection to the service.
            // Information on using the client with a proxy can be found in the README for this quick start, here:
            //   https://github.com/Azure-Samples/azure-iot-samples-csharp/tree/master/iot-hub/Quickstarts/read-d2c-messages/README.md#websocket-and-proxy-support
            //
            await using EventHubConsumerClient consumer =
                new EventHubConsumerClient(EventHubConsumerClient.DefaultConsumerGroupName, connectionString,
                    eventHubName);

            var stream = outputTopic.CreateStream();
            stream.Properties.Name = "Azure Hub data";

            Console.WriteLine("Listening for messages on all partitions");
            while (!cancellationToken.IsCancellationRequested)
            {

                try
                {
                    // Begin reading events for all partitions, starting with the first event in each partition and waiting indefinitely for
                    // events to become available.  Reading can be canceled by breaking out of the loop when an event is processed or by
                    // signaling the cancellation token.
                    //
                    // The "ReadEventsAsync" method on the consumer is a good starting point for consuming events for prototypes
                    // and samples.  For real-world production scenarios, it is strongly recommended that you consider using the
                    // "EventProcessorClient" from the "Azure.Messaging.EventHubs.Processor" package.
                    //
                    // More information on the "EventProcessorClient" and its benefits can be found here:
                    //   https://github.com/Azure/azure-sdk-for-net/blob/master/sdk/eventhub/Azure.Messaging.EventHubs.Processor/README.md
                    //
                    await foreach (PartitionEvent partitionEvent in consumer.ReadEventsAsync(cancellationToken))
                    {
                        foreach (var prop in partitionEvent.Data.Properties)
                        {
                            stream.Properties.Metadata[prop.Key] = prop.Value.ToString();
                        }

                        foreach (var prop in partitionEvent.Data.SystemProperties)
                        {
                            stream.Properties.Metadata[prop.Key] = prop.Value.ToString();
                        }

                        Console.WriteLine("Message received on partition {0}:", partitionEvent.Partition.PartitionId);

                        var data = Encoding.UTF8.GetString(partitionEvent.Data.Body.ToArray());

                        stream.Events
                            .AddTimestamp(partitionEvent.Data.EnqueuedTime.ToUniversalTime().DateTime)
                            .AddValue("message", data)
                            .Write();

                        Console.WriteLine("\t{0}:", data);

                        Console.WriteLine("Application properties (set by device):");
                    }
                }
                catch (TaskCanceledException)
                {
                    // This is expected when the token is signaled; it should not be considered an
                    // error in this scenario.
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex);
                }
            }
        }

        public static async Task Main(string[] args)
        {
            Console.WriteLine("IoT Hub Quickstarts - Read device to cloud messages. Ctrl-C to exit.\n");
            using var cancellationSource = new CancellationTokenSource();
            
            App.Run(beforeShutdown:() =>
            {
                cancellationSource.Cancel();
            });
            
            await ReceiveMessagesFromDeviceAsync(cancellationSource.Token);
        }

        private static string BuildEventHubsConnectionString(string eventHubsEndpoint,
            string iotHubSharedKeyName,
            string iotHubSharedKey) =>
            $"Endpoint={eventHubsEndpoint};SharedAccessKeyName={iotHubSharedKeyName};SharedAccessKey={iotHubSharedKey}";
    }
}