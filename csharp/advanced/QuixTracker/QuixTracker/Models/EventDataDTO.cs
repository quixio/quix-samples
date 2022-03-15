using System.Collections.Generic;

namespace QuixTracker.Models
{
    public class EventDataDTO
    {
        public long Timestamp { get; set; }
        public string Id { get; set; }
        public string Value { get; set; }
        public Dictionary<string, string> Tags { get; set; }
    }
}
