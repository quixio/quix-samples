using System.Collections.Generic;
using System.Threading.Tasks;
using Quix.SqlServer.Domain.Common;
using Quix.SqlServer.Domain.Models;

namespace Quix.SqlServer.Domain.Repositories
{
    /// <summary>
    /// Repository for persisting new <see cref="TelemetryParameter"/> and reading existing
    /// </summary>
    public interface IParameterRepository
    {
        Task<IList<TelemetryParameter>> Get(FilterDefinition<TelemetryParameter> filter);
        
        /// <summary>
        /// Bulk write capable of updating/inserting/deleting multiple things at a time
        /// </summary>
        /// <param name="requests">The request to execute</param>
        Task BulkWrite(IEnumerable<WriteModel<TelemetryParameter>> requests);
    }
}