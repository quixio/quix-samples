using System.Data;
using Microsoft.Extensions.Logging;
using Quix.Snowflake.Domain.Models;
using Quix.Snowflake.Domain.Repositories;
using Quix.Snowflake.Infrastructure.Shared;

namespace Quix.Snowflake.Infrastructure.Metadata
{
    public class EventGroupRepository : SnowflakeRepository<TelemetryEventGroup>, IEventGroupRepository
    {
        public EventGroupRepository(IDbConnection snowflakeDbConnection, ILoggerFactory loggerFactory) : base(snowflakeDbConnection, loggerFactory.CreateLogger<EventGroupRepository>())
        {
        }
    }
}