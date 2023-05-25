using System;
using System.Diagnostics;
using MathWorks.MATLAB.Engine;
using MathWorks.MATLAB.Types;
using MathWorks.MATLAB.Exceptions;
using QuixStreams.Streaming;
using QuixStreams.Streaming.Models;

namespace Service
{
    class Program
    {
        static void Main(string[] args)
        {
            var sw = new Stopwatch();
            sw.Start();
            dynamic matlab = MATLABEngine.StartMATLAB();
            sw.Stop();
            Console.WriteLine($"MATLAB engine started in {sw.ElapsedMilliseconds / 1000.0} seconds");

            var quix = new QuixStreamingClient();
            using var producer = quix.GetTopicProducer(Environment.GetEnvironmentVariable("OUTPUT_TOPIC"));
            using var consumer = quix.GetTopicConsumer(Environment.GetEnvironmentVariable("INPUT_TOPIC"));
            consumer.OnStreamReceived += (_, stream) =>
            {
                Console.WriteLine($"New stream received: {stream.StreamId}");
                stream.Timeseries.OnDataReceived += (_, args) =>
                {
                    foreach (var ts in args.Data.Timestamps)
                    {
                        var tin = new double[] { ts.TimestampMilliseconds / 1000.0 };
                        var din = new double[] { ts.Parameters["throttle_angle"].NumericValue.Value };
                    sim:
                        double rv;
                        try
                        {
                            rv = matlab.engine(din, tin);
                        }
                        catch (MATLABNotAvailableException)
                        {
                            sw.Restart();
                            matlab = MATLABEngine.StartMATLAB();
                            sw.Stop();
                            Console.WriteLine($"MATLAB engine restarted in {sw.ElapsedMilliseconds / 1000.0} seconds");
                            goto sim;
                        }
                        ts.AddValue("engine_speed", rv);
                        Console.WriteLine($"throttle angle:{din[0]}, engine speed:{rv}");
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