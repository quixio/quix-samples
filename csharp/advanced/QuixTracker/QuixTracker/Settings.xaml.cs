using QuixTracker.Services;
using Xamarin.Forms;
using Xamarin.Forms.Xaml;

namespace QuixTracker
{
    [XamlCompilation(XamlCompilationOptions.Compile)]
    public partial class Settings : ContentPage
    {
        private string deviceId;

        private string interval = "250";
        private string rider;
        private string team;
        private bool logGForce;
        private string sessionName;
        private ConnectionService connectionService;

        public string SessionName
        {
            get { return sessionName; }
            set
            {
                sessionName = value;
                this.OnPropertyChanged();
                connectionService.Settings.SessionName = value;
            }
        }

        public string DeviceId
        {
            get { return deviceId; }
            set
            {
                deviceId = value;
                this.OnPropertyChanged();
                connectionService.Settings.DeviceId = value;
            }
        }

        public string Rider
        {
            get { return rider; }
            set
            {
                rider = value;
                this.OnPropertyChanged();
                connectionService.Settings.Rider = value;
            }
        }

        public string Team
        {
            get { return team; }
            set
            {
                team = value;
                this.OnPropertyChanged();
                connectionService.Settings.Team = value;
            }
        }

        public string Interval
        {
            get { return interval; }
            set
            {
                interval = value;
                this.OnPropertyChanged();
                connectionService.Settings.Interval = int.Parse(value);
            }
        }

        public bool LogGForce
        {
            get { return logGForce; }
            set
            {
                logGForce = value;
                this.OnPropertyChanged();
                connectionService.Settings.LogGForce = value;
            }
        }

        public Settings()
        {
            InitializeComponent();

            this.connectionService = ConnectionService.Instance;
            this.SessionName = connectionService.Settings.SessionName;
            this.DeviceId = connectionService.Settings.DeviceId;
            this.Rider = connectionService.Settings.Rider;
            this.Team = connectionService.Settings.Team;
            this.LogGForce = connectionService.Settings.LogGForce;
            this.Interval = connectionService.Settings.Interval.ToString();

            BindingContext = this;

        }
    }
}