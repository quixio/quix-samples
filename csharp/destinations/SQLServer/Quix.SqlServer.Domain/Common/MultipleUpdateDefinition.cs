using System.Collections.Generic;

namespace Quix.SqlServer.Domain.Common
{
    public class MultipleUpdateDefinition<TModel> : UpdateDefinition<TModel>
    {
        public IEnumerable<UpdateDefinition<TModel>> UpdateDefinitions { get; set; }
    }
}