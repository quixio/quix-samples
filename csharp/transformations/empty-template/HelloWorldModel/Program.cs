using QuixStreams.Streaming;
using QuixStreams.Streaming.Models;

// Create a client which holds generic details for creating input and output topics
var client = new QuixStreamingClient();

var inputTopicName = Environment.GetEnvironmentVariable("input");
var outputTopicName = Environment.GetEnvironmentVariable("output");

using var producer = client.GetTopicProducer(outputTopicName);
using var consumer = client.GetTopicConsumer(inputTopicName);

// Hook up events before initiating read to avoid losing out on any data
consumer.OnStreamReceived += (topic, receivedStream) =>
{
    // Set the output stream id to the same as the input stream or change it,
    // if you grouped or merged data with different key.
    var streamWriter = producer.CreateStream(receivedStream.StreamId);

	Console.WriteLine($"New stream read: {receivedStream.StreamId}");
	
	// Various settings for the buffer.
	// Here we will buffer for 100 milliseconds before handling the data
	var bufferConfiguration = new TimeseriesBufferConfiguration
    {
		TimeSpanInMilliseconds = 100,
	};
	
	// create the buffer using the configuration
	var buffer = receivedStream.Timeseries.CreateBuffer(bufferConfiguration);

	buffer.OnDataReleased += (sender, args) =>
	{
		// subscribe to new data that is being received
		// refer to the docs here: https://docs.quix.io/sdk/subscribe.html
        Console.WriteLine($"Timestamp: {args.Data.Timestamps[0].Timestamp} has {args.Data.Timestamps[0].Parameters.Count} parameters");
    
        // Here is where you should add your transformation, run your models or perform 
        // any other data modification.

		foreach (var row in args.Data.Timestamps)
		{
        	var newValue = new Random().Next(500); // generate a random number up to 500

			row.AddValue("NewData", newValue);
		}
		        
		// Send using writer buffer
        streamWriter.Timeseries.Buffer.Publish(args.Data);
    };

	// We pass input events to output without change.
	receivedStream.Events.OnDataReceived += (sender, args) =>
	{
		streamWriter.Events.Publish(args.Data);
	};
	
	// Metadata manipulation. We suffix down-sampled to stream name and set parent stream reference.
	receivedStream.Properties.OnChanged += (sender, args) =>
	{
		streamWriter.Properties.Name = receivedStream.Properties.Name + " 10Hz";
		streamWriter.Properties.Parents.Add(receivedStream.StreamId);
	};
	
	// We set source parameter value range.
	receivedStream.Timeseries.OnDefinitionsChanged += (sender, args) => 
	{
		var parameterA = receivedStream.Timeseries.Definitions.FirstOrDefault(f => f.Id == "ParameterA");

		if (parameterA != null)
		{
			streamWriter.Timeseries
				.AddDefinition("ParameterA 10Hz")
				.SetRange(parameterA.MinimumValue.GetValueOrDefault(), parameterA.MaximumValue.GetValueOrDefault());
		}
	};

	// We close output stream when input stream is closed.
	receivedStream.OnStreamClosed += (reader, args) =>
	{
		streamWriter.Close(args.EndType);
		Console.WriteLine($"Stream {args.Stream.StreamId} is closed.");
	};
};
	
Console.WriteLine("Listening for streams");

// Handle termination signals, open streams, and graceful shutdown
App.Run();

Console.WriteLine("Exiting");
