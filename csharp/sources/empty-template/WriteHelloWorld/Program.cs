// Create a client that holds generic details for creating input and output topics
var client = new QuixStreams.Streaming.QuixStreamingClient();

var outputTopicName = Environment.GetEnvironmentVariable("output");
            
using var outputTopic = client.GetTopicProducer(outputTopicName);
            
Console.WriteLine("Creating stream");
var stream = outputTopic.CreateStream();

stream.Properties.Name = "Hello World stream";
           
stream.Timeseries
    .AddDefinition("ParameterA")
    .SetRange(-1.2, 1.2);
           
Console.WriteLine("Sending values for 30 seconds");
for (var index = 0; index < 3000; index++)
{
    stream.Timeseries.Buffer
        .AddTimestamp(DateTime.UtcNow)
        .AddValue("ParameterA", Math.Sin(index/200.0) + Math.Sin(index) / 5.0)
        .Publish(); 
                    
    Thread.Sleep(10);
}
            
Console.WriteLine("Closing stream");
stream.Close();
Console.WriteLine("Done!");