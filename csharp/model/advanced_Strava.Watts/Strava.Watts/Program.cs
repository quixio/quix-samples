using System;
using Quix.Sdk.Process.Models;
using Quix.Sdk.Streaming;
using Quix.Sdk.Streaming.Models;
using ParameterData = Quix.Sdk.Streaming.Models.ParameterData;

namespace Strava.Watts
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
            
           var wattOutputModel = new WattModel(107.0);
            
            // Hook up events before initiating read to avoid losing out on any data
            inputTopic.OnStreamReceived += (s, streamReader) =>
            {
                var streamWriter = outputTopic.CreateStream();

                Console.WriteLine($"New stream read: {streamReader.StreamId}");

                streamWriter.Parameters.DefaultLocation = "Models/Watt Output";
                    
                streamWriter.Parameters
                    .AddDefinition(
                        "gravity",
                        "Gravity", 
                        "You are cycling uphill: gravity is working against you")
                    .SetUnit("N");
                    
                streamWriter.Parameters
                    .AddDefinition("aerodynamicDrag", 
                        "Aerodynamic drag",
                        "As you cycle through the air, your bike and body need to push the air around you, similar to how a snowplow pushes snow out of the way.")
                    .SetUnit("N");
                    
                streamWriter.Parameters
                    .AddDefinition(
                        "rollingResistence",
                        "Rolling resistence",
                        "Friction between your tires and the road surface slows you down.")
                    .SetUnit("N");

                streamWriter.Parameters
                    .AddDefinition(
                        "wattOutput",
                        "Watt output",
                        "Total watt output to achieve input speed.")
                    .SetUnit("Watt");
                
                // Various settings for the buffer.
                var bufferConfiguration = new ParametersBufferConfiguration
                {
                    TimeSpanInMilliseconds = 100,
                };
                
                var buffer = streamReader.Parameters.CreateBuffer(bufferConfiguration);

                buffer.OnRead += (data) =>
                {
                    var outputData = new ParameterData();

                    foreach (var parameterDataTimestamp in data.Timestamps)
                    {
                        var speed = parameterDataTimestamp.Parameters["speed"].NumericValue.GetValueOrDefault();
                        var grade = parameterDataTimestamp.Parameters["grade"].NumericValue.GetValueOrDefault();
                        
                        streamWriter.Events.AddDefinition("maxheartrate", "Max heartrate", "Moment when max heartrate was reached.")
                            .SetLevel(EventLevel.Warning);
                        
                        var wattOutput = wattOutputModel.CalculateWattOutput(speed / 3.6, grade);
                        outputData.AddTimestamp(parameterDataTimestamp.Timestamp)
                            .AddValue("gravity", wattOutput.Gravity)
                            .AddValue("aerodynamicDrag", wattOutput.AerodynamicDrag)
                            .AddValue("rollingResistence", wattOutput.RollingResistence)
                            .AddValue("wattOutput", wattOutput.WattOutput)
                            .AddValue("distance", parameterDataTimestamp.Parameters["distance"].NumericValue.GetValueOrDefault())
                            .AddTags(parameterDataTimestamp.Tags);
                        
                        streamWriter.Parameters.Buffer.Write(outputData);
                    }
                };
                // Metadata manipulation. We suffix downsampled to stream name and set parent stream reference.
                streamReader.Properties.OnChanged += () =>
                {
                    streamWriter.Properties.Name = streamReader.Properties.Name + " watts";
                    streamWriter.Properties.Parents.Add(streamReader.StreamId);
                    
                    streamWriter.Parameters.Flush();
                };

                // We close output stream when input stream is closed.
                streamReader.OnStreamClosed += (reader, type) =>
                {
                    streamWriter.Close(type);
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