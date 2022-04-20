using System;
using System.Collections.Generic;
using System.Linq.Expressions;

namespace Quix.Snowflake.Domain.Common
{
    public class UpdateDefinitionBuilder<TModel>
    {
        public SetUpdateDefinition<TModel,TModelValue> Set<TModelValue>(Expression<Func<TModel, TModelValue>> selector, TModelValue value)
        {
            return new SetUpdateDefinition<TModel, TModelValue>(selector, value);
        }
        
        public MultipleUpdateDefinition<TModel> Combine(IEnumerable<UpdateDefinition<TModel>> definitions)
        {
            return new MultipleUpdateDefinition<TModel>()
            {
                UpdateDefinitions = definitions
            };
        }
        
        public MultipleUpdateDefinition<TModel> Combine(params UpdateDefinition<TModel>[] definitions)
        {
            return new MultipleUpdateDefinition<TModel>()
            {
                UpdateDefinitions = definitions
            };
        }
    }
}