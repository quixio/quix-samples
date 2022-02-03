using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;
using IO.Swagger.Model;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace Strava.Bridge
{
    public class StravaService
    {
        private readonly string clientId;
        private readonly string clientSecret;
        private readonly string initToken;
        
        private const string BaseUrl = "https://www.strava.com/api/v3";

        private HttpClient httpClient;
        private string refreshToken;

        public StravaService(string clientId, string clientSecret, string initToken)
        {
            this.clientId = clientId;
            this.clientSecret = clientSecret;
            this.initToken = initToken;
        }

        public async Task GetToken()
        {
            Console.WriteLine("Authorization started.");
            await this.GetToken(clientId, clientSecret, initToken);
            Console.WriteLine("Authorization succesfull.");
        }
        
        private async Task GetToken(string clientId, string clientSecret, string initToken)
        {
            this.httpClient = new HttpClient();

            var oathParams = new FormUrlEncodedContent(new Dictionary<string, string>
            {
                {"client_id", clientId},
                {"client_secret", clientSecret},
                {"refresh_token", this.refreshToken ?? initToken},
                {"grant_type", "refresh_token"}
            });
            var response = await this.httpClient.PostAsync("https://www.strava.com/oauth/token", oathParams);
            var responseContent = await response.Content.ReadAsStringAsync();
            var json = JObject.Parse(responseContent);
            var token = json["access_token"].ToString();
            this.refreshToken = json["refresh_token"].ToString();

            this.httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);
        }

        public async Task<SummaryActivity[]> GetAthleteActivities()
        {
            var activitiesResponse = await httpClient.GetAsync($"{BaseUrl}/athlete/activities?per_page=50");
            var activitiesResponseContent = await activitiesResponse.Content.ReadAsStringAsync();
            var payload = JsonConvert.DeserializeObject<SummaryActivity[]>(activitiesResponseContent);

            return payload;
        }
        
        public async Task<StreamSet> GetActivityStreams(long activityId)
        {
            var activitiesResponse = await httpClient.GetAsync(
                $"{BaseUrl}/activities/{activityId}/streams?keys=distance,time,latlng,velocity_smooth,heartrate,cadence,watts,temp,moving,grade_smooth,altitude");
            
            var activitiesResponseContent = await activitiesResponse.Content.ReadAsStringAsync();

            var json = JArray.Parse(activitiesResponseContent);
            
            var distanceStream = json.Any(a => a["type"].ToString() == "distance") ? JsonConvert.DeserializeObject<DistanceStream>(json.First(f => f["type"].ToString() == "distance").ToString()) : null;
            var timeStream = json.Any(a => a["type"].ToString() == "time") ? JsonConvert.DeserializeObject<TimeStream>(json.First(f => f["type"].ToString() == "time").ToString()): null;
            var smoothVelocityStream = json.Any(a => a["type"].ToString() == "velocity_smooth") ? JsonConvert.DeserializeObject<SmoothVelocityStream>(json.First(f => f["type"].ToString() == "velocity_smooth").ToString()): null;
            var heartrateStream = json.Any(a => a["type"].ToString() == "heartrate") ? JsonConvert.DeserializeObject<HeartrateStream>(json.First(f => f["type"].ToString() == "heartrate").ToString()): null;
            var latLngStream = json.Any(a => a["type"].ToString() == "latlng") ? JsonConvert.DeserializeObject<LatLngStream>(json.First(f => f["type"].ToString() == "latlng").ToString()): null;
            var cadenceStream = json.Any(a => a["type"].ToString() == "cadence") ? JsonConvert.DeserializeObject<CadenceStream>(json.First(f => f["type"].ToString() == "cadence").ToString()): null;
            var powerStream = json.Any(a => a["type"].ToString() == "watts") ? JsonConvert.DeserializeObject<PowerStream>(json.First(f => f["type"].ToString() == "watts").ToString()): null;
            var temperatureStream = json.Any(a => a["type"].ToString() == "temp") ? JsonConvert.DeserializeObject<TemperatureStream>(json.First(f => f["type"].ToString() == "temp").ToString()): null;
            var gradeStream = json.Any(a => a["type"].ToString() == "grade_smooth") ? JsonConvert.DeserializeObject<SmoothGradeStream>(json.First(f => f["type"].ToString() == "grade_smooth").ToString()): null;
            var altitudeStream = json.Any(a => a["type"].ToString() == "altitude") ? JsonConvert.DeserializeObject<AltitudeStream>(json.First(f => f["type"].ToString() == "altitude").ToString()): null;

            return new StreamSet
            {
                Time = timeStream,
                VelocitySmooth = smoothVelocityStream,
                Distance = distanceStream,
                Altitude = altitudeStream,
                Cadence = cadenceStream,
                Heartrate = heartrateStream,
                Latlng = latLngStream,
                Temp = temperatureStream,
                Watts = powerStream,
                GradeSmooth = gradeStream
            };
        }
        
        
        public async Task<SummaryAthlete> GetAthleteProfile()
        {
            var activitiesResponse = await httpClient.GetAsync($"{BaseUrl}/athlete");
            var activitiesResponseContent = await activitiesResponse.Content.ReadAsStringAsync();
            var payload = JsonConvert.DeserializeObject<SummaryAthlete>(activitiesResponseContent);

            return payload;
        }
        
        public async Task<SummaryActivity[]> GetActivityStream()
        {
            var activitiesResponse = await httpClient.GetAsync($"{BaseUrl}/athlete/activities");
            var activitiesResponseContent = await activitiesResponse.Content.ReadAsStringAsync();
            var payload = JsonConvert.DeserializeObject<SummaryActivity[]>(activitiesResponseContent);

            return payload;
        }
    }
}