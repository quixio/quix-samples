namespace Quix.Snowflake.Domain.Common
{
    public class Builders<TModel>
    {
        public static FilterDefinitionBuilder<TModel> Filter => new FilterDefinitionBuilder<TModel>();
        
        public static UpdateDefinitionBuilder<TModel> Update => new UpdateDefinitionBuilder<TModel>();
    }
}