using System;
using IO.Ably;
using QuixStreams.Streaming;
using QuixStreams.Streaming.Models;

namespace AblyHubSource
{
    class Program
    {
        /// <summary>
        /// Main will be invoked when you run the application
        /// </summary>
        static void Main()
        {
            // Supply your own Ably Token or the Token of an Ably Hub data source
            var ably = new AblyRealtime(Environment.GetEnvironmentVariable("AblyToken"));
            
            // Supply your own Ably Channel Name or one from an Ably Hub data source
            var chanName = Environment.GetEnvironmentVariable("AblyChannel");
            var channel = ably.Channels.Get(chanName);
            
            // Create a client which holds generic details for creating topic producers and consumers
            var client = new QuixStreamingClient();
            
            var outputTopicName = Environment.GetEnvironmentVariable("output");
            
            using var topicProducer = client.GetTopicProducer(outputTopicName);
            
            Console.WriteLine("Creating stream");
            var stream = topicProducer.CreateStream(Environment.GetEnvironmentVariable("StreamId"));
            
            channel.Subscribe(message => {
                Console.WriteLine($"Message received: {message.Data}");

                // Messages received from Ably will be written to a Quix Event
                var ed = new EventData(message.Name, DateTime.UtcNow, message.Data.ToString());
                stream.Events.Publish(ed);
            });

            Console.WriteLine("Listening for data from Ably");
            
            // Hook up to termination signal (for docker image) and CTRL-C and open streams
            App.Run();
            
            Console.WriteLine("Closing stream");
            stream.Close();
            Console.WriteLine("Done!");
            
            Console.WriteLine("Exiting");
        }
    }
}