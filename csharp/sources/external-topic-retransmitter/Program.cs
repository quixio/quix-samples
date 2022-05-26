using System;
using Quix.Sdk.Process.Kafka;
using Quix.Sdk.Streaming;

namespace Retransmitter
{
    class Program
    {
        /// <summary>
        /// The service entry point
        /// </summary>
        static void Main(string[] args)
        {
            GetConfiguration(out var sourceWorkspaceSdkToken,
                out var sourceTopicIdOrName,
                out var consumerGroup,
                out var autoOffsetReset,
                out var outputTopic);
            
            var sourceClient = new QuixStreamingClient(sourceWorkspaceSdkToken, false);
            var sourceTopic = sourceClient.OpenRawInputTopic(sourceTopicIdOrName, consumerGroup, autoOffsetReset);

            var targetClient = new QuixStreamingClient(); // reading SDK token from environment variables
            var targetTopic = targetClient.OpenRawOutputTopic(outputTopic);

            long packageRead = 0;
            DateTime nextPrint = DateTime.UtcNow.AddSeconds(5);

            sourceTopic.OnErrorOccurred += (sender, exception) =>
            {
                Console.WriteLine(exception);
            };

            sourceTopic.OnMessageRead += message =>
            {
                packageRead++;
                if (DateTime.UtcNow > nextPrint)
                {
                    nextPrint = DateTime.UtcNow.AddSeconds(10);
                    Console.WriteLine($"Total packages read: {packageRead}");
                }
                targetTopic.Write(message);
            };
            
            App.Run(beforeShutdown: () =>
            {
                Console.WriteLine("Shutting down.");
            });
            Console.WriteLine("Exiting.");
        }

        private static void GetConfiguration(
            out string sourceWorkspaceSdkToken,
            out string sourceTopic,
            out string consumerGroup,
            out AutoOffsetReset sourceOffset,
            out string outputTopic)
        {
            sourceWorkspaceSdkToken = Environment.GetEnvironmentVariable("Source__Workspace__SdkToken");
            if (string.IsNullOrWhiteSpace(sourceWorkspaceSdkToken)) throw new ArgumentException("Source__Workspace__SdkToken must be set");
            Console.WriteLine("Source__Workspace__SdkToken: [present]");
            
            sourceTopic = Environment.GetEnvironmentVariable("Source__Workspace__Topic");
            if (string.IsNullOrWhiteSpace(sourceTopic)) throw new ArgumentException("Source__Workspace__Topic must be set");
            Console.WriteLine($"Source__Workspace__Topic: {sourceTopic}");
            
            var sourceUseConsumerGroup = Environment.GetEnvironmentVariable("Source__UseConsumerGroup") ?? "false";
            if (!bool.TryParse(sourceUseConsumerGroup, out var useConsumerGroup)) useConsumerGroup = false;
            Console.WriteLine($"Source__UseConsumerGroup: {useConsumerGroup}");
            if (useConsumerGroup)
            {
                consumerGroup = Environment.GetEnvironmentVariable("Source__ConsumerGroup") ??
                                Environment.GetEnvironmentVariable("Quix__Deployment__Id") ?? "false";
                Console.WriteLine($"Consumer group: {consumerGroup}");
            }
            else consumerGroup = null;
            
            var sourceOffsetStr = Environment.GetEnvironmentVariable("Source__Offset") ?? "latest";
            if (!Enum.TryParse(sourceOffsetStr, true, out sourceOffset) || sourceOffset == AutoOffsetReset.Error)
            {
                throw new ArgumentException("Source__Offset must be 'latest' or 'earliest'");
            }
            Console.WriteLine($"Source__Offset: {sourceOffsetStr}");
            
            outputTopic = Environment.GetEnvironmentVariable("Output__Topic");
            if (string.IsNullOrWhiteSpace(outputTopic)) throw new ArgumentException("Output__Topic must be set");
            Console.WriteLine($"OutputTopic: {outputTopic}");
        }
    }
}