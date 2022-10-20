using System.Data;
using Microsoft.Extensions.Logging;
using Quix.SqlServer.Domain.Models;
using Quix.SqlServer.Domain.Repositories;
using Quix.SqlServer.Infrastructure.Shared;

namespace Quix.SqlServer.Infrastructure.Metadata
{
    public class StreamRepository : SqlServerRepository<TelemetryStream>, IStreamRepository
    {

        public StreamRepository(IDbConnection databaseConnection, ILoggerFactory loggerFactory) : base(databaseConnection, loggerFactory.CreateLogger<StreamRepository>())
        {
        }
    }
}