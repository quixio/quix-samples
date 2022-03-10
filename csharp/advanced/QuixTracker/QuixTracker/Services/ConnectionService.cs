using System;
using System.Diagnostics;
using Xamarin.Essentials;

namespace QuixTracker.Services
{
    public enum ConnectionState
    {
        Disconnected,
        Reconnecting,
        Connecting,
        Connected,
    }

    public class CurrentData
    {
        public double Speed { get; set; }

        public double Accuracy { get; set; }
    }

    public class Settings
    {
        private string deviceId;

        private int interval = 250;
        private string rider;
        private string team;
        private bool logGForce;
        private string sessionName;
        private string workspaceId;
        private string subDomain;
        private string token;
        private string topic;
        
        public Settings()
        {
            this.SessionName = Preferences.Get("SessionName", $"Session on {DateTime.Now:yyyy-M-dd h:mm:ss}"); 
            this.DeviceId = Preferences.Get("DeviceId", "My Device");
            this.Rider = Preferences.Get("Rider", "My Name");
            this.Team = Preferences.Get("Team", "My Team");
            this.Interval = Preferences.Get("Interval", 250);
            this.LogGForce = Preferences.Get("LogGForce", true);

            // these will be populated by Quix when you save the project to your workspace.
            this.workspaceId = "{placeholder:workspaceId}";
            this.subDomain = "{placeholder:environment.subdomain}";
            this.token = "{placeholder:token}";
            this.topic = "{placeholder:topic}";

            // debug values
            // this.token = "";
            // this.workspaceId = "";
            // this.subDomain = "dev";
            // this.topic = "phone";
        }

        public string WorkspaceId => workspaceId;
        public string SubDomain => subDomain;
        public string Token => token;
        public string Topic => topic;

        public string SessionName
        {
            get { return sessionName; }
            set
            {
                sessionName = value;
                Preferences.Set("SessionName", value);
            }
        }

        public string DeviceId
        {
            get { return deviceId; }
            set
            {
                deviceId = value;
                Preferences.Set("DeviceId", value);
            }
        }

        public string Rider
        {
            get { return rider; }
            set
            {
                rider = value;
                Preferences.Set("Rider", value);
            }
        }

        public string Team
        {
            get { return team; }
            set
            {
                team = value;
                Preferences.Set("Team", value);
            }
        }

        public int Interval
        {
            get { return interval; }
            set
            {
                interval = value;
                Preferences.Set("Interval", value);
            }
        }

        public bool LogGForce
        {
            get { return logGForce; }
            set
            {
                logGForce = value;
                Preferences.Set("logGForce", value);
            }
        }
    }

    public class ConnectionService
    {
        private static ConnectionService instance;

        public static ConnectionService Instance
        {
            get
            {
                if (instance == null)
                {
                    instance = new ConnectionService();
                }

                return instance;
            }
        }

        public Settings Settings { get; private set; }

        public event EventHandler<ConnectionState> InputConnectionChanged;
        public event EventHandler<ConnectionState> OutputConnectionChanged;
        public event EventHandler<string> ConnectionError;
        public event EventHandler<CurrentData> DataReceived;

        public ConnectionService()
        {
            this.Settings = new Settings();
        }

        public void OnDataReceived(CurrentData data)
        {
            DataReceived?.Invoke(this, data);
        }

        public void OnInputConnectionChanged(ConnectionState newState)
        {
            InputConnectionChanged?.Invoke(this, newState);
        }

        public void OnOutputConnectionChanged(ConnectionState newState)
        {
            OutputConnectionChanged?.Invoke(this, newState);
        }

        public void OnConnectionError(string message)
        {
            ConnectionError?.Invoke(this, message);
        }
    }
}