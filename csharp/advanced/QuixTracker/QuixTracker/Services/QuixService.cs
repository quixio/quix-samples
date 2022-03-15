
using Microsoft.AspNetCore.SignalR.Client;
using QuixTracker.Models;
using System;
using System.Linq;
using System.Net.Http;
using System.Threading.Tasks;

namespace QuixTracker.Services
{

    public class QuixService : IDisposable
    {
        private readonly ConnectionService connectionService;
        private HubConnection inputConnection;
        private HubConnection outputConnection;

        public event EventHandler<EventDataDTO> EventDataRecieved;


        public QuixService(ConnectionService connectionService)
        {
            this.connectionService = connectionService;
        }

        public async Task SubscribeToEvent(string streamId, string eventId)
        {
            await this.inputConnection.InvokeAsync("SubscribeToEvent", "phone-out", streamId + "-notifications", eventId);
        }

        public async Task StartInputConnection()
        {
            this.inputConnection = CreateWebSocketConnection("reader");

            this.inputConnection.On<ParameterDataDTO>("ParameterDataReceived", data =>
            {

            });

            this.inputConnection.On<EventDataDTO>("EventDataReceived", data =>
            {
                this.EventDataRecieved?.Invoke(this, data);
            });

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

       

        public async Task CloseStream(string streamId)
        {
            await this.outputConnection.InvokeAsync("CloseStream", "phone", streamId);

        }

        public async Task<string> CreateStream(string deviceId, string rider, string team, string sesionName)
        {
            var streamId = $"{rider}-{deviceId}-{Guid.NewGuid().ToString().Substring(0, 6)}";
            if (string.IsNullOrEmpty(sesionName))
            {
                sesionName = streamId;
            }


            var streamDetails = new
            {
                Name = sesionName,
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

        public async void Dispose()
        {
            await this.inputConnection.DisposeAsync();
            await this.outputConnection.DisposeAsync();
        }

        private HubConnection CreateWebSocketConnection(string service)
        {
            var url = $"https://{service}-{this.connectionService.Settings.WorkspaceId}" +
                      $".{this.connectionService.Settings.SubDomain}.quix.ai/hub";


            return new HubConnectionBuilder()
                .WithAutomaticReconnect(Enumerable.Repeat(5, 10000).Select(s => TimeSpan.FromSeconds(s)).ToArray())
              .WithUrl(url, options =>
              {
                  options.AccessTokenProvider = () => Task.FromResult(this.connectionService.Settings.Token);
                  options.DefaultTransferFormat = Microsoft.AspNetCore.Connections.TransferFormat.Binary;

                  options.HttpMessageHandlerFactory = factory => new HttpClientHandler
                  {
                      ServerCertificateCustomValidationCallback = (message, cert, chain, errors) => { return true; }
                  };
              })
              .Build();
        }
    }
}
