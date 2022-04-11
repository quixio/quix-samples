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
            var body = lambdaExpression.Body;
            if (body is UnaryExpression unaryExpression)
            {
                body = unaryExpression.Operand;
            }
            
            if (body.NodeType != ExpressionType.MemberAccess) throw new NotImplementedException("Member expression expected");
            var memberExpression = (MemberExpression)body;
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

        public static object GetFieldOrPropValue(MemberInfo member, object instance)
        {
            return member.MemberType == MemberTypes.Field
                ? ((FieldInfo)member).GetValue(instance)
                : ((PropertyInfo)member).GetValue(instance);
        }
        
        public static void SetFieldOrPropValue(MemberInfo member, object instance, object value)
        {
            if (member.MemberType == MemberTypes.Field)
            {
                var field = (FieldInfo)member;
                field.SetValue(instance, value);
            }
            else
            {
                var property = ((PropertyInfo)member);
                if (property.CanWrite) property.SetValue(instance, value);
            }
        }

        public static string UnPluralize(string plural)
        {
            if (plural.EndsWith("s", StringComparison.CurrentCultureIgnoreCase)) return plural.Substring(0, plural.Length - 1);
            if (plural.EndsWith("s\"", StringComparison.CurrentCultureIgnoreCase)) return plural.Substring(0, plural.Length - 2) + "\"";
            return plural;
        }
    }
}