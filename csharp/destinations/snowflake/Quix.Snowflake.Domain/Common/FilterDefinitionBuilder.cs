using System;
using System.Linq.Expressions;

namespace Quix.Snowflake.Domain.Common
{
    public class FilterDefinitionBuilder<TModel>
    {
        public EqFilterDefinition<TModel, TModelValue> Eq<TModelValue>(Expression<Func<TModel, TModelValue>> selector, TModelValue value)
        {
            return new EqFilterDefinition<TModel, TModelValue>(selector, value);
        }

        public FilterDefinition<TModel> And(params FilterDefinition<TModel>[] filterDefinitions)
        {
            return new AndFilterDefinition<TModel>
            {
                FilterDefinitions = filterDefinitions
            };
        }
    }
}