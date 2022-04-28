using System.Collections.Generic;

namespace Quix.Snowflake.Domain.Common
{
    public class AndFilterDefinition<TModel> : FilterDefinition<TModel>
    {
        public IEnumerable<FilterDefinition<TModel>> FilterDefinitions { get; set; }
    }
}