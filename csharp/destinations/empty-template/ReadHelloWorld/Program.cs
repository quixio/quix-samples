// Create a client which holds generic details for creating input and output topics
using QuixStreams.Streaming;
using QuixStreams.Streaming.Models;

var client = new QuixStreamingClient();

var topic = Environment.GetEnvironmentVariable("input");
            
using var consumer = client.GetTopicConsumer(topic);
            
// Hook up events before initiating read to avoid losing out on any data
consumer.OnStreamReceived += (s, stream) =>
{
    Console.WriteLine($"New stream received: {stream.StreamId}");
                
    var bufferConfiguration = new TimeseriesBufferConfiguration
    {
        TimeSpanInMilliseconds = 1000,
    };
                
    var buffer = stream.Timeseries.CreateBuffer(bufferConfiguration);

    buffer.OnDataReleased += (sender, args) => {
        Console.WriteLine($"Timestamp: {args.Data.Timestamps[0].Timestamp} has {args.Data.Timestamps[0].Parameters.Count} parameters");
    };
};

Console.WriteLine("Listening for streams");

// Handle termination signals, open streams, and graceful shutdown
App.Run();

Console.WriteLine("Exiting");