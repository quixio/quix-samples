using System.Linq;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json.Linq;

namespace Strava.Bridge
{
    public class QuixApiService
    {
        private readonly string baseUrl;

        private HttpClient client;

        public QuixApiService(string token, string baseUrl)
        {
            this.baseUrl = baseUrl;

            this.client = new HttpClient();
            
            this.client.DefaultRequestHeaders.Authorization = AuthenticationHeaderValue.Parse("bearer " + token);
        }

        public async Task<string[]> GetPersistedActivities()
        {
            var postBody = new StringContent("{}", Encoding.Default, "application/json");
            var response = await client.PostAsync(baseUrl + "/streams", postBody);
            var content = await response.Content.ReadAsStringAsync();

            var json = JArray.Parse(content);

            var streamIds = json.Select(s => s["streamId"].ToString()).ToArray();

            return streamIds;
        }
    }
}