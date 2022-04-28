using System;
using System.Collections.Generic;
using System.Diagnostics;

namespace Quix.Snowflake.Domain.Models
{
    public enum UpdateType
    {
        Insert,
        Update,
        Delete,
        //Replace, //todo needed??
        UpdateMany
    }
    
    public class TelemetryStreamUpdate
    {
        public TelemetryStreamUpdate(UpdateType updateType, string streamIdFilter = null, string parameterIdFilter = null)
        {
            UpdateType = updateType;
            StreamIdFilter = streamIdFilter;
            ParameterIdFilter = parameterIdFilter;
        }

        public string StreamIdFilter { get; private set; }
        public string ParameterIdFilter { get; private set; }
        
        public TelemetryStream TelemetryStream { get; set; }
        public UpdateType UpdateType { get; private set; }
    }
    
    [DebuggerDisplay("{StreamId}, {Name}")]
    public class TelemetryStream
    {
        /// <summary>
        /// Purely here for deserialization purposes
        /// </summary>
        public TelemetryStream()
        {
        }
        
        public TelemetryStream(string streamId)
        {
            this.StreamId = streamId ?? throw new ArgumentNullException(nameof(streamId));
        }

        public string StreamId { get; private set; }

        public string Name { get; set; }

        /// <summary>
        /// The time of first stream save.
        /// </summary>
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

        /// <summary>
        /// The last time the stream was updated
        /// </summary>
        public DateTime LastUpdate { get; set; } = DateTime.UtcNow;
        
        /// <summary>
        /// Time of the recording. Optional.
        /// </summary>
        public DateTime? TimeOfRecording { get; set; }
        
        /// <summary>
        /// The earliest data within the session in unix nanoseconds
        /// </summary>
        public long? Start { get; set; }

        /// <summary>
        /// The last data within the session in unix nanoseconds
        /// </summary>
        public long? End { get; set; }
        
        public long? Duration
        {
            get
            {
                if (End == null) return null;
                if (Start == null) return null;
                return End - Start;
            }
        }

        /// <summary>
        /// State of the stream
        /// </summary>
        public StreamStatus Status { get; set; }

        /// <summary>
        /// Metadata (extra context) for the stream
        /// </summary>
        public Dictionary<string,string> Metadata { get; set; }

        /// <summary>
        /// The stream Ids this session is derived from.
        /// </summary>
        public List<string> Parents { get; set; }

        /// <summary>
        /// The location of the stream
        /// </summary>
        public string Location { get; set; }

        /// <summary>
        /// The topic the stream originates from
        /// </summary>
        public string Topic { get; set; }
        
        /// <summary>
        /// The time of soft deletion.
        /// </summary>
        public DateTime? SoftDeleteAt { get; set; }
    }
}
