using System;
using MathWorks.MATLAB.Runtime;
using MathWorks.MATLAB.Types;
using MathWorks.MATLAB.Exceptions;
using QuixStreams.Streaming;
using QuixStreams.Streaming.Models;

namespace Service
{
    public class Program
    {
        static void Main()
        {
            dynamic matlab = MATLABRuntime.StartMATLAB("quixmatlab.ctf");

            var client = new QuixStreamingClient();
            using var producer = client.GetTopicProducer(Environment.GetEnvironmentVariable("output"));
            using var consumer = client.GetTopicConsumer(Environment.GetEnvironmentVariable("input"));
            consumer.OnStreamReceived += (_, stream) =>
            {
                Console.WriteLine($"New stream received: {stream.StreamId}");
                stream.Timeseries.OnDataReceived += (_, args) =>
                {
                    foreach (var ts in args.Data.Timestamps)
                    {
                        var x = ts.Parameters["x"].NumericValue.Value;
                        var y = ts.Parameters["y"].NumericValue.Value;
                        var v = new[,] { { x }, { y } };
                        double[,] M = matlab.rot(v, Math.PI / 180 * 45);
                        ts.AddValue("x45", M[0, 0]);
                        ts.AddValue("y45", M[1, 0]);
                        Console.WriteLine($"x:{M[0, 0]}, y:{M[1, 0]}");
                    }
                    producer.GetOrCreateStream(stream.StreamId).Timeseries.Publish(args.Data);
                };
            };
            Console.WriteLine("Listening for streams");
            App.Run();
            Console.WriteLine("Exiting");
        }
    }
}
