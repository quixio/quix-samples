using System;
using IO.Ably;
using Newtonsoft.Json;
using Quix.Sdk.Streaming;

namespace AblySink
{
    class Program
    {
        /// <summary>
        /// Main will be invoked when you run the application
        /// </summary>
        static void Main()
        {
            // Create a client which holds generic details for creating input and output topics
            var client = new QuixStreamingClient();
            var inputTopicName = Environment.GetEnvironmentVariable("input");
            
            using var inputTopic = client.OpenInputTopic(inputTopicName);

            var ably = new AblyRealtime(Environment.GetEnvironmentVariable("AblyToken"));
            var chanName = Environment.GetEnvironmentVariable("AblyChannel");
            
            var channel = ably.Channels.Get(chanName);

            var ablyMessageName = Environment.GetEnvironmentVariable("AblyMessageNamePrefix");
            var ablyParameterDataMessageName = $"{ablyMessageName}-parameter-data";
            var ablyEventDataMessageName = $"{ablyMessageName}-event-data";
            
            // Hook up events before initiating read to avoid losing out on any data
            inputTopic.OnStreamReceived += (s, streamReader) =>
            {
                Console.WriteLine($"New stream read: {streamReader.StreamId}");
                
                streamReader.Parameters.OnRead += parameterData =>
                {
                    var payload = JsonConvert.SerializeObject(parameterData);
                    channel.Publish(ablyParameterDataMessageName, payload);
                    
                    Console.WriteLine("Parameter Payload synced to Ably");
                };

                streamReader.Events.OnRead += eventData =>
                {
                    var payload = JsonConvert.SerializeObject(eventData);
                    channel.Publish(ablyEventDataMessageName, payload);
                    
                    Console.WriteLine("Event Payload synced to Ably");
                };
            };

            Console.WriteLine("Listening for streams");
            
            // Hook up to termination signal (for docker image) and CTRL-C and open streams
            App.Run();

            Console.WriteLine("Exiting");
        }
    }
}