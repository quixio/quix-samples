namespace Quix.Snowflake.Domain.Common
{
    public class DeleteOneModel<TModel> : WriteModel<TModel>
    {
        public readonly FilterDefinition<TModel> Filter;

        public DeleteOneModel(FilterDefinition<TModel> filter)
        {
            this.Filter = filter;
        }
    }
}