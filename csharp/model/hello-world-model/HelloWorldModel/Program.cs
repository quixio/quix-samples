using System;
using System.Linq;
using System.Threading;
using Quix.Sdk.Streaming.Configuration;
using Quix.Sdk.Streaming.Models;

namespace HelloWorldModel
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
                
                // Various settings for the buffer.
                var bufferConfiguration = new ParametersBufferConfiguration
                {
                    TimeSpanInMilliseconds = 100,
                };
                
                var buffer = streamReader.Parameters.CreateBuffer(bufferConfiguration);

                buffer.OnRead += (data) =>
                {
                    var outputData = new ParameterData();
                    
                    // We calculate mean value for each second of data to effectively down-sample source topic to 1Hz.
                    outputData.AddTimestamp(data.Timestamps.First().Timestamp)
                        .AddValue("ParameterA 10Hz", data.Timestamps.Average(s => s.Parameters["ParameterA"].NumericValue.GetValueOrDefault()))
                        .AddValue("ParameterA source frequency", data.Timestamps.Count);

                    // Cloning data
                    //var outData = new ParameterData(data);

                    // Send using writer buffer
                    streamWriter.Parameters.Buffer.Write(outputData);


                    // Send without using writer buffer
                    //streamWriter.Parameters.Write(data);
                };

                // We pass input events to output without change.
                streamReader.Events.OnRead += (data) =>
                {
                    streamWriter.Events.Write(data);
                };
                
                // Metadata manipulation. We suffix down-sampled to stream name and set parent stream reference.
                streamReader.Properties.OnChanged += () =>
                {
                    streamWriter.Properties.Name = streamReader.Properties.Name + " 10Hz";
                    streamWriter.Properties.Parents.Add(streamReader.StreamId);
                };
                
                // We set source parameter value range.
                streamReader.Parameters.OnDefinitionsChanged += () => 
                {
                    var parameterA = streamReader.Parameters.Definitions.FirstOrDefault(f => f.Id == "ParameterA");

                    if (parameterA != null)
                    {
                        streamWriter.Parameters
                            .AddDefinition("ParameterA 10Hz")
                            .SetRange(parameterA.MinimumValue.GetValueOrDefault(), parameterA.MaximumValue.GetValueOrDefault());
                    }
                };

                // We close output stream when input stream is closed.
                streamReader.OnStreamClosed += (reader, type) =>
                {
                    streamWriter.Close(type);
                    Console.WriteLine($"Stream {reader.StreamId} is closed.");
                };
            };
                
            inputTopic.StartReading(); // initiate read
            Console.WriteLine("Listening for streams");
            
            // Hook up to termination signal (for docker image) and CTRL-C
            var exitEvent = new ManualResetEventSlim();
            Console.CancelKeyPress += (s, e) =>
            {
                e.Cancel = true; // In order to allow the application to cleanly exit instead of terminating it
                exitEvent.Set();
            }; 
            // Wait for CTRL-C
            exitEvent.Wait();
            Console.WriteLine("Exiting");
        }
    }
}
