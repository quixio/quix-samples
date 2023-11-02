using System;
using System.Linq;
using QuixStreams.Streaming;
using QuixStreams.Streaming.Models;

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
            var client = new QuixStreamingClient();
            
            var inputTopicName = Environment.GetEnvironmentVariable("input");
            var outputTopicName = Environment.GetEnvironmentVariable("output");
            
            using var outputTopic = client.GetTopicProducer(outputTopicName);
            using var inputTopic = client.GetTopicConsumer(inputTopicName);
            
            // Hook up events before initiating read to avoid losing out on any data
            inputTopic.OnStreamReceived += (s, streamReader) =>
            {
                var streamWriter = outputTopic.CreateStream();

                Console.WriteLine($"New stream read: {streamReader.StreamId}");
                
                // Various settings for the buffer.
                var bufferConfiguration = new TimeseriesBufferConfiguration
                {
                    TimeSpanInMilliseconds = 100,
                };
                
                var buffer = streamReader.Timeseries.CreateBuffer(bufferConfiguration);

                buffer.OnDataReleased += (s, data) =>
                {
                    var outputData = new TimeseriesData();
                    
                    // We calculate mean value for each second of data to effectively down-sample source topic to 1Hz.
                    outputData.AddTimestamp(data.Data.Timestamps.First().Timestamp)
                        .AddValue("ParameterA 10Hz", data.Data.Timestamps.Average(s => s.Parameters["ParameterA"].NumericValue.GetValueOrDefault()))
                        .AddValue("ParameterA source frequency", data.Data.Timestamps.Count);

                    // Cloning data
                    //var outData = new ParameterData(data);

                    // Send using writer buffer
                    streamWriter.Timeseries.Buffer.Publish(outputData);


                    // Send without using writer buffer
                    //streamWriter.Parameters.Write(data);
                };

                // We pass input events to output without change.
                streamReader.Events.OnDataReceived += (s, data) =>
                {
                    streamWriter.Events.Publish(data.Data);
                };
                
                // Metadata manipulation. We suffix down-sampled to stream name and set parent stream reference.
                streamReader.Properties.OnChanged += (s, data) =>
                {
                    streamWriter.Properties.Name = streamReader.Properties.Name + " 10Hz";
                    streamWriter.Properties.Parents.Add(streamReader.StreamId);
                };
                
                // We set source parameter value range.
                streamReader.Timeseries.OnDefinitionsChanged += (s, data) => 
                {
                    var parameterA = streamReader.Timeseries.Definitions.FirstOrDefault(f => f.Id == "ParameterA");

                    if (parameterA != null)
                    {
                        streamWriter.Timeseries
                            .AddDefinition("ParameterA 10Hz")
                            .SetRange(parameterA.MinimumValue.GetValueOrDefault(), parameterA.MaximumValue.GetValueOrDefault());
                    }
                };

                // We close output stream when input stream is closed.
                streamReader.OnStreamClosed += (reader, data) =>
                {
                    streamWriter.Close(data.EndType);
                    Console.WriteLine($"Stream {data.Stream.StreamId} is closed.");
                };
            };
                
            Console.WriteLine("Listening for streams");
            
            // Wait for CTRL-C
            App.Run();
            
            Console.WriteLine("Exiting");
        }
    }
}
