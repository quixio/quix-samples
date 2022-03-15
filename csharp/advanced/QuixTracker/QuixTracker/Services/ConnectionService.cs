using System;
using System.Diagnostics;
using QuixTracker.Models;

namespace QuixTracker.Services
{

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

        public Models.Settings Settings { get; private set; }

        public event EventHandler<ConnectionState> InputConnectionChanged;
        public event EventHandler<ConnectionState> OutputConnectionChanged;
        public event EventHandler<string> ConnectionError;
        public event EventHandler<CurrentData> DataReceived;

        public ConnectionState OutputConnectionState { get; private set; }

        public ConnectionService()
        {
            this.Settings = new Models.Settings();


        }

        public void Test()
        {

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
            OutputConnectionState = newState;
        }

        public void OnConnectionError(string message)
        {
            ConnectionError?.Invoke(this, message);
        }
    }
}