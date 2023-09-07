using System;
using System.Linq;
using QuixStreams.Streaming;
using QuixStreams.Streaming.Models;

namespace ReadCompleteExample
{
    class Program
    {
        /// <summary>
        /// Main will be invoked when you run the application
        /// </summary>
        /// <param name="args">Command line arguments (not used)</param>
        static void Main(string[] args)
        {           
            // Create a client which holds generic details for creating input and output topics
            var client = new QuixStreamingClient();

            var consumerTopicName = Environment.GetEnvironmentVariable("input");

            // Create an output topic using the client's configuration
            using var consumer = client.GetTopicConsumer(consumerTopicName, "complete-example"); // consumer group is optional, if not provided defaults to POD_NAMESPACE environment variable or a default one if that is not set

            // Hook up events before initiating read to avoid losing out on any data
            consumer.OnStreamReceived += OnStreamReceivedHandler; 

            // Hook up to termination signal (for docker image) and CTRL-C and open streams
            App.Run();
        }

        /// <summary>
        /// Invoked when new stream is picked up from the topic
        /// </summary>
        /// <param name="sender">Streaming client raising the event we're handling</param>
        /// <param name="streamConsumer">The stream consumer for the newly picked up stream</param>
        private static void OnStreamReceivedHandler(object sender, IStreamConsumer streamConsumer)
        {
            // Subscribe to the events of the stream reader
            Console.WriteLine($"New stream read: {streamConsumer.StreamId}");
            streamConsumer.Properties.OnChanged += (s, data) =>
            {
                Console.WriteLine($"Stream properties for stream {data.Stream.StreamId}:");
                Console.WriteLine($"  Location: {data.Stream.Properties.Location}");
                Console.WriteLine($"  Time of recording: {data.Stream.Properties.TimeOfRecording}");
                Console.WriteLine($"  Name: {data.Stream.Properties.Name}");
                // Note: There are additional properties available, please feel free to explore the types
            };

            streamConsumer.Timeseries.OnDefinitionsChanged += (s, data) =>
            {
                Console.WriteLine($"Parameter definitions changed for stream {data.Stream.StreamId}");
                // The parameter definitions provide additional context for the parameters, like their human friendly display name, min/max, their location among other
                // var definitions = streamConsumer.Parameters.Definitions;
                // var definition = definitions[0];
                // definition.Description
            };

            // create a read buffer which will give the parameters received for the stream 
            // in 100 ms batches, or if no data is read for 100 ms, gives whatever it has
            var buffer = streamConsumer.Timeseries.CreateBuffer();
            buffer.TimeSpanInMilliseconds = 100;
            buffer.BufferTimeout = 100;
            // Note: If you wish to get values as they are read, just set all buffer properties to null (or not set them at all, as that is default)
            buffer.OnDataReleased += (s, data) =>
            {
                // note: sr and streamConsumer are the same. sr is provided in case your handler is created where streamConsumer is not available
                Console.WriteLine($"Parameter data read for stream {streamConsumer.StreamId} containing {GetSampleCount(data.Data)} values.");
                foreach (var timestamp in data.Data.Timestamps)
                {
                    //parameters are accessible as a dictionary of [ParameterId to ParameterValue] at  timestamp.Parameters
                    var parameter = timestamp.Parameters.First();
                    var parameterId = parameter.Key;
                    var value = parameter.Value;
                    // value.Type // gives the type of the parameter (numeric, string)
                    // value.Value // gives the underlying value, whether it is numeric or string
                    // value.NumericValue // gives the underlying value if it os type numeric
                    // value.StringValue // gives the underlying value if it os type string
                    
                    // tags are applied for the entire timestamp, so any value found in this timestamp.Parameters are tagged as such
                    var tagAbcd = timestamp.Tags["abcd"]; // in case the tag doesn't exist, null is returned instead of exception

                }
                
                // data.NumericValues, data.StringValues, data.TagValues are dictionaries, where the key is the parameter id, and the value is an array of double (NumericValues) or string (StringValues, TagValues)
                // The timestamps and the values are linked by index. Example: data.Timestamps[10] links to data.NumericValues.First().Value[10]
                // Explore the properties of the types to gain more insight into what else they contain
            };

            streamConsumer.Events.OnDefinitionsChanged += (s, data) =>
            {
                Console.WriteLine($"Event definitions changed for stream {streamConsumer.StreamId}");
                // The event definitions provide additional context for the parameters, like their human friendly display name, description, severity, their location among other
                // var definitions = streamConsumer.Events.Definitions;
                // var definition = definitions[0];
                // definition.Description
            };
            
            streamConsumer.Events.OnDataReceived += (s, data) =>
            {
                // Because events are treated in a different manner to parameters, there is no buffering capability for them. They're immediately given when read
                Console.WriteLine($"Event read for stream {streamConsumer.StreamId}, Event Id: {data.Data.Id}");
            };

            streamConsumer.OnStreamClosed += (s, data) =>
            {
                // note: sr and streamConsumer are the same. sr is provided in case your handler is created where streamConsumer is not available
                Console.WriteLine($"Stream {data.Stream.StreamId} closed with '{data.EndType}'");
                // the stream closed event occurs when the sending side closes the stream. No more data is to be expected in this case, but the stream may still be reopened by sender if they chose to
            };
        }

        /// <summary>
        /// Returns the number of samples found in <see cref="ParameterData"/> 
        /// </summary>
        static int GetSampleCount(TimeseriesData data)
        {
            return data.Timestamps.Sum(x => x.Parameters.Count);
        }
    }
}