using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using QuixStreams.Streaming;
using QuixStreams.Telemetry.Models;
using TimeseriesData = QuixStreams.Streaming.Models.TimeseriesData;

namespace CarDataGeneratorConnector
{
    class Program
    {
        /// <summary>
        /// Main will be invoked when you run the application
        /// </summary>
        /// <param name="args">Command line arguments (not used)</param>
        static void Main(string[] args)
        {
            // Hook up to CTRL-C, so can exit the application
            var cts = new CancellationTokenSource();

            Console.CancelKeyPress += (s, e) =>
            {
                Console.WriteLine("Exiting (SIGINT) ...");
                cts.Cancel();
                e.Cancel = true; // In order to allow the application to cleanly exit instead of terminating it
            };

            AppDomain.CurrentDomain.ProcessExit += (s, e) =>
            {
                Console.WriteLine("Exiting (SIGTERM) ...");
                cts.Cancel();
            };

            try
            {
                var configuration = new AppConfiguration();

                // Checking source parameters
                if (!Enumerable.Range(1, 10000).Contains(configuration.DataFrequency))
                {
                    throw new Exception("DataFrequency should be between 1 and 10000 Hz.");
                }

                // Create a client which holds generic details for creating topic producers and consumers
                var client = new QuixStreamingClient();

                // Create a topic producer using the client's configuration
                using var topicProducer = client.GetTopicProducer(configuration.Topic);
                var stream = topicProducer.CreateStream();

                // Standard log indicating the Connector has started the connection successfully
                Console.WriteLine("CONNECTED!");

                // Generate some data
                GenerateData(stream, configuration.DataFrequency, cts.Token);

                Console.WriteLine("Closing stream");
                stream.Close(StreamEndType.Closed);
            }
            catch (Exception ex)
            {
                Console.WriteLine("ERROR: {0}", ex.Message);
                Environment.ExitCode = -1;
                cts.Token.WaitHandle.WaitOne();
            }
        }

        /// <summary>
        /// Generate data for your stream. The function is a little more complicated to provide at least a bit of realistic data, however the methods used for sending data is still the same as in <see cref="Main"/>
        /// </summary>
        /// <param name="stream">The stream to generate the data to</param>
        /// <param name="ctsToken">Application exit cancellation token</param>
        static void GenerateData(IStreamProducer stream, int dataFrequency, CancellationToken ctsToken)
        {
            var interval = (int)((double)(1 * 1000) / dataFrequency); // calc how many ms should be the interval between samples
            
            // Some local variables to help with our data generation to be a little more realistic. Feel free to ignore them
            var random = new Random();
            var currentGear = 0;
            var speedCaps = new Dictionary<int, double> {{0, 0}, {1, 70}, {2, 90}, {3, 110}, {4, 140}, {5, 170}, {6, 210}};
            var maxGear = speedCaps.Keys.Max();
            var lastGearChange = DateTime.MinValue;
            var dropGearUntil = DateTime.MinValue;
            var currentSpeed = 0D;

            stream.Epoch = DateTime.UtcNow;

            // And now set some optional properties on the stream. All of these can be omitted, but can help greatly in organising the streams
            stream.Properties.Location = "sample/car-data"; // location helps to organize the streams into folder like structure
            stream.Properties.Name = "Stream generated with Car Data Generator"; // the display name of the stream. If not set, the stream id will be used
            stream.Properties.Metadata["Language"] = "C#"; // optional meta data on the stream. Can be any string pair, can be used to provide additional one-time information regarding the stream.
            stream.Properties.Metadata["Sample"] = "WriteStream"; // Updating the value during stream overwrites previous value
            stream.Properties.Metadata["Connector"] = "Car Data Generator"; // Updating the value during stream overwrites previous value

            // While this is entirely optional, the protocol functions without it, lets describe some of the parameters and events present in the stream so consumers can better understand and work with the data                                            
            stream.Timeseries.DefaultLocation = "/car"; // the default location will determine where parameters will be placed if you add them after this line
            stream.Timeseries
                .AddDefinition("car_speed", "Car speed", "Speed of the car") // name (2nd param) and description (3rd param) are optional. The name will default to the parameter id if none provided.
                .SetUnit("kph")
                .SetRange(0, 210);
            stream.Timeseries
                .AddLocation("/car/engine") // optionally you can overwrite the default location by specifying location like this
                .AddDefinition("car_gear", "Gear").SetRange(0, 6)
                .AddDefinition("car_engine_rpm", "Engine RPM"); // the definition builder allows you to set as many parameters at once as you wish 

            stream.Events
                .AddDefinition("car_started", "Car Started", "The car has started") // add a few events also, similarly to parameters
                .AddDefinition("car_stopped", "Car Stopped", "the car has stopped")
                .AddDefinition("gear_changed", "Gear Changed", "The car has changed the gear")
                .SetLevel(EventLevel.Trace); // You can also set severity of an event, there are many options to choose from

            Console.WriteLine($"Streaming data at {dataFrequency}Hz");

            stream.Events.AddTimestamp(DateTime.UtcNow).AddValue("car_started", "Car started!").Publish();
            
            while (!ctsToken.IsCancellationRequested) // exit if CTRL-C is invoked
            {
                var data = new TimeseriesData();
                var timestamp = data.AddTimestamp(DateTime.UtcNow); // not necessary to set builder to a variable, but I wish to have the same timestamp for all values within an iteration
                                                                            // therefore saving it like this.
                if (GetGearValue(out var newGear))
                {
                    currentGear = newGear;
                    lastGearChange = DateTime.UtcNow;
                    timestamp.AddValue("car_gear", newGear); // If you don't have a lot of parameter identifiers and know them ahead of time, might be best to use a constant instead for name
                    Console.WriteLine("GEAR CHANGE: {0}", newGear);

                    stream.Events.AddTimestamp(DateTime.UtcNow).AddValue("gear_changed", $"Gear changed to {newGear}").Publish();
                }

                currentSpeed = GetSpeed();
                var currentRPM = GetRPM();
                timestamp.AddValue("car_speed", currentSpeed);
                timestamp.AddValue("car_engine_rpm", currentRPM);
                stream.Timeseries.Publish(data);
                Console.WriteLine("Speed: {0,20} - Rpm: {1,5}", currentSpeed, currentRPM);

                Thread.Sleep(interval); // sleep the interval
            }
            
            stream.Events.AddTimestamp(DateTime.UtcNow).AddValue("car_stopped", "Car stopped!").Publish();
            
            // some local helper functions kept here to not clutter class too much. Feel free to ignore them
            bool GetGearValue(out int newGearValue)
            {
                newGearValue = 0;
                var minimumGearChangeTime = dropGearUntil > DateTime.UtcNow
                    ? TimeSpan.FromMilliseconds(200)
                    : TimeSpan.FromMilliseconds(500);
                if (lastGearChange + minimumGearChangeTime >= DateTime.UtcNow) return false;
                if (dropGearUntil > DateTime.UtcNow)
                {
                    newGearValue = Math.Max(1, currentGear - 1);
                    return true;
                }
                if (currentGear == maxGear)
                {
                    if (random.Next(0, 15) == 3) // 1 in 15 chance
                    {
                        dropGearUntil = DateTime.UtcNow + TimeSpan.FromMilliseconds(200 * random.Next(1, 7));
                        return false; // next time gear will drop
                    }

                    return false;
                }

                var maxSpeedAtCurrentGear = speedCaps[currentGear];
                if (Math.Max(0, maxSpeedAtCurrentGear - 30) > currentSpeed) return false; // don't switch if nowhere near max for current
                if (maxSpeedAtCurrentGear - currentSpeed > 5 && random.Next(0, 4) != 1) return false;
                newGearValue = currentGear + 1; // 1:8 chance down, else up
                return true;
            }
            
            double GetSpeed()
            {
                var maxSpeedAtCurrentGear = speedCaps[currentGear];
                if (currentSpeed <= maxSpeedAtCurrentGear & dropGearUntil <= DateTime.UtcNow) return Math.Min(maxSpeedAtCurrentGear, currentSpeed + (double) random.Next(currentGear*25, 1000) / 200 / currentGear);
                if (dropGearUntil > DateTime.UtcNow && currentSpeed <= maxSpeedAtCurrentGear )
                {
                    return Math.Max(0, currentSpeed - (double) random.Next(250, 750)*5 / 1000);
                }
                return Math.Max(0, currentSpeed - (double) random.Next(250, 750)*45 / 1000);
            }
            
            uint GetRPM()
            {
                return (uint) (Math.Sqrt(Math.Abs(currentGear)) * Math.Abs(currentSpeed) * 23.4); // not really realistic, but has a different characteristic than other parameters at least
            }
        }
    }
}