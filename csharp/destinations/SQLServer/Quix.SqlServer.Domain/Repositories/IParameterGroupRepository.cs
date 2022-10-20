using System.Collections.Generic;
using System.Threading.Tasks;
using Quix.SqlServer.Domain.Common;
using Quix.SqlServer.Domain.Models;

namespace Quix.SqlServer.Domain.Repositories
{
    /// <summary>
    /// Repository for persisting new <see cref="TelemetryParameterGroup"/> and reading existing
    /// </summary>
    public interface IParameterGroupRepository
    {
        /// <summary>
        /// Gets all parameter groups as queryable for further filtering
        /// </summary>
        /// <returns>Queryable telemetry parameter groups</returns>
        Task<IList<TelemetryParameterGroup>> Get(FilterDefinition<TelemetryParameterGroup> filter);
        
        /// <summary>
        /// Bulk write capable of updating/inserting/deleting multiple things at a time
        /// </summary>
        /// <param name="requests">The request to execute</param>
        Task BulkWrite(IEnumerable<WriteModel<TelemetryParameterGroup>> requests);
    }
}