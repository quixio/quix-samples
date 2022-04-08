using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using Quix.Snowflake.Domain.Models;
using Quix.Snowflake.Domain.Repositories;
using Quix.Snowflake.Infrastructure.Shared;

namespace Quix.Snowflake.Infrastructure.Metadata
{
    
    //TODO need to implement this.
    
    public class StreamRepository : IStreamRepository
    {
        private readonly IDbConnection dbConnection;

        public StreamRepository(IDbConnection dbConnection,
            ILogger<StreamRepository> logger)
        {
            this.dbConnection = dbConnection;
        }
        
        public Task Save(TelemetryStream stream)
        {
            InsertStreamData(stream);
            InsertStreamMetaData(stream);
            InsertStreamRelations(stream);
            
            return Task.CompletedTask;
        }

        private void InsertStreamData(TelemetryStream stream)
        {
            var sqlHeader = "INSERT INTO PUBLIC.Streams (Id, Name, Topic, CreatedAt, Start, End, Duration, " +
                            "LastUpdate, SoftDeleteAt, TimeOfRecording, Location, Status, Version, MigrationState) ";

            var sqlStringBuilder = new StringBuilder();

            // insert single items first
            sqlStringBuilder.Append($"VALUES ('{stream.StreamId}', '{stream.Name}', '{stream.Topic}'" +
                                    $", '{stream.CreatedAt}', '{stream.Start}', '{stream.End}'" +
                                    $", '{stream.Duration}', '{stream.LastUpdate}'" +
                                    $", '{stream.SoftDeleteAt}', '{stream.TimeOfRecording}'" +
                                    $", '{stream.Location}', '{stream.Status}'" +
                                    $", '{stream.Version}', '{stream.MigrationState}')");

            SnowflakeQuery.ExecuteSnowFlakeNonQuery(dbConnection, sqlHeader + sqlStringBuilder);
        }
        
        private void InsertStreamMetaData(TelemetryStream stream)
        {
            // todo const for table + schema
            var sqlHeader = "INSERT INTO PUBLIC.StreamMetadata (StreamId, Key, Value) ";

            var sqlStringBuilder = new StringBuilder();

            foreach (var metadata in stream.Metadata)
                sqlStringBuilder.Append($"VALUES ('{stream.StreamId}', '{metadata.Key}', '{metadata.Value}')");
            
            SnowflakeQuery.ExecuteSnowFlakeNonQuery(dbConnection, sqlHeader + sqlStringBuilder);
        }
        
        private void InsertStreamRelations(TelemetryStream stream)
        {
            // todo const for table + schema
            var sqlHeader = "INSERT INTO PUBLIC.StreamRelations (StreamId, Relationship, Value) ";

            var sqlStringBuilder = new StringBuilder();

            foreach (var parent in stream.Parents)
                sqlStringBuilder.Append($"VALUES ('{stream.StreamId}', 'PARENT', '{parent}')");
            
            foreach (var child in stream.Children)
                sqlStringBuilder.Append($"VALUES ('{stream.StreamId}', 'CHILD', '{child}')");
            
            SnowflakeQuery.ExecuteSnowFlakeNonQuery(dbConnection, sqlHeader + sqlStringBuilder);
        }

        //TODO not needed for this? called from API->Patch in telemetry writer
        public Task Update(string streamId, TelemetryStream update)
        {
            throw new System.NotImplementedException();
        }

        public Task BulkWrite(IEnumerable<TelemetryStream> insertRequests)
        {
            throw new System.NotImplementedException();
        }

        public Task Delete(string streamId)
        {
            throw new System.NotImplementedException();
        }

        public Task<long> MarkDeleted(ICollection<string> streamIds, bool hardDelete)
        {
            throw new System.NotImplementedException();
        }

        public Task<long> Restore(ICollection<string> streamIds)
        {
            throw new System.NotImplementedException();
        }

        public IQueryable<TelemetryStream> GetAll()
        {
            throw new System.NotImplementedException();
        }
    }
}