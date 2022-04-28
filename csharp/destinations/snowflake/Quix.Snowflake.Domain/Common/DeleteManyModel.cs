namespace Quix.Snowflake.Domain.Common
{
    public class DeleteManyModel<TModel> : WriteModel<TModel>
    {
        public readonly FilterDefinition<TModel> Filter;

        public DeleteManyModel(FilterDefinition<TModel> filter)
        {
            this.Filter = filter;
        }
    }
}