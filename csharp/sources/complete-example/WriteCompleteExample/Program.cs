using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using QuixStreams.Streaming;
using QuixStreams.Streaming.Models;
using QuixStreams.Telemetry.Models;

namespace WriteCompleteExample
{
    class Program
    {
        /// <summary>
        /// The frequency at which data will be generated. See <see cref="GenerateData"/>
        /// Increase to send more, lower to send less.
        /// </summary>
        private const uint DataFrequency = 10;
        
        /// <summary>
        /// Main will be invoked when you run the application
        /// </summary>
        /// <param name="args">Command line arguments (not used)</param>
        static void Main(string[] args)
        {
            var cts = new CancellationTokenSource();
            
            // Create a client which holds generic details for creating topic consumers and producers
            var client = new QuixStreamingClient();

            var outputTopicName = Environment.GetEnvironmentVariable("output");
            
            // Create a topic producer using the client's configuration
            using var topicProducer = client.GetTopicProducer(outputTopicName);

            var stream = topicProducer.CreateStream(); // Note, you can also create a stream with a stream id of your choice. Useful if you wish to continuously stream under the same stream id.
                                                // Stream id is what is grouping together individual messages. If you send messages under different stream Id, they are considered unrelated.

            stream.Epoch = DateTime.UtcNow; // It is useful to set the epoch in order to avoid having to add it to each parameter sample and event. Explore other properties of the classes used
                                            // in this example to gain more in-depth knowledge

            // And now set some optional properties on the stream. All of these can be omitted, but can help greatly in organising the streams
            stream.Properties.Location = "sample/car-data"; // location helps to organize the streams into folder like structure
            stream.Properties.TimeOfRecording = new DateTime(2017, 03, 8, 13, 22, 32); // the time of recording, when the data was initially acquired.
            stream.Properties.Name = "C# stream write sample using generated car data"; // the display name of the stream. If not set, the stream id will be used
            stream.Properties.Metadata["Language"] = "C#"; // optional meta data on the stream. Can be any string pair, can be used to provide additional one-time information regarding the stream.
            stream.Properties.Metadata["Sample"] = "WriteStream"; // Updating the value during stream overwrites previous value
            
            // Note: Properties do not need to be manually sent. They will be sent after the last change with a bit of delay (less than a second), but if stream closes, before stream close message.

            // While this is entirely optional, the protocol functions without it, lets describe some of the parameters and events present in the stream so consumers can better understand and work with the data                                            
            stream.Timeseries.DefaultLocation = "/car"; // the default location will determine where parameters will be placed if you add them after this line
            stream.Timeseries
                .AddDefinition("car_speed", "Car speed", "speed of the card") // name (2nd param) and description (3rd param) are optional. The name will default to the parameter id if none provided.
                                                                                                          // Parameter id has to be unique within the stream, because this is what you will use to link the data to the parameter 
                .SetUnit("kph")
                .SetRange(0, 210);
            stream.Timeseries
                .AddLocation("/car/engine") // optionally you can overwrite the default location by specifying location like this
                .AddDefinition("car_gear", "Gear").SetRange(0, 6)
                .AddDefinition("car_engine_rpm", "Engine RPM"); // the definition builder allows you to set as many parameters at once as you wish 

            stream.Events
                .AddDefinition("car_started", "Car Started", "The car has stopped") // add a few events also, similarly to parameters
                .AddDefinition("car_stopped", "Car Stopped", "the car has started") 
                .AddDefinition("Example Event pretty id") // parameter or event ids do not need to be complicated, just unique. Consistency is good.
                .SetLevel(EventLevel.Trace); // You can also set severity of an event, there are many options to choose from
            
            // Important note: Parameter/Event definitions do not need to be manually sent, but values do! Definitions will be sent automatically after the last change with a bit of delay (less than a second), but if stream closes,
            // before stream close message. This can be forced with .Flush(), but unnecessary in nearly every scenario
            
            // Send some data to the topic
            stream.Events
                .AddTimestamp(DateTime.UtcNow) // when you wish to add data, you always need to start with .AddTimestamp or .AddTimestampMilliseconds//Nanoseconds. Read the documentation of each to know exactly how they work
                .AddValue("Example Event pretty id", "You can add as many events as you wish, All will all be added at this timestamp")
                .Publish();

            stream.Events
                .AddTimestampNanoseconds(150)
                .AddValue("Example Event pretty id", "event at 150 nanoseconds after previously configured Epoch");

            var data = new TimeseriesData();
            data.AddTimestamp(DateTime.UtcNow) // Note: When adding timestamp using DateTime, epoch is ignored.
                .AddValue("car_engine_on", "true") // as previously mentioned, you do not need to define parameters ahead of time, but if you don't, there will be no additional context provided for them, like min/max value or human friendly name
                .AddValue("car_engine_on_num", 1);// also, parameter value can be string, not just double
            stream.Timeseries.Publish(data);

            Console.WriteLine("Generating stream data");
            // Generate some data, similarly to above, but a bit more.
            GenerateData(stream, cts.Token);

            // Hook up to termination signal (for docker image) and CTRL-C
            App.Run(beforeShutdown: () =>
            {
                // before shutdown, cancel the token to stop generating data
                cts.Cancel();
            });
            
            Console.WriteLine("Closing stream");
            stream.Close(StreamEndType.Closed); // If the stream isn't closed, it will be left open. Useful if you intend to signal to consumers more data should be expected in the future.
                                                // There are several close types provided, there are no specific meaning tied to them, up to you to interpret them the way you wish
            Console.WriteLine("Exiting...");
        }
        
        /// <summary>
        /// Generate data for your stream. The function is a little more complicated to provide at least a bit of realistic data, however the methods used for sending data is still the same as in <see cref="Main"/>
        /// </summary>
        /// <param name="stream">The stream to generate the data to</param>
        /// <param name="ctsToken">Application exit cancellation token</param>
        static void GenerateData(IStreamProducer stream, CancellationToken ctsToken)
        {
            var interval = (int)((double)(1 * 1000) / DataFrequency); // calc how many ms should be the interval between samples
            
            // Some local variables to help with our data generation to be a little more realistic. Feel free to ignore them
            var random = new Random();
            var currentGear = 0;
            var speedCaps = new Dictionary<int, double> {{0, 0}, {1, 70}, {2, 90}, {3, 110}, {4, 140}, {5, 170}, {6, 210}};
            var maxGear = speedCaps.Keys.Max();
            var lastGearChange = DateTime.MinValue;
            var dropGearUntil = DateTime.MinValue;
            var currentSpeed = 0D;
            
            stream.Events.AddTimestamp(DateTime.UtcNow).AddValue("car_started", "Car started!");
            
            while (!ctsToken.IsCancellationRequested) // exit if CTRL-C is invoked
            {
                var data = new TimeseriesData();
                var timestampValues = data.AddTimestamp(DateTime.UtcNow); // not necessary to set builder to a variable, but I wish to have the same timestamp for all values within an iteration
                                                                            // therefore saving it like this.
                if (GetGearValue(out var newGear))
                {
                    currentGear = newGear;
                    lastGearChange = DateTime.UtcNow;
                    timestampValues.AddValue("car_gear", newGear); // If you don't have a lot of parameter identifiers and know them ahead of time, might be best to use a constant instead for name
                }

                currentSpeed = GetSpeed();
                timestampValues.AddValue("car_speed", currentSpeed);
                timestampValues.AddValue("car_engine_rpm", GetRPM());
                stream.Timeseries.Publish(data);
                Thread.Sleep(interval); // sleep the interval
            }
            
            stream.Events.AddTimestamp(DateTime.UtcNow).AddValue("data_interrupted", "data generation interrupted");
            
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