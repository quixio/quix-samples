using QuixTracker.Models;
using QuixTracker.Services;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

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
        private string bufferSize;
        private string altitude;
        private string bearing;
        private string message;
        private bool connecting;
        private bool draining;
        private bool disconnected = true;
        private string heartRate;

        public bool Connected
        {
            get { return connected; }
            set
            {
                connected = value;
                this.OnPropertyChanged();
            }
        }

        public bool Connecting
        {
            get { return connecting; }
            set
            {
                connecting = value;
                this.OnPropertyChanged();
            }
        }

        public bool Disconnected
        {
            get { return disconnected; }
            set
            {
                disconnected = value;
                this.OnPropertyChanged();
            }
        }

        public bool Draining
        {
            get { return draining; }
            set
            {
                draining = value;
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

        public string BufferSize
        {
            get { return bufferSize; }
            set
            {
                bufferSize = value;
                this.OnPropertyChanged();
            }
        }

        public string Altitude
        {
            get { return altitude; }
            set
            {
                altitude = value;
                this.OnPropertyChanged();
            }
        }

        public string Bearing
        {
            get { return bearing; }
            set
            {
                bearing = value;
                this.OnPropertyChanged();
            }
        }

        public string Message
        {
            get { return message; }
            set
            {
                message = value;
                this.OnPropertyChanged();
            }
        }

        public string HeartRate
        {
            get { return heartRate; }
            set
            {
                heartRate = value;
                this.OnPropertyChanged();
            }
        }

        public Dashboard()
        {

            InitializeComponent();

            BindingContext = this;

            this.connectionService = ConnectionService.Instance;

            this.connectionService.OutputConnectionChanged += ConnectionService_OutputConnectionChanged;
            this.connectionService.ConnectionError += ConnectionService_ConnectionError;

            this.connectionService.DataReceived += ConnectionService_DataReceived;

            this.ConnectionService_OutputConnectionChanged(this, this.connectionService.OutputConnectionState);

        }

        private void ConnectionService_DataReceived(object sender, CurrentData e)
        {
            this.Speed = ((int)e.Speed).ToString();
            this.Accuracy = ((int)e.Accuracy).ToString();
            this.BufferSize = e.LocationBufferSize.ToString();
            this.Bearing = e.Bearing.ToString("0.00");
            this.Altitude = e.Altitude.ToString("0.00");
            this.Message = e.Message;
            this.HeartRate = e.Heartrate.ToString();
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
                    this.Connecting = false;
                    this.Draining = false;
                    this.Disconnected = false;
                    break;
                case ConnectionState.Connecting:
                    this.Reconnecting = false;
                    this.Connected = false;
                    this.Connecting = true;
                    this.Draining = false;
                    this.Disconnected = false;

                    break;
                case ConnectionState.Reconnecting:
                    this.Reconnecting = true;
                    this.Connected = false;
                    this.Connecting = false;
                    this.Draining = false;
                    this.Disconnected = false;


                    break;
                case ConnectionState.Disconnected:
                    this.Connected = false;
                    this.Reconnecting = false;
                    this.Connecting = false;
                    this.Draining = false;
                    this.Disconnected = true;

                    break;
                case ConnectionState.Draining:
                    this.Connected = false;
                    this.Reconnecting = false;
                    this.Connecting = false;
                    this.Draining = true;
                    this.Disconnected = false;
                    break;
            }
        }

        private void OnButtonClicked(object sender, EventArgs e)
        {
            DependencyService.Get<IStartService>().StartForegroundServiceCompat();
        }

        private void OnStopClicked(object sender, EventArgs e)
        {
            DependencyService.Get<IStartService>().StopForegroundServiceCompat();
        }
    }
}