using System;
using System.Diagnostics;

namespace Quix.Snowflake.Domain.Models
{
    [DebuggerDisplay("{Path}, {Name}")]
    public class TelemetryParameterGroup : IEquatable<TelemetryParameterGroup>
    {
        internal TelemetryParameterGroup()
        {
        }

        public TelemetryParameterGroup(string streamId)
        {
            this.StreamId = streamId ?? throw new ArgumentNullException(nameof(streamId));
        }
        
        /// <summary>
        /// Using as the primary key to avoid use of composite keys
        /// </summary>
        public string ObjectId { get; set; } = Guid.NewGuid().ToString("N");

        public string StreamId { get; private set; }

        public string Name { get; set; }

        public string Description { get; set; }

        public string CustomProperties { get; set; }
        
        public int ChildrenCount { get; set; }
        
        /// <summary>
        /// <see cref="Location"/> + /<see cref="Name"/>
        /// Also serves as an unique identifier
        /// </summary>
        public string Path { get; set; }
        
        /// <summary>
        /// Location within the parameter tree. The Location of the parameter group is equivalent to the location of the parent group location + /parent group id
        /// Example: If parent parameter group location is root ("/") and parent parameter group id is "Body" then location will be "/Body"
        /// </summary>
        public string Location { get;set; }

        public override int GetHashCode()
        {
            unchecked
            {
                var hash = ((this.Path != null ? this.Path.GetHashCode() : 0) * 397);
                hash ^= (this.Name != null ? this.Name.GetHashCode() : 0);
                hash ^= (this.Description != null ? this.Description.GetHashCode() : 0);
                hash ^= (this.CustomProperties != null ? this.CustomProperties.GetHashCode() : 0);
                hash ^= (this.StreamId != null ? this.StreamId.GetHashCode() : 0);
                hash ^= (this.ChildrenCount != null ? this.ChildrenCount.GetHashCode() : 0);
                // hash ^= (this.BsonObjectId != null ? this.BsonObjectId.GetHashCode() : 0);
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
            return this.Equals((TelemetryParameterGroup)obj);
        }

        public bool Equals(TelemetryParameterGroup other)
        {
            if (ReferenceEquals(null, other))
                return false;
            if (ReferenceEquals(this, other))
                return true;
            return string.Equals(this.Path, other.Path)
                   && string.Equals(this.Name, other.Name)
                   && string.Equals(this.StreamId, other.StreamId)
                   && string.Equals(this.Description, other.Description)
                   && string.Equals(this.CustomProperties, other.CustomProperties);
        }
    }
}
