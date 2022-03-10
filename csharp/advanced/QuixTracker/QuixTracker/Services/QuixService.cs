using Microsoft.AspNetCore.SignalR.Client;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Threading.Tasks;

namespace QuixTracker.Services
{
    public class ParameterDataDTO
    {
        public int Epoch { get; set; }
        public long[] Timestamps { get; set; }
        public Dictionary<string, double[]> NumericValues { get; set; }
        public Dictionary<string, string[]> StringValues { get; set; }
        public Dictionary<string, string[]> BinaryValues { get; set; }
        public Dictionary<string, string[]> TagValues { get; set; }
    }

    public class EventDataDTO
    {
        public long Timestamp { get; set; }
        public string Id { get; set; }
        public string Value { get; set; }
        public Dictionary<string, string> Tags { get; set; }
    }

    public class NotificationDTO
    {
        public string Title { get; set; }

        public string Content { get; set; }
    }

    public class QuixService
    {
        // private const string Token = "{placeholder:token}";
        // private const string Token = ;


        private readonly ConnectionService connectionService;
        private HubConnection inputConnection;
        private HubConnection outputConnection;

        public event EventHandler<EventDataDTO> EventDataReceived;
        public event EventHandler InputCo;


        public QuixService(ConnectionService connectionService)
        {
            this.connectionService = connectionService;
        }

        public async Task SubscribeToEvent(string streamId, string eventId)
        {
            await this.inputConnection.InvokeAsync("SubscribeToEvent", "phone-out", streamId + "-notifications",
                eventId);
        }

        public async Task StartInputConnection()
        {
            this.inputConnection = CreateWebSocketConnection("reader");

            this.inputConnection.On<ParameterDataDTO>("ParameterDataReceived", data => { });

            this.inputConnection.On<EventDataDTO>("EventDataReceived",
                data => { this.EventDataReceived?.Invoke(this, data); });

            this.inputConnection.Reconnecting += (e) =>
            {
                this.connectionService.OnInputConnectionChanged(ConnectionState.Reconnecting);

                return Task.CompletedTask;
            };

            this.inputConnection.Reconnected += (e) =>
            {
                this.connectionService.OnInputConnectionChanged(ConnectionState.Connected);

                return Task.CompletedTask;
            };

            this.inputConnection.Closed += (e) =>
            {
                this.connectionService.OnInputConnectionChanged(ConnectionState.Disconnected);

                return Task.CompletedTask;
            };


            await this.inputConnection.StartAsync();
        }

        public async Task StartOutputConnection()
        {
            this.outputConnection = CreateWebSocketConnection("writer");

            this.outputConnection.Reconnecting += (e) =>
            {
                this.connectionService.OnOutputConnectionChanged(ConnectionState.Reconnecting);

                return Task.CompletedTask;
            };

            this.outputConnection.Reconnected += (e) =>
            {
                this.connectionService.OnOutputConnectionChanged(ConnectionState.Connected);

                return Task.CompletedTask;
            };

            this.outputConnection.Closed += (e) =>
            {
                this.connectionService.OnOutputConnectionChanged(ConnectionState.Disconnected);

                return Task.CompletedTask;
            };

            await this.outputConnection.StartAsync();
        }

        private HubConnection CreateWebSocketConnection(string service)
        {
            var url = $"https://{service}-{this.connectionService.Settings.WorkspaceId}" +
                      $".{this.connectionService.Settings.SubDomain}.quix.ai/hub";

            return new HubConnectionBuilder()
                .WithAutomaticReconnect(Enumerable.Repeat(5, 5).Select(s => TimeSpan.FromSeconds(s))
                    .Union(Enumerable.Repeat(30, 1000).Select(s => TimeSpan.FromSeconds(s))).ToArray())
                .WithUrl(
                    url,
                    options =>
                    {
                        options.AccessTokenProvider = () => Task.FromResult(this.connectionService.Settings.Token);

                        options.HttpMessageHandlerFactory = factory => new HttpClientHandler
                        {
                            ServerCertificateCustomValidationCallback = (message, cert, chain, errors) =>
                            {
                                return true;
                            }
                        };
                    })
                .Build();
        }

        public async Task CloseStream(string streamId)
        {
            await this.outputConnection.InvokeAsync("CloseStream", "phone", streamId);
        }

        public async Task<string> CreateStream(string deviceId, string rider, string team, string sessionName)
        {
            var streamId = $"{rider}-{deviceId}-{Guid.NewGuid().ToString().Substring(0, 6)}";
            if (string.IsNullOrEmpty(sessionName))
            {
                sessionName = streamId;
            }

            var streamDetails = new
            {
                Name = sessionName,
                Location = team + "/" + rider,
                Metadata = new
                {
                    Rider = rider,
                    CreatedAt = DateTimeOffset.UtcNow
                }
            };

            await this.outputConnection.InvokeAsync("UpdateStream", "phone", streamId, streamDetails);

            return streamId;
        }

        public async Task SendParameterData(string streamId, ParameterDataDTO data)
        {
            await this.outputConnection.InvokeAsync("SendParameterData", "phone", streamId, data);
        }
    }
}