using Android.App;
using Android.Content;
using Android.OS;
using Android.Runtime;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Xamarin.Essentials;
using System.Threading;
using Android.Hardware;
using System.Collections.Concurrent;
using Flurl.Http.Configuration;
using System.Net.Http;
using AndroidX.Core.App;
using QuixTracker.Services;
using System.Text.Json;
using Android.Locations;
using Plugin.Geolocator.Abstractions;
using Plugin.Geolocator;
using Android.Gms.Location;
using Android.Content.PM;

namespace QuixTracker.Droid
{
    public class NotificationService
    {
        private readonly NotificationManager notificationManager;
        private readonly Service parentService;

        public NotificationService(NotificationManager notificationManager, Android.App.Service parentService)
        {
            this.notificationManager = notificationManager;
            this.parentService = parentService;
        }

        public void SendForegroundNotification(string title, string content)
        {
            Notification notification = CreateNotification(title, content);

            try
            {
                this.parentService.StartForeground(1, notification, Android.Content.PM.ForegroundService.TypeLocation);
            }
            catch
            {
                this.parentService.StartForeground(1, notification);
            }
        }

        public void SendNotifcation(string title, string content)
        {
            Notification notification = CreateNotification(title, content);

            this.notificationManager.Notify(2, notification);
        }

        private Notification CreateNotification(string title, string content)
        {
            String CHANNEL_ID = "my_channel_01";
            NotificationChannel channel = new NotificationChannel(CHANNEL_ID,
                "Quix tracking app",
                NotificationImportance.High);

            var notification = new NotificationCompat.Builder(this.parentService, CHANNEL_ID)
                .SetAutoCancel(true) // Dismiss the notification from the notification area when the user clicks on it
                .SetContentTitle(title) // Set the title
                //.SetContentIntent(resultPendingIntent)
                .SetNumber(3) // Display the count in the Content Info
                .SetSmallIcon(Resource.Drawable.notification_tile_bg) // This is the icon to display
                .SetContentText(content).Build();

            this.notificationManager.CreateNotificationChannel(channel);
            return notification;
        }
    }

    public class UntrustedCertClientFactory : DefaultHttpClientFactory
    {
        public override HttpMessageHandler CreateMessageHandler()
        {
            return new HttpClientHandler
            {
                ServerCertificateCustomValidationCallback = (a, b, c, d) => true
            };
        }
    }

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
        private IList<Sensor> sensorList;

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
                await this.StopGeoLocationTracking();

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

        public void StartForegroundServiceCompat()
        {
        }

        #endregion

        public async void DoWork()
        {
            this.sensorManager = GetSystemService(Context.SensorService) as SensorManager;

            this.gyroSensor = this.sensorManager.GetDefaultSensor(SensorType.Accelerometer);
            this.tempSensor = this.sensorManager.GetDefaultSensor(SensorType.AmbientTemperature);

            this.sensorList = sensorManager.GetSensorList(SensorType.All);

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

        //When the DI Container fetches a new instance of the AndroidLocationService
        //Wire up the _locationManager/Provider stuff and tell it to start fetching updates every 2 ses
        async Task StartGeoLocationTracking()
        {
            CrossGeolocator.Current.DesiredAccuracy = 5;
            await CrossGeolocator.Current.StartListeningAsync(
                TimeSpan.FromMilliseconds(this.connectionService.Settings.Interval), 1, true);

            CrossGeolocator.Current.PositionChanged += Geolocator_PositionChanged;
        }

        public class LocationCallbackExt : LocationCallback
        {
            private readonly PeriodicBackgroundService trackingService;

            public LocationCallbackExt(PeriodicBackgroundService trackingService)
            {
                this.trackingService = trackingService;
            }

            public override void OnLocationResult(LocationResult result)
            {
                base.OnLocationResult(result);

                trackingService.OnLocationChanged(result.LastLocation);
            }
        }

        async Task StopGeoLocationTracking()
        {
            await CrossGeolocator.Current.StopListeningAsync();

            CrossGeolocator.Current.PositionChanged -= Geolocator_PositionChanged;
        }

        private void Geolocator_PositionChanged(object sender, PositionEventArgs e)
        {
            this.OnLocationChanged(e.Position);
        }

        private void QuixServiceEventDataReceived(object sender, EventDataDTO e)
        {
            var notification = JsonSerializer.Deserialize<NotificationDTO>(e.Value,
                new JsonSerializerOptions {PropertyNameCaseInsensitive = true});
            this.notificationService.SendNotifcation(notification.Title, notification.Content);
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
                    this.connectionService.Test();
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

        public void OnLocationChanged2(LocationCallbackAvailabilityEventArgs e)
        {
        }

        public async void OnLocationChanged(Position location)
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
                            {"Heading", new[] {location.Heading}},
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

        public void OnProviderDisabled(string provider)
        {
        }

        public void OnProviderEnabled(string provider)
        {
        }

        public void OnStatusChanged(string provider, [GeneratedEnum] Availability status, Bundle extras)
        {
        }
    }
}