using System.Data;
using Microsoft.Extensions.Logging;
using Quix.SqlServer.Domain.Models;
using Quix.SqlServer.Domain.Repositories;
using Quix.SqlServer.Infrastructure.Shared;

namespace Quix.SqlServer.Infrastructure.Metadata
{
    public class EventGroupRepository : SqlServerRepository<TelemetryEventGroup>, IEventGroupRepository
    {
        public EventGroupRepository(IDbConnection databaseConnection, ILoggerFactory loggerFactory) : base(databaseConnection, loggerFactory.CreateLogger<EventGroupRepository>())
        {
        }
    }
}