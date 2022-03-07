using System;
using System.Collections.Generic;
using System.IO;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading;
using System.Threading.Tasks;
using Quix.Sdk.Streaming;
using Microsoft.Extensions.Configuration;
using Service.Models;

namespace Service
{
    class Program
    {
        private static HttpClient client = new HttpClient();
        /// <summary>
        /// The service entry point
        /// </summary>
        static async Task Main(string[] args)
        {
            var exitEvent = new ManualResetEventSlim();
            Console.CancelKeyPress += (s, e) =>
            {
                Console.WriteLine($"{DateTime.UtcNow:g} Exiting");
                e.Cancel = true; // In order to allow the application to cleanly exit instead of terminating it
                exitEvent.Set();
            };
            
            var configuration = GetConfiguration(args);

            List<Device> devices;
            try
            {
                devices = await GetDevices(configuration.Awair);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"ERROR: {ex}"); 
                Thread.Sleep(-1); // this is here so the service doesn't automatically restart instantly until end of times
                return;
            }

            if (devices.Count == 0)
            {
                Console.WriteLine($"ERROR: There are no devices!!!"); 
                Thread.Sleep(-1); // this is here so the service doesn't automatically restart instantly until end of times
                return;
            }
            System.Console.WriteLine("CONNECTED!");
            Console.WriteLine($"{DateTime.UtcNow:g} Found {devices.Count} devices:");
            foreach (var device in devices)
            {
                Console.WriteLine($"{DateTime.UtcNow:g}    [{device.DeviceUUID}] {device.Name}, {device.LocationName}");    
            }

            var client = new QuixStreamingClient(); // Pick up token from env variable

            // Create a StreamingClient (using the factory) in order to easily created new streams using the configured kafka and topic which you set up above
            var outputTopic = client.OpenOutputTopic(configuration.Topic);

            var cts = new CancellationTokenSource();
            var task = ImportData(outputTopic, devices, configuration.Awair, cts.Token);
            task.ContinueWith(t =>
            {
                exitEvent.Set();
            }, TaskContinuationOptions.OnlyOnFaulted);
            
            // Wait for CTRL-C
            exitEvent.Wait();
            cts.Cancel();
            Console.WriteLine($"{DateTime.UtcNow:g} Waiting for streams data import to stop");
            await task;
            Console.WriteLine($"{DateTime.UtcNow:g} Waiting for topic to close");
            outputTopic.Dispose();
            Console.WriteLine($"{DateTime.UtcNow:g} Streams closed. Bye!");
        }

        public static async Task ImportData(IOutputTopic topic, List<Device> devices, AwairConfiguration awairConfiguration, CancellationToken cancellationToken)
        {

                var periodToGet = TimeSpan.FromMinutes(5);
                var periodToSleep = periodToGet;
                var pointsToGet = 350;
                var lastImported = new Dictionary<string, DateTime>();
                while (!cancellationToken.IsCancellationRequested)
                {
                    try
                    {
                        var to = DateTime.UtcNow;
                        var from = to.Add(-periodToGet);
                        foreach (var device in devices)
                        {
                            if (cancellationToken.IsCancellationRequested) break;
                            Console.WriteLine($"{DateTime.UtcNow:g} Importing data for device {device.DeviceUUID} - {device.Name}");
                            var stream = topic.GetOrCreateStream($"{device.DeviceUUID} - {device.Name}", (sw) =>
                            {
                                sw.Properties.Name = device.Name;
                                sw.Properties.Location = "/Awair";
                                var md = sw.Properties.Metadata;
                                md["DevicePreference"] = device.Preference;
                                md["DeviceTimezone"] = device.Timezone;
                                md["DeviceType"] = device.DeviceType;
                                md["DeviceLocation"] = device.LocationName;
                                md["DeviceRoomType"] = device.RoomType;
                                md["DeviceSpaceType"] = device.SpaceType;
                                md["DeviceLongitude"] = device.Longitude.ToString();
                                md["DeviceLatitude"] = device.Latitude.ToString();

                                var parameters = sw.Parameters;
                                parameters.AddDefinition("humid", "Humidity").SetRange(0, 100);
                                parameters.AddDefinition("co2", "CO2").SetRange(0, 5000);
                                parameters.AddDefinition("pm25", "PM2.5").SetRange(0, 1000);
                                parameters.AddDefinition("temp", "Temperature").SetRange(10, 50);
                                parameters.AddDefinition("voc", "VOC", "Volatile Organic Compound").SetRange(0, 3500);
                                parameters.AddDefinition("score", "Score", "The air score between 0 and 100, where greater is better").SetRange(0, 100);
                            });
                            if (!lastImported.TryGetValue(stream.StreamId, out var latestImported))
                            {
                                latestImported = from.AddSeconds(-1);
                            }

                            var points = await GetRawDataPoints(awairConfiguration, device, latestImported.AddSeconds(1), to, pointsToGet);

                            var ignoreBeforeOrAt = latestImported; // probably not necessary but can't hurt
                            foreach (var dataPoint in points)
                            {
                                if (ignoreBeforeOrAt >= dataPoint.Timestamp) continue;
                                var ts = stream.Parameters.Buffer.AddTimestamp(dataPoint.Timestamp);
                                foreach (var pointSensor in dataPoint.Sensors)
                                {
                                    ts.AddValue(pointSensor.Comp, pointSensor.Value);
                                }

                                ts.AddValue("score", dataPoint.Score);
                                ts.Write();
                                if (latestImported < dataPoint.Timestamp)
                                {
                                    latestImported = dataPoint.Timestamp;
                                }
                            }

                            lastImported[stream.StreamId] = latestImported;
                            Console.WriteLine($"{DateTime.UtcNow:g} Imported data for device {device.DeviceUUID} - {device.Name}");
                        }

                        try
                        {
                            Console.WriteLine($"{DateTime.UtcNow:g} Sleeping for {periodToSleep:g}");
                            await Task.Delay(periodToSleep, cancellationToken);
                            Console.WriteLine($"{DateTime.UtcNow:g} Woke up!");
                        }
                        catch
                        {
                            // cancelled
                            if (cancellationToken.IsCancellationRequested) break;
                        }                    
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"{DateTime.UtcNow:g} Error while importing!");
                        Console.WriteLine(ex.ToString());
                    }
                }
        }
        
        public static async Task<List<DataPoint>> GetRawDataPoints(AwairConfiguration awairConfiguration, Device device, DateTime from, DateTime to, int pointCount)
        {
            if (awairConfiguration == null) throw new ArgumentNullException(nameof(awairConfiguration));
            if (string.IsNullOrWhiteSpace(awairConfiguration.Token)) throw new ArgumentNullException(nameof(awairConfiguration), "Awair token is null");
            var message = new HttpRequestMessage(HttpMethod.Get, $"https://developer-apis.awair.is/v1/users/self/devices/{device.DeviceType}/{device.DeviceId}/air-data/raw?from={from.ToString("O")}&to={to.ToString("O")}&limit={pointCount}&desc=true&fahrenheit=false");
            message.Headers.Authorization = new AuthenticationHeaderValue("Bearer", awairConfiguration.Token);
            var response = await client.SendAsync(message);
            if (!response.IsSuccessStatusCode)
            {
                var msg = response.Content.ReadAsStringAsync().GetAwaiter().GetResult();
                throw new Exception($"StatusCode: {response.StatusCode}{Environment.NewLine}Response: {msg}");
            }
            var content = response.Content.ReadAsStringAsync().GetAwaiter().GetResult();
            return Newtonsoft.Json.JsonConvert.DeserializeObject<RawDataResponse>(content).Data;
        }


        public static async Task<List<Device>> GetDevices(AwairConfiguration awairConfiguration)
        {
            if (awairConfiguration == null) throw new ArgumentNullException(nameof(awairConfiguration));
            if (string.IsNullOrWhiteSpace(awairConfiguration.Token)) throw new ArgumentNullException(nameof(awairConfiguration), "Awair token is null");
            var message = new HttpRequestMessage(HttpMethod.Get, "https://developer-apis.awair.is/v1/users/self/devices");
            message.Headers.Authorization = new AuthenticationHeaderValue("Bearer", awairConfiguration.Token);
            var response = await client.SendAsync(message);
            if (!response.IsSuccessStatusCode)
            {
                var msg = await response.Content.ReadAsStringAsync();
                throw new Exception($"StatusCode: {response.StatusCode}{Environment.NewLine}Response: {msg}");
            }
            var content = await response.Content.ReadAsStringAsync();
            return Newtonsoft.Json.JsonConvert.DeserializeObject<DeviceListResponse>(content).Devices;
        }
        
        
        /// <summary>
        /// Gets steaming configuration from app settings
        /// </summary>
        static Configuration GetConfiguration(string[] args)
        {
            var builder = new ConfigurationBuilder();
            builder.SetBasePath(Directory.GetCurrentDirectory());
            builder.AddJsonFile("appsettings.json");
            builder.AddEnvironmentVariables();
            var config = builder.Build();
            var configuration = new Configuration();
            config.Bind(configuration);
            return configuration;
        }
    }
}