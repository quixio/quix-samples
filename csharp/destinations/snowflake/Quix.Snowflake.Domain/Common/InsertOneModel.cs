namespace Quix.Snowflake.Domain.Common
{
    public class InsertOneModel<TModel> : WriteModel<TModel>
    {
        public InsertOneModel(TModel model)
        {
            this.Model = model;
        }

        public TModel Model { get; }
    }
}