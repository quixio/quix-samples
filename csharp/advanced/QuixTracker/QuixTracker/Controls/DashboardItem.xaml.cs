using Xamarin.Forms;
using Xamarin.Forms.Xaml;

namespace QuixTracker.Controls
{
    [XamlCompilation(XamlCompilationOptions.Compile)]
    public partial class DashboardItem : ContentView
    {
        public string Title
        {
            get
            {
                return (string)GetValue(TitleProperty);
            }
            set
            {
                SetValue(TitleProperty, value);
            }
        }

        public static readonly BindableProperty TitleProperty =
           BindableProperty.Create(nameof(Title), typeof(string), typeof(DashboardItem), "");


        public string Value
        {
            get
            {
                return (string)GetValue(ValueProperty);
            }
            set
            {
                SetValue(ValueProperty, value);
            }
        }

        public static readonly BindableProperty ValueProperty =
           BindableProperty.Create(nameof(Value), typeof(string), typeof(DashboardItem), "");


        public double ValueScale
        {
            get
            {
                return (double)GetValue(ValueScaleProperty);
            }
            set
            {
                SetValue(ValueScaleProperty, value);
            }
        }

        public static readonly BindableProperty ValueScaleProperty =
           BindableProperty.Create(nameof(ValueScale), typeof(double), typeof(DashboardItem), 1.0);

        public DashboardItem()
        {
            InitializeComponent();

            this.Root.BindingContext = this;
        }
    }
}