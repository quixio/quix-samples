using System;
using System.Linq;
using Quix.Sdk.Streaming;
using Quix.Sdk.Streaming.Models;

namespace Strava.HeartrateZones
{
    class Program
    {
        /// <summary>
        /// Main will be invoked when you run the application
        /// </summary>
        static void Main()
        {
            // Create a client which holds generic details for creating input and output topics
            var client = new Quix.Sdk.Streaming.QuixStreamingClient();
            
            var inputTopicName = Environment.GetEnvironmentVariable("input");
            var outputTopicName = Environment.GetEnvironmentVariable("output");

            using var outputTopic = client.OpenOutputTopic(outputTopicName);
            using var inputTopic = client.OpenInputTopic(inputTopicName);

            // Hook up events before initiating read to avoid losing out on any data
            inputTopic.OnStreamReceived += (s, streamReader) =>
            {
                var streamWriter = outputTopic.CreateStream();
                
                Console.WriteLine($"New stream read: {streamReader.StreamId}");

                streamWriter.Parameters.DefaultLocation = "Models/Heartzones";

                // Various settings for the buffer.
                var bufferConfiguration = new ParametersBufferConfiguration
                {
                    TimeSpanInMilliseconds = 100,
                };
                
                var buffer = streamReader.Parameters.CreateBuffer(bufferConfiguration);

                buffer.OnRead += (data) =>
                {
                    var outputData = data.Clone();

                    foreach (var parameterDataTimestamp in outputData.Timestamps.Where(w => w.Parameters["heartrate"].NumericValue.HasValue))
                    {
                        var heartrate = parameterDataTimestamp.Parameters["heartrate"].NumericValue.Value;

                        string zone = "";

                        if (heartrate <= 112) zone = "Endurance";
                        else if (heartrate <= 148) zone = "Moderate";
                        else if (heartrate <= 166) zone = "Tempo";
                        else if (heartrate <= 184) zone = "Threshold";
                        else if (heartrate > 184) zone = "Anaerobic";
                            
                        parameterDataTimestamp.AddTag("heartratezone", zone);
                    }

                    // Send using writer buffer
                    streamWriter.Parameters.Buffer.Write(outputData);
                };

                // Metadata manipulation. We suffix down-sampled to stream name and set parent stream reference.
                streamReader.Properties.OnChanged += () =>
                {
                    streamWriter.Properties.Name = streamReader.Properties.Name + " heartrate zones";
                    streamWriter.Properties.Parents.Add(streamReader.StreamId);
                    
                    streamWriter.Parameters.Flush();
                };
                
                // We close output stream when input stream is closed.
                streamReader.OnStreamClosed += (reader, type) =>
                {
                    streamWriter.Close(type); //close the stream
                    Console.WriteLine($"Stream {reader.StreamId} is closed.");
                };
            };
                
            Console.WriteLine("Listening for streams");
            
            // Hook up to termination signal (for docker image) and CTRL-C
            App.Run();
            
            Console.WriteLine("Exiting");
        }
    }
}