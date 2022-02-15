using System;
using System.Linq;
using System.Threading.Tasks;
using Quix.Sdk.Streaming;

namespace Strava.Bridge
{
    class Program
    {
        
        private static string _clientId = "YOUR_CLIENT_ID";
        private static string _clientSecret = "YOUR_CLIENT_SECRET";
        private static string _stravaRefreshToken = "YOUR_STRAVA_REFRESH_TOKEN";

        private static string _quixPatToken = "YOUR_QUIX_PAT_TOKEN";
        private static string _outputTopicName = "outputTopic";
        
        private const  string QueryApiBaseUrl = "https://telemetry-query-{placeholder:workspaceId}.{placeholder:environment.subdomain}.quix.ai";

        
        /// <summary>
        /// Main will be invoked when you run the application
        /// </summary>
        static async Task Main()
        {

            _quixPatToken = Environment.GetEnvironmentVariable("PATToken");
            _clientId = Environment.GetEnvironmentVariable("ClientId");
            _clientSecret = Environment.GetEnvironmentVariable("ClientSecret");
            _stravaRefreshToken = Environment.GetEnvironmentVariable("StravaRefreshToken");
            _outputTopicName = Environment.GetEnvironmentVariable("output");
            
            // Create a client which holds generic details for creating input and output topics
            var factory = new QuixStreamingClient();
            
            using var outputTopic = factory.OpenOutputTopic(_outputTopicName);

            var stravaService = new StravaService(_clientId, _clientSecret, _stravaRefreshToken);
            var quixApiService = new QuixApiService(_quixPatToken, QueryApiBaseUrl);
            
            while (true)
            {
                Console.WriteLine("Import started.");
                
                await ImportActivities(outputTopic,stravaService, quixApiService);

                Console.WriteLine("Import finished.");

                await Task.Delay(5 * 60 * 1000);
            }
        }

        private static async Task ImportActivities(IOutputTopic outputTopic, StravaService stravaService, QuixApiService quixApiService)
        {
            await stravaService.GetToken();

            Console.WriteLine("Getting activities...");
            var athlete = await stravaService.GetAthleteProfile();
            var activities = await stravaService.GetAthleteActivities();
            Console.WriteLine($"{activities.Length} activities downloaded.");

            var persistedActivities = await quixApiService.GetPersistedActivities();

            var newActivities = activities.Where(w => !persistedActivities.Contains($"strava-v10-{_clientId}-{w.Id}")).ToList();

            Console.WriteLine($"{newActivities.Count} new activities.");

            
            foreach (var activity in newActivities)
            {
                var streamId = $"strava-v10-{_clientId}-{activity.Id}";
                Console.WriteLine($"Creating stream {streamId}.");

                var stream = outputTopic.CreateStream(streamId); //$"strava-v3-{ClientId}-{activity.Id}");
                stream.Properties.Location =
                    $"strava/{activity.Type.ToString()}/{athlete.Firstname}-{athlete.Lastname}";

                var startDate = activity.StartDate;

                stream.Properties.Name = activity.Name;
                stream.Properties.TimeOfRecording = DateTime.Now;
                stream.Properties.Metadata.Add("GearId", activity.GearId);
                stream.Properties.Metadata.Add("Timezone", activity.Timezone);
                stream.Properties.Metadata.Add("AthleteId", activity.Athlete.Id.ToString());
                stream.Properties.Metadata.Add("Distance", activity.Distance.GetValueOrDefault().ToString());
                stream.Properties.Metadata.Add("Kilojoules", activity.Kilojoules.ToString());
                stream.Properties.Metadata.Add("ActivityType", activity.Type.ToString());

                var streamsData = await stravaService.GetActivityStreams(activity.Id.Value);

                stream.Parameters.AddDefinition("speed", "Speed", "Speed in KMH")
                    .SetUnit("KPH")
                    .SetRange(0, activity.MaxSpeed.GetValueOrDefault() * 3.6);

                stream.Parameters.AddDefinition("distance", "Distance", "Metres from the start of the trip.")
                    .SetUnit("metres")
                    .SetRange(0, activity.Distance.Value);

                stream.Parameters.AddDefinition("altitude", "Altitude", "Altitude in metres above see level")
                    .SetUnit("msl")
                    .SetRange(activity.ElevLow.GetValueOrDefault(), activity.ElevHigh.GetValueOrDefault());

                stream.Parameters.AddDefinition("cadence", "Cadence", "Number of pedals revolutions per minute.")
                    .SetUnit("rpm")
                    .SetRange(0, 200);

                stream.Parameters.AddDefinition("heartrate", "Heartrate", "Heart beats per minute of rider.")
                    .SetUnit("bpm")
                    .SetRange(0, 300);

                stream.Parameters.AddDefinition("watts", "Watts", "Power output.")
                    .SetUnit("W")
                    .SetRange(0, 500);

                stream.Parameters.AddDefinition("lat", "Latitude", "Latitude coordinates.");
                stream.Parameters.AddDefinition("lng", "Longitude", "Longitude coordinates.");

                if (streamsData.Temp != null)
                {
                    stream.Parameters.AddDefinition("temp", "Temperature", "Ambient temperature of environment.")
                        .SetUnit("°C")
                        .SetRange(streamsData.Temp.Data.Where(w => w.HasValue).Min(m => m.Value),
                            streamsData.Temp.Data.Where(w => w.HasValue).Max(m => m.Value));
                }

                if (streamsData.GradeSmooth != null)
                {
                    stream.Parameters.AddDefinition("grade", "Grade", "Grade of ascent/descent.")
                        .SetUnit("deg")
                        .SetRange(streamsData.GradeSmooth.Data.Where(w => w.HasValue).Min(m => m.Value),
                            streamsData.GradeSmooth.Data.Where(w => w.HasValue).Max(m => m.Value));
                }

                for (var index = 0; index < streamsData.Time.OriginalSize.Value; index++)
                {
                    var buffer = stream.Parameters.Buffer;
                    buffer.Epoch = startDate.GetValueOrDefault();
                    buffer.PacketSize = 100;
                    var timestamp = buffer
                        .AddTimestampMilliseconds(streamsData.Time.Data[index].GetValueOrDefault() * 1000);

                    if (streamsData.VelocitySmooth != null)
                    {
                        timestamp.AddValue("speed",
                            streamsData.VelocitySmooth.Data[index].GetValueOrDefault() * 3.6);
                    }

                    if (streamsData.Distance != null)
                    {
                        timestamp.AddValue("distance", streamsData.Distance.Data[index].GetValueOrDefault());
                    }

                    if (streamsData.Altitude != null)
                    {
                        timestamp.AddValue("altitude", streamsData.Altitude.Data[index].GetValueOrDefault());
                    }

                    if (streamsData.Cadence != null)
                    {
                        timestamp.AddValue("cadence", streamsData.Cadence.Data[index].GetValueOrDefault());
                    }

                    if (streamsData.Heartrate != null)
                    {
                        timestamp.AddValue("heartrate", streamsData.Heartrate.Data[index].GetValueOrDefault());
                    }

                    if (streamsData.Watts != null)
                    {
                        timestamp.AddValue("watts", streamsData.Watts.Data[index].GetValueOrDefault());
                    }


                    if (streamsData.Latlng != null)
                    {
                        timestamp
                            .AddValue("lat", streamsData.Latlng.Data[index][0].GetValueOrDefault())
                            .AddValue("lng", streamsData.Latlng.Data[index][1].GetValueOrDefault());
                    }

                    if (streamsData.Temp != null)
                    {
                        timestamp.AddValue("temp", streamsData.Temp.Data[index].GetValueOrDefault());
                    }

                    if (streamsData.GradeSmooth != null)
                    {
                        timestamp.AddValue("grade", streamsData.GradeSmooth.Data[index].GetValueOrDefault());
                    }

                    timestamp.AddTag("athlete", $"{athlete.Firstname}-{athlete.Lastname}");
                    timestamp.AddTag("athlete-sex", $"{athlete.Sex}");
                    timestamp.AddTag("activity-type", $"{activity.Type.ToString()}");

                    timestamp.Write();
                }

                stream.Close();
                Console.WriteLine($"Stream {streamId} imported.");
            }
        }
    }
}
