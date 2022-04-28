using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using Quix.Snowflake.Domain.Models;
using Quix.Snowflake.Domain.Repositories;
using Quix.Snowflake.Infrastructure.Shared;

namespace Quix.Snowflake.Infrastructure.Metadata
{
    public class ParameterRepository : SnowflakeRepository<TelemetryParameter>, IParameterRepository
    {
        public ParameterRepository(IDbConnection databaseConnection, ILoggerFactory loggerFactory) : base(databaseConnection, loggerFactory.CreateLogger<ParameterRepository>())
        {
        }
    }
}