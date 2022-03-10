using Xamarin.Forms;
using Xamarin.Forms.Xaml;

namespace QuixTracker.Controls
{
    [XamlCompilation(XamlCompilationOptions.Compile)]
    public partial class DashboardItem : ContentView
    {
        public string Name
        {
            get
            {
                return (string)GetValue(NameProperty);
            }
            set
            {
                SetValue(NameProperty, value);
            }
        }

        public static readonly BindableProperty NameProperty =
           BindableProperty.Create(nameof(Name), typeof(string), typeof(DashboardItem), "N/A");
        
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
           BindableProperty.Create(nameof(Value), typeof(string), typeof(DashboardItem), "N/A");


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