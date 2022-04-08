using System;
using System.Collections;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Linq.Expressions;
using System.Reflection;
using Quix.Snowflake.Domain.Common;
using Quix.Snowflake.Domain.Models;

namespace Quix.Snowflake.Infrastructure.Shared
{
    public class SnowflakeSchemaRegistry
    {
        private static bool registered = false;
        private static object registerLock = new object();
        internal static IReadOnlyDictionary<Type, SnowflakeModelSchema> Registry { get; private set; } = new Dictionary<Type, SnowflakeModelSchema>();


        public static void Register()
        {
            if (registered) return;
            lock (registerLock)
            {
                if (registered) return;
                registered = true;
            }
            
            var modelRegistrations = new List<SnowflakeModelSchemaBuilder>();

            SnowflakeSchemaRegistry.RegisterModel<TelemetryStream>(modelRegistrations)
                .SetTableName("Streams")
                .SetPrimaryKey(y => y.StreamId)
                .SetForeignTable(y => y.Metadata, "StreamMetadata", "StreamId")
                .SetForeignTable(y => y.Parents, "StreamParents", "StreamId");

            SnowflakeSchemaRegistry.RegisterModel<TelemetryEvent>(modelRegistrations)
                .SetTableName("EventDetails")
                .SetPrimaryKey(y => y.EventId);
            
            SnowflakeSchemaRegistry.RegisterModel<TelemetryParameter>(modelRegistrations)
                .SetTableName("ParameterDetails")
                .SetPrimaryKey(y => y.ParameterId);
            
            Registry = Build(modelRegistrations);
        }


        private static IReadOnlyDictionary<Type, SnowflakeModelSchema> Build(List<SnowflakeModelSchemaBuilder> snowFlakeModelRegistrationBuilders)
        {
            return new ReadOnlyDictionary<Type, SnowflakeModelSchema>(snowFlakeModelRegistrationBuilders.ToDictionary(y => y.Type, y => y.Build()));
        }
        

        private static SnowflakeModelSchemaBuilder<T> RegisterModel<T>(List<SnowflakeModelSchemaBuilder> snowFlakeModelRegistrationBuilders)
        {
            var registration = new SnowflakeModelSchemaBuilder<T>();
            snowFlakeModelRegistrationBuilders.Add(registration);
            return registration;
        }
        
        private abstract class SnowflakeModelSchemaBuilder
        {
            protected SnowflakeModelSchemaBuilder(Type type)
            {
                this.Type = type;
            }
            
            public abstract SnowflakeModelSchema Build();
            
            public Type Type { get; }
        }

        private class SnowflakeModelSchemaBuilder<T> : SnowflakeModelSchemaBuilder
        {
            private string tableName;
            private MemberInfo primaryKeyMemberInfo;
            private Dictionary<MemberInfo, SnowflakeForeignTableSchema> foreignTables = new Dictionary<MemberInfo, SnowflakeForeignTableSchema>();

            public SnowflakeModelSchemaBuilder() : base(typeof(T))
            {
                
            }

            public SnowflakeModelSchemaBuilder<T> SetPrimaryKey<TK>(Expression<Func<T, TK>> keyExpression)
            {
                var memberInfoExpression = Utils.GetMemberExpression(keyExpression);
                var type = Utils.GetMemberInfoType(memberInfoExpression.Member);
                if (type != typeof(string) && type != typeof(int) && type != typeof(long))
                {
                    throw new NotImplementedException("Primary key must be string, int or long"); // no need to implement everything for now
                }

                this.primaryKeyMemberInfo = memberInfoExpression.Member;
                return this;
            }

            public SnowflakeModelSchemaBuilder<T> SetTableName(string tableName)
            {
                this.tableName = tableName;
                return this;
            }
            
            public SnowflakeModelSchemaBuilder<T> SetForeignTable<TK>(Expression<Func<T, TK>> keyExpression, string tableName, string foreignKeyName) where TK : IEnumerable
            {
                var memberInfoExpression = Utils.GetMemberExpression(keyExpression);
                var type = Utils.GetMemberInfoType(memberInfoExpression.Member);
                if (type == typeof(string)) throw new Exception("Can't set foreign table for string");
                foreignTables[memberInfoExpression.Member] = new SnowflakeForeignTableSchema(memberInfoExpression.Member, tableName, foreignKeyName);
                return this;
            }

            public override SnowflakeModelSchema Build()
            {
                return new SnowflakeModelSchema(tableName, primaryKeyMemberInfo, foreignTables);
            }
        }
    }

    internal class SnowflakeForeignTableSchema
    {
        public SnowflakeForeignTableSchema(MemberInfo foreignMemberInfo, string foreignTableName, string keyInForeignTable)
        {
            this.ForeignMemberInfo = foreignMemberInfo;
            this.ForeignTableName = foreignTableName;
            this.KeyInForeignTable = keyInForeignTable;
            var memberType = Utils.GetMemberInfoType(foreignMemberInfo);
            if (memberType.GenericTypeArguments.Length == 1)
            {
                this.ForeignMemberType = memberType.GenericTypeArguments[0];
            } else if (memberType.GenericTypeArguments.Length == 2 && typeof(IDictionary).IsAssignableFrom(memberType))
            {
                this.ForeignMemberType = typeof(KeyValuePair<,>).MakeGenericType(new[] { memberType.GenericTypeArguments[0], memberType.GenericTypeArguments[1] });
            }
            else
            {
                throw new NotImplementedException();
                // Not sure how to handle
            }
        }

        public Type ForeignMemberType { get; }

        public object ForeignTableName { get;  }

        public MemberInfo ForeignMemberInfo { get;  }
        public string KeyInForeignTable { get; }
    }

    internal class SnowflakeModelSchema
    {
        public SnowflakeModelSchema(string tableName, MemberInfo primaryKeyMemberInfo, Dictionary<MemberInfo, SnowflakeForeignTableSchema> foreignTables)
        {
            this.TableName = tableName;
            this.PrimaryKeyMemberInfo = primaryKeyMemberInfo;
            this.ForeignTables = new ReadOnlyDictionary<MemberInfo, SnowflakeForeignTableSchema>(foreignTables);
        }

        public IReadOnlyDictionary<MemberInfo, SnowflakeForeignTableSchema> ForeignTables { get; }

        public MemberInfo PrimaryKeyMemberInfo { get; }

        public string TableName { get; }
    }
}