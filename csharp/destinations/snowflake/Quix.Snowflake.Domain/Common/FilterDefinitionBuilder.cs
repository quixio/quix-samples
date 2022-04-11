using System;
using System.Collections.Generic;
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

        public FilterDefinition<TModel> In<TModelValue>(Expression<Func<TModel, TModelValue>> selector, ICollection<TModelValue> values)
        {
            return new InFilterDefinition<TModel, TModelValue>(selector, values);
        }
        
        public FilterDefinition<TModel> Not(FilterDefinition<TModel> filter)
        {
            return new NotFilterDefinition<TModel>(filter);
        }
    }

    public static class FilterDefinitionBuildExtensions
    {
        public static FilterDefinition<TModel> And<TModel>(this FilterDefinition<TModel> definition, FilterDefinition<TModel> otherDefinition)
        {
            return Builders<TModel>.Filter.And(definition, otherDefinition);
        } 
        public static FilterDefinition<TModel> Not<TModel>(this FilterDefinition<TModel> definition)
        {
            return Builders<TModel>.Filter.Not(definition);
        } 
    }
}