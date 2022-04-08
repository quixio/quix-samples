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
            // assuming shape of table is known
            
            StringBuilder sqlStringBuilder = new StringBuilder();
            sqlStringBuilder.Append($"INSERT INTO PUBLIC.Streams (Id, Name, Topic) ");
            sqlStringBuilder.Append($"VALUES ('{stream.StreamId}', '{stream.Name}', '{stream.Topic}')");
            
            
            SnowflakeQuery.ExecuteSnowFlakeNonQuery(dbConnection, "");
            
            
            return Task.CompletedTask;
        }

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