using System.Collections.Generic;
using Newtonsoft.Json;

namespace Service.Models
{
    public class Device
    {
        [JsonProperty("name")]
        public string Name { get; set; }

        [JsonProperty("macAddress")]
        public string MacAddress { get; set; }

        [JsonProperty("latitude")]
        public double Latitude { get; set; }

        [JsonProperty("preference")]
        public string Preference { get; set; }

        [JsonProperty("timezone")]
        public string Timezone { get; set; }

        [JsonProperty("roomType")]
        public string RoomType { get; set; }

        [JsonProperty("deviceType")]
        public string DeviceType { get; set; }

        [JsonProperty("longitude")]
        public double Longitude { get; set; }

        [JsonProperty("spaceType")]
        public string SpaceType { get; set; }

        [JsonProperty("deviceUUID")]
        public string DeviceUUID { get; set; }

        [JsonProperty("deviceId")]
        public int DeviceId { get; set; }

        [JsonProperty("locationName")]
        public string LocationName { get; set; }
    }

    public class DeviceListResponse
    {
        [JsonProperty("devices")]
        public List<Device> Devices { get; set; }
    }
}

