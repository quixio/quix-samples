namespace Quix.Snowflake.Domain.Common
{
    public class UpdateOneModel<TModel> : WriteModel<TModel>
    {
        public readonly TModel ModelToUpdate;
        public readonly UpdateDefinition<TModel> Update;

        public UpdateOneModel(TModel modelToUpdate, UpdateDefinition<TModel> update)
        {
            ModelToUpdate = modelToUpdate;
            this.Update = update;
        }
    }
}