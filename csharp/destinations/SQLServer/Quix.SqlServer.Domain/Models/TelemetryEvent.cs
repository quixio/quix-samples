using System;
using System.Diagnostics;

namespace Quix.SqlServer.Domain.Models
{
    [DebuggerDisplay("{EventId}, {Name}")]
    public class TelemetryEvent : IEquatable<TelemetryEvent>
    {
        /// <summary>
        /// Purely here for deserialization purposes
        /// </summary>
        public TelemetryEvent()
        {
        }

        public TelemetryEvent(string streamId)
        {
            this.StreamId = streamId ?? throw new ArgumentNullException(nameof(streamId));
        }

        /// <summary>
        /// Using as the primary key to avoid use of composite keys
        /// </summary>
        public string ObjectId { get; set; } = Guid.NewGuid().ToString("N");

        public string EventId { get; set; }

        public string Name { get; set; }

        public string StreamId { get; private set; }
        
        public string Description { get; set; }
        public string CustomProperties { get; set; }
        
        /// <summary>
        /// The level of the event. Defaults to <see cref="TelemetryEventLevel.Information"/>
        /// </summary>
        public TelemetryEventLevel Level { get; set; } = TelemetryEventLevel.Information;
        
        /// <summary>
        /// Location within the event tree. The Location of the event is equivalent to the path of the parent group
        /// </summary>
        public string Location { get;set; }

        public override int GetHashCode()
        {
            unchecked
            {
                var hash = ((this.EventId != null ? this.EventId.GetHashCode() : 0) * 397);
                hash ^= (this.Name != null ? this.Name.GetHashCode() : 0);
                hash ^= (this.Description != null ? this.Description.GetHashCode() : 0);
                hash ^= (this.CustomProperties != null ? this.CustomProperties.GetHashCode() : 0);
                hash ^= (this.StreamId != null ? this.StreamId.GetHashCode() : 0);
                hash ^= (this.Level != null ? this.Level.GetHashCode() : 0);
                hash ^= (this.Location != null ? this.Location.GetHashCode() : 0);
                //hash ^= (this.BsonObjectId != null ? this.BsonObjectId.GetHashCode() : 0);
                return hash;
            }
        }

        public override bool Equals(object obj)
        {
            if (ReferenceEquals(null, obj))
                return false;
            if (ReferenceEquals(this, obj))
                return true;
            if (obj.GetType() != this.GetType())
                return false;
            return this.Equals((TelemetryEvent)obj);
        }

        public bool Equals(TelemetryEvent other)
        {
            if (ReferenceEquals(null, other))
                return false;
            if (ReferenceEquals(this, other))
                return true;
            return string.Equals(this.EventId, other.EventId)
                && string.Equals(this.Name, other.Name)
                && string.Equals(this.Description, other.Description)
                && string.Equals(this.CustomProperties, other.CustomProperties)
                && Equals(this.Level, other.Level)
                && string.Equals(this.Location, other.Location);
        }
    }

    public enum TelemetryEventLevel
    {
        Trace = 0,
        Debug = 1,
        Information  = 2,
        Warning = 3,
        Error = 4,
        Critical = 5,
    }
}
