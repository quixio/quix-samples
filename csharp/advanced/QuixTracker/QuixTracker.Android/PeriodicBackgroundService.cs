using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Android.App;
using Android.Content;
using Android.Content.PM;
using Android.Gms.Location;
using Android.Hardware;
using Android.Locations;
using Android.OS;
using Android.Runtime;
using Plugin.Geolocator;
using Plugin.Geolocator.Abstractions;
using QuixTracker.Services;
using Xamarin.Essentials;

namespace QuixTracker.Droid
{
    [Service(ForegroundServiceType = Android.Content.PM.ForegroundService.TypeLocation, Exported = true)]
    public class PeriodicBackgroundService : Android.App.Service, ISensorEventListener
    {
        private string streamId;
        private long lastTimeStamp;

        private const string Tag = "[PeriodicBackgroundService]";

        private bool isRunning;
        private Task task;
        private NotificationService notificationService;
        private CancellationTokenSource cancellationTokenSource;
        private SensorManager sensorManager;

        private ConcurrentDictionary<long, Tuple<double, double, double>> gforces =
            new ConcurrentDictionary<long, Tuple<double, double, double>>();

        private ConcurrentDictionary<long, double> temperatures = new ConcurrentDictionary<long, double>();
        private ConnectionService connectionService;
        private QuixService quixService;
        private DateTime lastErrorMessage = DateTime.Now;
        private Sensor gyroSensor;
        private Sensor tempSensor;
        private FusedLocationProviderClient fusedLocationProviderClient;
        private PackageInfo packageInfo;

        public PeriodicBackgroundService()
        {
            this.connectionService = ConnectionService.Instance;
            this.quixService = new QuixService(this.connectionService);

            var context = Android.App.Application.Context;

            this.packageInfo = context.PackageManager.GetPackageInfo(context.PackageName, 0);
        }

        #region overrides

        public override IBinder OnBind(Intent intent)
        {
            return null;
        }

        public void Start()
        {
        }

        public override void OnCreate()
        {
            isRunning = false;

            task = new Task(DoWork);

            this.notificationService =
                new NotificationService(GetSystemService(Context.NotificationService) as NotificationManager, this);
            this.notificationService.SendForegroundNotification("Quix tracking service", "Tracking in progress...");

            this.cancellationTokenSource = new CancellationTokenSource();
        }

        public override async void OnDestroy()
        {
            try
            {
                this.cancellationTokenSource.Cancel();

                this.task.Wait(1000);

                await this.quixService.CloseStream(this.streamId);

                isRunning = false;

                if (task != null && task.Status == TaskStatus.RanToCompletion)
                {
                    task.Dispose();
                }
            }
            catch (Exception ex)
            {
                this.connectionService.OnConnectionError(ex.Message);
                this.lastErrorMessage = DateTime.Now;
            }
            finally
            {
                this.connectionService.OnOutputConnectionChanged(ConnectionState.Disconnected);
            }
        }

        public override StartCommandResult OnStartCommand(Intent intent, StartCommandFlags flags, int startId)
        {
            if (!isRunning)
            {
                isRunning = true;
                task.Start();
            }

            return StartCommandResult.Sticky;
        }
        
        #endregion

        public async void DoWork()
        {
            this.sensorManager = GetSystemService(Context.SensorService) as SensorManager;

            this.gyroSensor = this.sensorManager.GetDefaultSensor(SensorType.Accelerometer);
            this.tempSensor = this.sensorManager.GetDefaultSensor(SensorType.AmbientTemperature);

            OnResume();

            this.connectionService.OnInputConnectionChanged(ConnectionState.Disconnected);

            try
            {
                await this.quixService.StartInputConnection();
                await this.quixService.StartOutputConnection();

                this.streamId = await this.quixService.CreateStream(
                    this.connectionService.Settings.DeviceId,
                    this.connectionService.Settings.Rider,
                    this.connectionService.Settings.Team,
                    this.connectionService.Settings.SessionName);

                this.CleanErrorMessage();

                await this.quixService.SubscribeToEvent(this.streamId, "notification");

                this.quixService.EventDataReceived += QuixServiceEventDataReceived;

                this.LocationTracking();

#pragma warning disable CS4014 // Because this call is not awaited, execution of the current method continues before the call is completed
                if (this.connectionService.Settings.LogGForce)
                {
                    this.gforceTracking();
                }
#pragma warning disable CS4014 // Because this call is not awaited, execution of the current method continues before the call is completed
                this.TemperatureTracking();

                this.connectionService.OnOutputConnectionChanged(ConnectionState.Connected);
            }
            catch (Exception ex)
            {
                this.connectionService.OnConnectionError(ex.Message);
                this.lastErrorMessage = DateTime.Now;
                this.connectionService.OnInputConnectionChanged(ConnectionState.Disconnected);

                StopSelf();
            }
        }
        
        private void QuixServiceEventDataReceived(object sender, EventDataDTO e)
        {
            var notification = JsonSerializer.Deserialize<NotificationDTO>(e.Value,
                new JsonSerializerOptions {PropertyNameCaseInsensitive = true});
            this.notificationService.SendNotification(notification.Title, notification.Content);
        }

        private void OnResume()
        {
            this.sensorManager.RegisterListener(this, this.gyroSensor, SensorDelay.Normal);
            this.sensorManager.RegisterListener(this, this.tempSensor, SensorDelay.Normal);
        }

        private void OnPause()
        {
            this.sensorManager.UnregisterListener(this, this.gyroSensor);
            this.sensorManager.UnregisterListener(this, this.tempSensor);
        }

        private async Task TemperatureTracking()
        {
            while (!this.cancellationTokenSource.IsCancellationRequested)
            {
                try
                {
                    if (!this.temperatures.IsEmpty)
                    {
                        var timestamps = this.temperatures.ToArray();
                        this.temperatures.Clear();

                        await this.quixService.SendParameterData(this.streamId, new ParameterDataDTO
                        {
                            Timestamps = new long[] {timestamps.First().Key},
                            NumericValues = new Dictionary<string, double[]>()
                            {
                                {"Temperature", new[] {timestamps.Average(s => s.Value)}},
                            }
                        });
                        this.CleanErrorMessage();
                    }
                }
                catch (Exception ex)
                {
                    this.connectionService.OnConnectionError(ex.Message);

                    this.lastErrorMessage = DateTime.Now;
                }
                finally
                {
                    await Task.Delay(this.connectionService.Settings.Interval);
                }
            }
        }

        private async Task LocationTracking()
        {
            this.fusedLocationProviderClient = LocationServices.GetFusedLocationProviderClient(this);

            while (!this.cancellationTokenSource.IsCancellationRequested)
            {
                try
                {
                    //await this.fusedLocationProviderClient.FlushLocationsAsync();
                    var location = await this.fusedLocationProviderClient.GetLastLocationAsync();
                    await this.OnLocationChanged(location);
                    var currentData = new CurrentData
                    {
                        Accuracy = location.Accuracy,
                        Speed = location.Speed
                    };
                    this.connectionService.OnDataReceived(currentData);
                }
                catch (Exception ex)
                {
                    this.connectionService.OnConnectionError(ex.Message);
                    this.lastErrorMessage = DateTime.Now;
                }
                finally
                {
                    //this.OnPause();
                    await Task.Delay(this.connectionService.Settings.Interval);
                    //this.OnResume();
                }
            }
        }

        private async Task gforceTracking()
        {
            while (!this.cancellationTokenSource.IsCancellationRequested)
            {
                try
                {
                    if (!this.gforces.IsEmpty)
                    {
                        var timestamps = this.gforces.ToArray();
                        this.gforces.Clear();

                        await this.quixService.SendParameterData(this.streamId, new ParameterDataDTO
                        {
                            Timestamps = new long[] {timestamps.First().Key},
                            NumericValues = new Dictionary<string, double[]>()
                            {
                                {"gForceX", new[] {timestamps.Average(s => s.Value.Item1)}},
                                {"gForceY", new[] {timestamps.Average(s => s.Value.Item2)}},
                                {"gForceZ", new[] {timestamps.Average(s => s.Value.Item3)}},
                            },
                            TagValues = new Dictionary<string, string[]>()
                            {
                                {"version", new string[] {this.packageInfo.VersionName}},
                                {"rider", new string[] {this.connectionService.Settings.Rider}},
                                {"team", new string[] {this.connectionService.Settings.Team}},
                            }
                        });
                        this.CleanErrorMessage();
                    }
                }
                catch (Exception ex)
                {
                    this.connectionService.OnConnectionError(ex.Message);

                    this.lastErrorMessage = DateTime.Now;
                }
                finally
                {
                    await Task.Delay(this.connectionService.Settings.Interval);
                }
            }
        }

        public void OnSensorChanged(SensorEvent e)
        {
            switch (e.Sensor.Type)
            {
                case SensorType.Accelerometer:
                    this.gforces.TryAdd((DateTime.UtcNow - new DateTime(1970, 1, 1)).Ticks * 100,
                        new Tuple<double, double, double>(e.Values[0], e.Values[1], e.Values[2]));
                    break;
                case SensorType.AmbientTemperature:
                    this.temperatures.TryAdd((DateTime.UtcNow - new DateTime(1970, 1, 1)).Ticks * 100, e.Values[0]);
                    break;
            }
        }

        private void CleanErrorMessage()
        {
            if ((DateTime.Now - lastErrorMessage).TotalSeconds > 10)
            {
                this.connectionService.OnConnectionError(null);
            }
        }

        public void OnAccuracyChanged(Sensor sensor, [GeneratedEnum] SensorStatus accuracy)
        {
        }

        public async Task OnLocationChanged(Android.Locations.Location location)
        {
            try
            {
                if (location != null && this.streamId != null)
                {
                    var timestamp = (long) (DateTime.UtcNow - new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc))
                        .TotalMilliseconds * 1000000;

                    this.lastTimeStamp = timestamp;

                    await this.quixService.SendParameterData(this.streamId, new ParameterDataDTO
                    {
                        Timestamps = new[] {timestamp},
                        NumericValues = new Dictionary<string, double[]>
                        {
                            {"Accuracy", new[] {(double) location.Accuracy}},
                            {"Altitude", new[] {location.Altitude}},
                            {"Heading", new[] {(double) location.Bearing}},
                            {"Latitude", new[] {location.Latitude}},
                            {"Longitude", new[] {location.Longitude}},
                            {"Speed", new[] {(double) location.Speed * 3.6}},
                            {"BatteryLevel", new[] {Battery.ChargeLevel}}
                        },
                        StringValues = new Dictionary<string, string[]>
                        {
                            {"BatteryState", new[] {Battery.State.ToString()}},
                            {"BatteryPowerSource", new[] {Battery.PowerSource.ToString()}},
                            {"EnergySaverStatus", new[] {Battery.EnergySaverStatus.ToString()}},
                        },
                        TagValues = new Dictionary<string, string[]>()
                        {
                            {"version", new string[] {this.packageInfo.VersionName}},
                            {"rider", new string[] {this.connectionService.Settings.Rider}},
                            {"team", new string[] {this.connectionService.Settings.Team}},
                        }
                    });

                    this.CleanErrorMessage();
                }
            }
            catch (Exception ex)
            {
                this.connectionService.OnConnectionError(ex.Message);
                this.lastErrorMessage = DateTime.Now;
            }
            finally
            {
                await Task.Delay(this.connectionService.Settings.Interval);
            }
        }
    }
}