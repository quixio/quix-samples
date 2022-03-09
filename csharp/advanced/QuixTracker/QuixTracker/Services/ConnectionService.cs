using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.Text;
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

        public Settings()
        {
            this.DeviceId = Preferences.Get("DeviceId", "My session");
            this.Rider = Preferences.Get("Rider", "MyName");
            this.Team = Preferences.Get("Team", "My team");
            this.Interval = Preferences.Get("Interval", 250);
            this.LogGForce = Preferences.Get("LogGForce", true);
        }

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
