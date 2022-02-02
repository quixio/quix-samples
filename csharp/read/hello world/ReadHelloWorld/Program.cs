using System;
using System.Linq;
using Quix.Sdk.Streaming;
using Quix.Sdk.Streaming.Models;

namespace ReadHelloWorld
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
            
            // Hook up events before initiating read to avoid losing out on any data
            inputTopic.OnStreamReceived += (s, streamReader) =>
            {
                Console.WriteLine($"New stream read: {streamReader.StreamId}");
                
                var bufferConfiguration = new ParametersBufferConfiguration
                {
                    TimeSpanInMilliseconds = 1000,
                };
                
                var buffer = streamReader.Parameters.CreateBuffer(bufferConfiguration);

                buffer.OnRead += parameterData =>
                {
                    Console.WriteLine(
                        $"ParameterA - {parameterData.Timestamps[0].Timestamp}: {parameterData.Timestamps.Average(a => a.Parameters["ParameterA"].NumericValue)}");
                };
            };


            Console.WriteLine("Listening for streams");
            
            // Hook up to termination signal (for docker image) and CTRL-C and open streams
            App.Run();

            Console.WriteLine("Exiting");
        }
    }
}
