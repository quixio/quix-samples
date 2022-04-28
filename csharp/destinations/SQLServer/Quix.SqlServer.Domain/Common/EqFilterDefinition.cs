using System;
using System.Linq.Expressions;

namespace Quix.Snowflake.Domain.Common
{
    public class EqFilterDefinition<TModel, TModelValue> : EqFilterDefinition<TModel>
    {
        public EqFilterDefinition(Expression<Func<TModel, TModelValue>> selector, TModelValue value) : base(selector, value, typeof(TModelValue))
        {
            this.Selector = selector;
            this.Value = value;
        }

        public Expression<Func<TModel, TModelValue>> Selector { get; }

        public TModelValue Value { get; }
    }

    public abstract class EqFilterDefinition<TModel> : FilterDefinition<TModel>
    {
        protected EqFilterDefinition(Expression selector, object value, Type valueType)
        {
            this.Selector = selector;
            this.Value = value;
            this.Type = valueType;
        }

        public Type Type { get; }

        public Expression Selector { get; }

        public object Value { get; }
    }
}