using System;
using Quix.Sdk.Streaming.Models;
using Quix.Sdk.Process.Models;
using Quix.Sdk.Streaming;

namespace Strava.Events
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
                var streamWriter = outputTopic.CreateStream(streamReader.StreamId + "_events");

                Console.WriteLine($"New stream read: {streamReader.StreamId}");
                
                // Various settings for the buffer.
                var bufferConfiguration = new ParametersBufferConfiguration
                {
                    TimeSpanInMilliseconds = 100,
                };

                streamWriter.Events.DefaultLocation = "Models/Events";
                streamWriter.Events.AddDefinition("maxspeed", "Max speed", "Moment when max speed was reached.")
                    .SetLevel(EventLevel.Information);
                
                streamWriter.Events.AddDefinition("maxaltitude", "Max altitude", "Moment when max altitude was reached.")
                    .SetLevel(EventLevel.Information);
                
                streamWriter.Events.AddDefinition("maxheartrate", "Max heart rate", "Moment when max heart rate was reached.")
                    .SetLevel(EventLevel.Warning);
                
                var buffer = streamReader.Parameters.CreateBuffer(bufferConfiguration);

                var maxSpeed = new Tuple<DateTime, double>(new DateTime(0), 0);
                var maxAltitude = new Tuple<DateTime, double>(new DateTime(0), 0);
                var maxHeartRate = new Tuple<DateTime, double>(new DateTime(0), 0);
                
                buffer.OnRead += (data) =>
                {
                    foreach (var parameterDataTimestamp in data.Timestamps)
                    {
                        var speed = parameterDataTimestamp.Parameters["speed"].NumericValue.GetValueOrDefault();
                        if (speed > maxSpeed.Item2)
                        {
                            maxSpeed = new Tuple<DateTime, double>(parameterDataTimestamp.Timestamp, speed);
                        }
                        
                        var altitude = parameterDataTimestamp.Parameters["altitude"].NumericValue.GetValueOrDefault();
                        if (altitude > maxAltitude.Item2)
                        {
                            maxAltitude = new Tuple<DateTime, double>(parameterDataTimestamp.Timestamp, altitude);
                        }
                        
                        var heartrate = parameterDataTimestamp.Parameters["heartrate"].NumericValue.GetValueOrDefault();
                        if (heartrate > maxHeartRate.Item2)
                        {
                            maxHeartRate = new Tuple<DateTime, double>(parameterDataTimestamp.Timestamp, heartrate);
                        }
                    }
                };
                
                // Metadata manipulation. We suffix downsampled to stream name and set parent stream reference.
                streamReader.Properties.OnChanged += () =>
                {
                    streamWriter.Properties.Name = streamReader.Properties.Name + " events";
                    streamWriter.Properties.Parents.Add(streamReader.StreamId);
                    
                    streamWriter.Parameters.Flush();
                };

                // We close output stream when input stream is closed.
                streamReader.OnStreamClosed += (reader, type) =>
                {
                    if (maxSpeed.Item1.Ticks > 0)
                    {
                        streamWriter.Events
                            .AddTimestamp(maxSpeed.Item1)
                            .AddValue("maxspeed", $"Max speed: {maxSpeed.Item2} kmh.")
                            .Write();
                    }
                    
                    if (maxAltitude.Item1.Ticks > 0)
                    {
                        streamWriter.Events
                            .AddTimestamp(maxAltitude.Item1)
                            .AddValue("maxaltitude", $"Max altitude: {maxAltitude.Item2} metres above see level.")
                            .Write();
                    }
                    
                    if (maxHeartRate.Item1.Ticks > 0)
                    {
                        streamWriter.Events
                            .AddTimestamp(maxHeartRate.Item1)
                            .AddValue("maxheartrate", $"Max heartrate: {maxHeartRate.Item2} BPM.")
                            .Write();
                    }
                    
                    streamWriter.Close(type);
                    Console.WriteLine($"Stream {reader.StreamId} is closed.");
                };
            };
                
            Console.WriteLine("Listening for streams");
            
            // Wait for CTRL-C
            App.Run();
            
            Console.WriteLine("Exiting");
        }
    }
}
