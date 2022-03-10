using QuixTracker.Services;
using System;
using System.Diagnostics;
using System.Globalization;
using Xamarin.Forms;
using Xamarin.Forms.Xaml;

namespace QuixTracker.Views
{
    [XamlCompilation(XamlCompilationOptions.Compile)]
    public partial class Dashboard : ContentPage
    {
        private bool reconnectingWebSocket;
        private bool connected = false;
        private bool reconnecting;
        private string errorMessage;
        private ConnectionService connectionService;
        private CurrentData currentData;
        private string speed;
        private string accuracy;

        public bool Connected
        {
            get { return connected; }
            set
            {
                connected = value;
                this.OnPropertyChanged();
            }
        }

        public bool Reconnecting
        {
            get { return reconnecting; }
            set
            {
                reconnecting = value;
                this.OnPropertyChanged();
            }
        }

        public bool ReconnectingWebSocket
        {
            get { return reconnectingWebSocket; }
            set
            {
                reconnectingWebSocket = value;
                this.OnPropertyChanged();
            }
        }
        
        public string ErrorMessage
        {
            get { return errorMessage; }
            set
            {
                errorMessage = value;
                this.OnPropertyChanged();
            }
        }
        public string Speed
        {
            get { return speed; }
            set
            {
                speed = value;
                this.OnPropertyChanged();
            }
        }

        public string Accuracy
        {
            get { return accuracy; }
            set
            {
                accuracy = value;
                this.OnPropertyChanged();
            }
        }

        public Dashboard()
        {
            InitializeComponent();

            this.connectionService = ConnectionService.Instance;

            this.connectionService.OutputConnectionChanged += ConnectionService_OutputConnectionChanged;
            this.connectionService.ConnectionError += ConnectionService_ConnectionError;
            this.connectionService.DataReceived += ConnectionService_DataReceived;
            
            BindingContext = this;

        }

        private void ConnectionService_DataReceived(object sender, CurrentData e)
        {
            Debug.WriteLine(e.Accuracy.ToString(CultureInfo.InvariantCulture));

            this.Speed = ((int)e.Speed).ToString();
            this.Accuracy = ((int)e.Accuracy).ToString();
        }

        private void ConnectionService_ConnectionError(object sender, string e)
        {
            this.ErrorMessage = e;
        }

        private void ConnectionService_OutputConnectionChanged(object sender, ConnectionState e)
        {
            switch (e)
            {
                case ConnectionState.Connected: 
                    this.Reconnecting = false;
                    this.Connected = true;
                    break;
                case ConnectionState.Reconnecting:
                    this.Reconnecting = true;
                    this.Connected = false;
                    break;
                case ConnectionState.Disconnected:
                    this.Connected = false;
                    this.Reconnecting = false;
                    break;
            }
        }

        private void OnButtonClicked(object sender, EventArgs e)
        {
            Start();
        }
        
        private void OnStopClicked(object sender, EventArgs e)
        {
            Stop();
        }

        private void Stop()
        {
            DependencyService.Get<IStartService>().StopForegroundServiceCompat();
        }
        
        private void Start()
        {
            DependencyService.Get<IStartService>().StartForegroundServiceCompat();
        }
    }
}