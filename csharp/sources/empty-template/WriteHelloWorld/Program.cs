using System;
using System.Threading;

namespace WriteHelloWorld
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

            var outputTopicName = Environment.GetEnvironmentVariable("output");
            
            using var outputTopic = client.OpenOutputTopic(outputTopicName);
            
            Console.WriteLine("Creating stream");
            var stream = outputTopic.CreateStream();

            stream.Properties.Name = "Hello World stream";
           
            stream.Parameters
                .AddDefinition("ParameterA")
                .SetRange(-1.2, 1.2);
           
            Console.WriteLine("Sending values for 30 seconds");
            for (var index = 0; index < 3000; index++)
            {
                stream.Parameters.Buffer
                    .AddTimestamp(DateTime.UtcNow)
                    .AddValue("ParameterA", Math.Sin(index/200.0) + Math.Sin(index) / 5.0)
                    .Write(); 
                    
                Thread.Sleep(10);
            }
            
            Console.WriteLine("Closing stream");
            stream.Close();
            Console.WriteLine("Done!");
        }
    }
}
