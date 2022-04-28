using System.Collections.Generic;

namespace Quix.Snowflake.Domain.Common
{
    public class MultipleUpdateDefinition<TModel> : UpdateDefinition<TModel>
    {
        public IEnumerable<UpdateDefinition<TModel>> UpdateDefinitions { get; set; }
    }
}