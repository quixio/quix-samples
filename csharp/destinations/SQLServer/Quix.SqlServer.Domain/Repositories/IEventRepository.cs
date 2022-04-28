using System.Collections.Generic;
using System.Threading.Tasks;
using Quix.SqlServer.Domain.Common;
using Quix.SqlServer.Domain.Models;

namespace Quix.SqlServer.Domain.Repositories
{
    /// <summary>
    /// Repository for persisting new <see cref="TelemetryEvent"/> and reading existing
    /// </summary>
    public interface IEventRepository
    {
        /// <summary>
        /// Gets all events as queryable for further filtering
        /// </summary>
        /// <returns>Queryable telemetry events</returns>
        Task<IList<TelemetryEvent>> Get(FilterDefinition<TelemetryEvent> filter);
        
        /// <summary>
        /// Bulk write capable of updating/inserting/deleting multiple things at a time
        /// </summary>
        /// <param name="requests">The request to execute</param>
        Task BulkWrite(IEnumerable<WriteModel<TelemetryEvent>> requests);
    }
}