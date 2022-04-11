using System;
using System.Diagnostics;
using System.Linq;

namespace Quix.Snowflake.Domain.Models
{
    [DebuggerDisplay("{ParameterId}, {Name}")]
    public class TelemetryParameter : IEquatable<TelemetryParameter>
    {
        /// <summary>
        /// Purely here for deserialization purposes
        /// </summary>
        public TelemetryParameter()
        {
        }

        public TelemetryParameter(string streamId)
        {
            this.StreamId = streamId ?? throw new ArgumentNullException(nameof(streamId));
        }
        
        /// <summary>
        /// Using as the primary key to avoid use of composite keys
        /// </summary>
        public string ObjectId { get; set; } = Guid.NewGuid().ToString("N");

        public string ParameterId { get; set; }

        public string Name { get; set; }

        public string StreamId { get; private set; }
        
        public string Description { get; set; }

        public double? MinimumValue { get; set; }

        public double? MaximumValue { get; set; }

        public string Unit { get; set; }

        public string Format { get; set; }

        public string CustomProperties { get; set; }
        
        /// <summary>
        /// Location within the parameter tree. The Location of the parameter is equivalent to the path of the parent group
        /// </summary>
        public string Location { get;set; }
        
        public ParameterType Type { get; set; }

        public override int GetHashCode()
        {
            unchecked
            {
                var hash = ((this.ParameterId != null ? this.ParameterId.GetHashCode() : 0) * 397);
                hash ^= (this.Name != null ? this.Name.GetHashCode() : 0);
                hash ^= (this.Description != null ? this.Description.GetHashCode() : 0);
                hash ^= (this.MinimumValue != null ? this.MinimumValue.GetHashCode() : 0);
                hash ^= (this.MaximumValue != null ? this.MaximumValue.GetHashCode() : 0);
                hash ^= (this.Unit != null ? this.Unit.GetHashCode() : 0);
                hash ^= (this.Format != null ? this.Format.GetHashCode() : 0);
                hash ^= (this.CustomProperties != null ? this.CustomProperties.GetHashCode() : 0);
                hash ^= (this.StreamId != null ? this.StreamId.GetHashCode() : 0);
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
            return this.Equals((TelemetryParameter)obj);
        }

        public bool Equals(TelemetryParameter other)
        {
            if (ReferenceEquals(null, other))
                return false;
            if (ReferenceEquals(this, other))
                return true;
            return string.Equals(this.ParameterId, other.ParameterId)
                && string.Equals(this.Name, other.Name)
                && string.Equals(this.Description, other.Description)
                && Equals(this.MinimumValue, other.MinimumValue)
                && Equals(this.MaximumValue, other.MaximumValue)
                && string.Equals(this.Unit, other.Unit)
                && string.Equals(this.Format, other.Format)
                && string.Equals(this.CustomProperties, other.CustomProperties);
        }
    }

    /// <summary>
    /// The possible parameter types
    /// </summary>
    public enum ParameterType
    {
        /// <summary>
        /// The parameter type is not known yet
        /// </summary>
        Unknown = 0, // Important to be 0, to be default value
        
        /// <summary>
        /// Numeric parameter type
        /// </summary>
        Numeric = 1,
        
        /// <summary>
        /// String parameter type
        /// </summary>
        String = 2,
        
        /// <summary>
        /// Binary parameter type
        /// </summary>
        Binary = 3
    }
}
