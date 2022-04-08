namespace Quix.Snowflake.Domain.Common
{
    public class UpdateOneModel<TModel> : WriteModel<TModel>
    {
        public readonly FilterDefinition<TModel> Filter;
        public readonly UpdateDefinition<TModel> Update;

        public UpdateOneModel(FilterDefinition<TModel> filter, UpdateDefinition<TModel> update)
        {
            this.Filter = filter;
            this.Update = update;
        }
    }
}