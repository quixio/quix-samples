using System;
using System.Globalization;
using System.Linq;
using Xamarin.Forms;

namespace QuixTracker
{
    public class LogicalConverter : IMultiValueConverter
    {
        public object Convert(object[] values, Type targetType, object parameter, CultureInfo culture)
        {
            if (parameter.ToString() == "AND")
            {
                return values.All(x => x != null && (bool)x);
            }
            else
            {
                return values.Any(x => x != null && (bool)x);
            }
        }

        public object[] ConvertBack(object value, Type[] targetTypes, object parameter, CultureInfo culture)
        {
            throw new NotImplementedException();
        }
    }
}
