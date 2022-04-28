using System.Collections.Generic;

namespace Quix.SqlServer.Domain.Common
{
    public class AndFilterDefinition<TModel> : FilterDefinition<TModel>
    {
        public IEnumerable<FilterDefinition<TModel>> FilterDefinitions { get; set; }
    }
}