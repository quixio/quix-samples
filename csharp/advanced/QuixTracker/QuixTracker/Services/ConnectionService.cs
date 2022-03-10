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
        
        public Settings()
        {
            // this.DeviceId = Preferences.Get("DeviceId", "My session");
            // this.Rider = Preferences.Get("Rider", "MyName");
            // this.Team = Preferences.Get("Team", "My team");
            // this.Interval = Preferences.Get("Interval", 250);
            // this.LogGForce = Preferences.Get("LogGForce", true);

            // these will be populated by Quix when you save the project to your workspace.
            this.workspaceId = "{placeholder:workspaceId}";
            this.subDomain = "{placeholder:environment.subdomain}";
            this.token = "{placeholder:token}";

            // debug values
            this.token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlpXeUJqWTgzcXotZW1pUlZDd1I4dyJ9.eyJodHRwczovL3F1aXguYWkvb3JnX2lkIjoicXVpeGRldiIsImh0dHBzOi8vcXVpeC5haS9yb2xlcyI6ImFkbWluIFF1aXhBZG1pbiIsImlzcyI6Imh0dHBzOi8vYXV0aC5kZXYucXVpeC5haS8iLCJzdWIiOiJhdXRoMHw5YjFhYjE5Yy05NWYwLTRhZjQtYjczMy0yYWRmYjY0MmUxMmUiLCJhdWQiOlsiaHR0cHM6Ly9wb3J0YWwtYXBpLmRldi5xdWl4LmFpLyIsImh0dHBzOi8vcXVpeC1kZXYuZXUuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTY0NjgzODgwNywiZXhwIjoxNjQ5NDMwODA3LCJhenAiOiI2MDRBOXE1Vm9jWW92b05Qb01panVlVVpjRUhJY2xNcyIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJwZXJtaXNzaW9ucyI6W119.Yt4a7NBWQmk51gM3YTpOyUzqLGcU8fSqKMQKA2MyjBfJc24RUF03FQzsfNajnGat75k-4KwW8W1xNwQduBmZUsCQn8IGhfm5mDLyYWMOSsA393kXEi2cduyGZFgu-3chlccF2CZ4IzxRmOqyUeCh6OKDOJ1L9UPxjvkAhS-MtT93iZGR4j2XlQPDzCjcTs9-ktoCxqNrqPD2Q6aOBSaTF28-OMnhyIjMWSRSMfDdui3pPECciIbUYNnA0OenUiVqqyf5mxKS_HWVprp6g2pp5ywF86bEqa_LQCdrbqW0P8BrW9B1T1zQHBAM3NUJ5Bm8C07-OyYPTXihQ7nSxwTl5A";
            this.workspaceId = "quixdev-stevesstuff";
            this.subDomain = "dev";
        }

        public string WorkspaceId => workspaceId;
        public string SubDomain => subDomain;
        public string Token => token;

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

        public void Test()
        {
        }

        public void OnDataReceived(CurrentData data)
        {
            Debug.WriteLine("HEY");
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