using System;
using Xamarin.Essentials;

namespace QuixTracker.Models
{
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
            this.workspaceId = "quixdev-iotdemo";
            this.subDomain = "dev";
            this.token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlpXeUJqWTgzcXotZW1pUlZDd1I4dyJ9.eyJodHRwczovL3F1aXguYWkvb3JnX2lkIjoicXVpeGRldiIsImh0dHBzOi8vcXVpeC5haS9yb2xlcyI6ImFkbWluIFF1aXhBZG1pbiIsImlzcyI6Imh0dHBzOi8vYXV0aC5kZXYucXVpeC5haS8iLCJzdWIiOiJhdXRoMHwzOWRmMmU1ZS0zN2I0LTQzNDEtYWIxNy1kNWIyODA3Yjk0ZjAiLCJhdWQiOlsiaHR0cHM6Ly9wb3J0YWwtYXBpLmRldi5xdWl4LmFpLyIsImh0dHBzOi8vcXVpeC1kZXYuZXUuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTY0NzMzNjE0MCwiZXhwIjoxNjQ5OTI4MTQwLCJhenAiOiI2MDRBOXE1Vm9jWW92b05Qb01panVlVVpjRUhJY2xNcyIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJwZXJtaXNzaW9ucyI6W119.py3idBal-w0AKNaCWsS4nTMygxvgtQv_nHy6eUJNAAx2MAA26rm_SOoL9IXmQsHfc3XE42kcw92sW9PkU7AGqrqMq8rGtc7QJHYWs3TWeTsc5gzNMOA8WSihFKdEjuiAOpzCFlbr-5dF9umkQZI0ULzt37EjzMvrXtK6PI2jgI8Kd5FX4cDNx8jyWyVp0VkB6Hk_sjkwaE0yxK9NgPFBIcTEIhpPPRKIg22rq23m2dEPNTq18jY9RI9nWT1LEMqyKWV6az39KqHhuG9wXXhKKLftadPSaSjke5OyL-cV7CsWimtv46lzgL1KJ4jl7Z5QzrKlL2BWErcwQITqU2yRQQ";
            this.topic = "phone-data";

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
}