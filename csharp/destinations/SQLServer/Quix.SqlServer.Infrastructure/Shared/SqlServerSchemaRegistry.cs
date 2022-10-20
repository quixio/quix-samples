using System;
using System.Collections;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Linq.Expressions;
using System.Reflection;
using Quix.SqlServer.Domain.Common;
using Quix.SqlServer.Domain.Models;

namespace Quix.SqlServer.Infrastructure.Shared
{
    public class SqlServerSchemaRegistry
    {
        private static bool registered = false;
        private static object registerLock = new object();
        internal static IReadOnlyDictionary<Type, SqlServerModelSchema> Registry { get; private set; } = new Dictionary<Type, SqlServerModelSchema>();


        public static void Register()
        {
            if (registered) return;
            lock (registerLock)
            {
                if (registered) return;
                registered = true;
            }
            
            var modelRegistrations = new List<SqlServerModelSchemaBuilder>();

            SqlServerSchemaRegistry.RegisterModel<TelemetryStream>(modelRegistrations)
                .SetTableName("Streams")
                .SetPrimaryKey(y => y.StreamId)
                .SetForeignTable(y => y.Metadata, "StreamMetadata", "StreamId")
                .SetForeignTable(y => y.Parents, "StreamParents", "StreamId");

            SqlServerSchemaRegistry.RegisterModel<TelemetryEvent>(modelRegistrations)
                .SetTableName("EventDetails")
                .SetPrimaryKey(y => y.ObjectId)
                .SetClusterKey(y => y.StreamId);
            
            SqlServerSchemaRegistry.RegisterModel<TelemetryParameter>(modelRegistrations)
                .SetTableName("ParameterDetails")
                .SetPrimaryKey(y => y.ObjectId)
                .SetClusterKey(y => y.StreamId);
            
            SqlServerSchemaRegistry.RegisterModel<TelemetryEventGroup>(modelRegistrations)
                .SetTableName("EventGroupDetails")
                .SetPrimaryKey(y => y.ObjectId)
                .SetClusterKey(y => y.StreamId);

            SqlServerSchemaRegistry.RegisterModel<TelemetryParameterGroup>(modelRegistrations)
                .SetTableName("ParameterGroupDetails")
                .SetPrimaryKey(y => y.ObjectId)
                .SetClusterKey(y => y.StreamId);
            
            Registry = Build(modelRegistrations);
        }


        private static IReadOnlyDictionary<Type, SqlServerModelSchema> Build(List<SqlServerModelSchemaBuilder> SqlServerModelRegistrationBuilders)
        {
            return new ReadOnlyDictionary<Type, SqlServerModelSchema>(SqlServerModelRegistrationBuilders.ToDictionary(y => y.Type, y => y.Build()));
        }
        

        private static SqlServerModelSchemaBuilder<T> RegisterModel<T>(List<SqlServerModelSchemaBuilder> SqlServerModelRegistrationBuilders)
        {
            var registration = new SqlServerModelSchemaBuilder<T>();
            SqlServerModelRegistrationBuilders.Add(registration);
            return registration;
        }
        
        private abstract class SqlServerModelSchemaBuilder
        {
            protected SqlServerModelSchemaBuilder(Type type)
            {
                this.Type = type;
            }
            
            public abstract SqlServerModelSchema Build();
            
            public Type Type { get; }
        }

        private class SqlServerModelSchemaBuilder<T> : SqlServerModelSchemaBuilder
        {
            private string tableName;
            private MemberInfo primaryKeyMemberInfo;
            private Dictionary<MemberInfo, SqlServerForeignTableSchema> foreignTables = new Dictionary<MemberInfo, SqlServerForeignTableSchema>();
            private MemberInfo clusterKeyInfo;

            public SqlServerModelSchemaBuilder() : base(typeof(T))
            {
                
            }

            public SqlServerModelSchemaBuilder<T> SetPrimaryKey<TK>(Expression<Func<T, TK>> keyExpression)
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
            
            public SqlServerModelSchemaBuilder<T> SetClusterKey<TK>(Expression<Func<T, TK>> keyExpression)
            {
                var memberInfoExpression = Utils.GetMemberExpression(keyExpression);
                var type = Utils.GetMemberInfoType(memberInfoExpression.Member);
                if (type != typeof(string) && type != typeof(int) && type != typeof(long))
                {
                    throw new NotImplementedException("Cluster key key must be string, int or long"); // no need to implement everything for now
                }

                this.clusterKeyInfo = memberInfoExpression.Member;
                return this;
            }

            public SqlServerModelSchemaBuilder<T> SetTableName(string tableName)
            {
                this.tableName = tableName;
                return this;
            }
            
            public SqlServerModelSchemaBuilder<T> SetForeignTable<TK>(Expression<Func<T, TK>> keyExpression, string tableName, string foreignKeyName) where TK : IEnumerable
            {
                var memberInfoExpression = Utils.GetMemberExpression(keyExpression);
                var type = Utils.GetMemberInfoType(memberInfoExpression.Member);
                if (type == typeof(string)) throw new Exception("Can't set foreign table for string");
                foreignTables[memberInfoExpression.Member] = new SqlServerForeignTableSchema(memberInfoExpression.Member, tableName, foreignKeyName);
                return this;
            }

            public override SqlServerModelSchema Build()
            {
                return new SqlServerModelSchema(tableName, primaryKeyMemberInfo, clusterKeyInfo, foreignTables);
            }
        }
    }

    internal class SqlServerForeignTableSchema
    {
        public SqlServerForeignTableSchema(MemberInfo foreignMemberInfo, string foreignTableName, string keyInForeignTable)
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

            if (this.ForeignMemberType.IsPrimitive || this.ForeignMemberType == typeof(string))
            {
                this.ColumnMemberInfos = null;
            }
            else
            {
                var propertiesOrFields = this.ForeignMemberType.GetMembers(BindingFlags.Public | BindingFlags.Instance)
                    .Where(y => y.MemberType == MemberTypes.Field || y.MemberType == MemberTypes.Property).ToList();
                if (propertiesOrFields.Any(y =>
                    {
                        var type = Utils.GetMemberInfoType(y);
                        return typeof(IEnumerable).IsAssignableFrom(type) && typeof(string) != type;
                    })) throw new Exception("Foreign table to a foreign table is not supported");
                this.ColumnMemberInfos = propertiesOrFields;
            }
        }

        public IReadOnlyList<MemberInfo> ColumnMemberInfos { get; }

        public Type ForeignMemberType { get; }

        public string ForeignTableName { get;  }

        public MemberInfo ForeignMemberInfo { get;  }
        public string KeyInForeignTable { get; }
    }

    internal class SqlServerModelSchema
    {
        public SqlServerModelSchema(string tableName, MemberInfo primaryKeyMemberInfo, MemberInfo clusterKeyInfo, Dictionary<MemberInfo, SqlServerForeignTableSchema> foreignTables)
        {
            this.TableName = tableName;
            this.PrimaryKeyMemberInfo = primaryKeyMemberInfo;
            this.ClusterKeyMemberInfo = clusterKeyInfo;
            this.ForeignTables = new ReadOnlyDictionary<MemberInfo, SqlServerForeignTableSchema>(foreignTables);
            var propertiesOrFields = primaryKeyMemberInfo.DeclaringType.GetMembers(BindingFlags.Public | BindingFlags.Instance).Where(y=> y.MemberType == MemberTypes.Field || y.MemberType == MemberTypes.Property).Except(foreignTables.Keys).ToList();
            this.ColumnMemberInfos = propertiesOrFields;
            this.TypeMapFrom = new Dictionary<MemberInfo, Dictionary<object, object>>();

            foreach (var @enum in this.ColumnMemberInfos.Where(y => typeof(Enum).IsAssignableFrom(Utils.GetMemberInfoType(y))))
            {
                var map = new Dictionary<object, object>();
                foreach (var value in Enum.GetValues(Utils.GetMemberInfoType(@enum)))
                {
                    map[value.ToString()] = value;
                }

                this.TypeMapFrom[@enum] = map;
            }
        }

        /// <summary>
        /// The map to convert back from SqlServer result to dotnet value. Used primarily for enums at the moment
        /// </summary>
        public Dictionary<MemberInfo, Dictionary<object, object>> TypeMapFrom { get; set; }

        public MemberInfo ClusterKeyMemberInfo { get; }

        public IReadOnlyList<MemberInfo> ColumnMemberInfos { get; }

        public IReadOnlyDictionary<MemberInfo, SqlServerForeignTableSchema> ForeignTables { get; }

        public MemberInfo PrimaryKeyMemberInfo { get; }

        public string TableName { get; }
    }
}