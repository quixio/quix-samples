using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace Service.Models
{
    public class Sensor
    {
        [JsonProperty("comp")]
        public string Comp { get; set; }

        [JsonProperty("value")]
        public double Value { get; set; }
    }

    public class Index
    {
        [JsonProperty("comp")]
        public string Comp { get; set; }

        [JsonProperty("value")]
        public double Value { get; set; }
    }

    public class DataPoint
    {
        [JsonProperty("timestamp")]
        public DateTime Timestamp { get; set; }

        [JsonProperty("score")]
        public double Score { get; set; }

        [JsonProperty("sensors")]
        public List<Sensor> Sensors { get; set; }

        [JsonProperty("indices")]
        public List<Index> Indices { get; set; }
    }

    public class RawDataResponse
    {
        [JsonProperty("data")]
        public List<DataPoint> Data { get; set; }
    }

}