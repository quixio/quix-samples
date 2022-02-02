using System;
using System.IO;
using System.Linq;
using Microsoft.Extensions.Configuration;
using Quix.Sdk.Streaming;
using Quix.Sdk.Streaming.Models;

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
            var configuration = GetConfiguration();

            // Create a client which holds generic details for creating input and output topics
            var client = new QuixStreamingClient();

            // Create an output topic using the client's configuration
            using var inputTopic = client.OpenInputTopic(configuration.Topic, "complete-example"); // consumer group is optional, if not provided defaults to POD_NAMESPACE environment variable or a default one if that is not set
            
            // Hook up events before initiating read to avoid losing out on any data
            inputTopic.OnStreamReceived += OnStreamReceivedHandler; 

            // Hook up to termination signal (for docker image) and CTRL-C and open streams
            App.Run();
        }

        /// <summary>
        /// Invoked when new stream is picked up from the topic
        /// </summary>
        /// <param name="sender">Streaming client raising the event we're handling</param>
        /// <param name="streamReader">The stream reader for the newly picked up stream</param>
        private static void OnStreamReceivedHandler(object sender, IStreamReader streamReader)
        {
            // Subscribe to the events of the stream reader
            Console.WriteLine($"New stream read: {streamReader.StreamId}");
            streamReader.Properties.OnChanged += () =>
            {
                Console.WriteLine($"Stream properties for stream {streamReader.StreamId}:");
                Console.WriteLine($"  Location: {streamReader.Properties.Location}");
                Console.WriteLine($"  Time of recording: {streamReader.Properties.TimeOfRecording}");
                Console.WriteLine($"  Name: {streamReader.Properties.Name}");
                // Note: There are additional properties available, please feel free to explore the types
            };

            streamReader.Parameters.OnDefinitionsChanged += () =>
            {
                Console.WriteLine($"Parameter definitions changed for stream {streamReader.StreamId}");
                // The parameter definitions provide additional context for the parameters, like their human friendly display name, min/max, their location among other
                // var definitions = streamReader.Parameters.Definitions;
                // var definition = definitions[0];
                // definition.Description
            };

            // create a read buffer which will give the parameters received for the stream 
            // in 100 ms batches, or if no data is read for 100 ms, gives whatever it has
            var buffer = streamReader.Parameters.CreateBuffer();
            buffer.TimeSpanInMilliseconds = 100;
            buffer.BufferTimeout = 100;
            // Note: If you wish to get values as they are read, just set all buffer properties to null (or not set them at all, as that is default)
            buffer.OnRead += (data) =>
            {
                // note: sr and streamReader are the same. sr is provided in case your handler is created where streamReader is not available
                Console.WriteLine($"Parameter data read for stream {streamReader.StreamId} containing {GetSampleCount(data)} values.");
                foreach (var timestamp in data.Timestamps)
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

            streamReader.Events.OnDefinitionsChanged += () =>
            {
                Console.WriteLine($"Event definitions changed for stream {streamReader.StreamId}");
                // The event definitions provide additional context for the parameters, like their human friendly display name, description, severity, their location among other
                // var definitions = streamReader.Events.Definitions;
                // var definition = definitions[0];
                // definition.Description
            };
            
            streamReader.Events.OnRead += (data) =>
            {
                // Because events are treated in a different manner to parameters, there is no buffering capability for them. They're immediately given when read
                Console.WriteLine($"Event read for stream {streamReader.StreamId}, Event Id: {data.Id}");
            };

            streamReader.OnStreamClosed += (sr, endType) =>
            {
                // note: sr and streamReader are the same. sr is provided in case your handler is created where streamReader is not available
                Console.WriteLine($"Stream {sr.StreamId} closed with '{endType}'");
                // the stream closed event occurs when the sending side closes the stream. No more data is to be expected in this case, but the stream may still be reopened by sender if they chose to
            };
        }


        /// <summary>
        /// Gets steaming configuration from app settings
        /// </summary>
        static StreamingConfiguration GetConfiguration()
        {
            var builder = new ConfigurationBuilder();
            builder.SetBasePath(Directory.GetCurrentDirectory());
            builder.AddJsonFile("appsettings.json");
            var config = builder.Build();
            var configuration = new Configuration();
            config.Bind(configuration);
            return configuration.Streaming;
        }

        /// <summary>
        /// Returns the number of samples found in <see cref="ParameterData"/> 
        /// </summary>
        static int GetSampleCount(ParameterData data)
        {
            return data.Timestamps.Sum(x => x.Parameters.Count);
        }
    }
}