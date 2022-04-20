namespace Quix.Snowflake.Domain.Common
{
    public class NotFilterDefinition<TModel> : FilterDefinition<TModel>
    {
        public readonly FilterDefinition<TModel> Filter;

        public NotFilterDefinition(FilterDefinition<TModel> filter)
        {
            this.Filter = filter;
        }
    }
}