using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq.Expressions;

namespace Quix.Snowflake.Domain.Common
{
    public abstract class InFilterDefinition<TModel> : FilterDefinition<TModel>
    {
        protected InFilterDefinition(Expression selector, IEnumerable values, Type valueType)
        {
            this.Selector = selector;
            this.Values = values;
            this.Type = valueType;
        }

        public Type Type { get; }

        public Expression Selector { get; }

        public IEnumerable Values { get; }
    }

    public class InFilterDefinition<TModel, TModelValue> : InFilterDefinition<TModel>
    {
        public InFilterDefinition(Expression<Func<TModel, TModelValue>> selector, ICollection<TModelValue> values) : base(selector, values, typeof(TModelValue))
        {
            this.Selector = selector;
            this.Values = values;
        }

        public Expression<Func<TModel, TModelValue>> Selector { get; }

        public ICollection<TModelValue> Values { get; }
    }
}