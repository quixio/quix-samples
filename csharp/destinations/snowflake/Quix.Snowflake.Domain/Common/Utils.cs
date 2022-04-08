using System;
using System.Linq.Expressions;
using System.Reflection;

namespace Quix.Snowflake.Domain.Common
{
    public class Utils
    {
        public static MemberExpression GetMemberExpression(Expression expression)
        {
            if (expression.NodeType != ExpressionType.Lambda) throw new NotImplementedException("Lambda expression expected");
            var lambdaExpression = (LambdaExpression)expression;
            if (lambdaExpression.Body.NodeType != ExpressionType.MemberAccess) throw new NotImplementedException("Member expression expected");
            var memberExpression = (MemberExpression)lambdaExpression.Body;
            return memberExpression;
        }
        public static Type GetMemberInfoType(MemberInfo member)
        {
            switch (member.MemberType)
            {
                case MemberTypes.Field:
                    return ((FieldInfo)member).FieldType;
                case MemberTypes.Property:
                    return ((PropertyInfo)member).PropertyType;
                case MemberTypes.TypeInfo:
                    return ((TypeInfo)member).UnderlyingSystemType;
                default:
                    throw new ArgumentException();
            }
        }

        public static string UnPluralize(string plural)
        {
            if (!plural.EndsWith("s")) return plural;
            return plural.Substring(0, plural.Length - 1);
        }
    }
}