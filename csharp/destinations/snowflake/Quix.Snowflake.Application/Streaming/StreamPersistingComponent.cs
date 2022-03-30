using System;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using Quix.Snowflake.Application.TimeSeries;
using Quix.Sdk.Process;
using Quix.Sdk.Process.Models;

namespace Quix.Snowflake.Application.Streaming
{
    public class StreamPersistingComponent : StreamComponent, IDisposable
    {
        private readonly ILogger<StreamPersistingComponent> logger;
        private readonly ITimeSeriesBufferedPersistingService timeSeriesBufferedPersistingService;

        public StreamPersistingComponent(ILogger<StreamPersistingComponent> logger,
            ITimeSeriesBufferedPersistingService timeSeriesBufferedPersistingService)
        {
            this.logger = logger;
            this.timeSeriesBufferedPersistingService = timeSeriesBufferedPersistingService;
            this.Input.LinkTo(this.Output);
            this.Input.Subscribe<ParameterDataRaw>(this.OnParameterDataReceived);
            this.Input.Subscribe<EventDataRaw[]>(this.OnMultipleEventDataReceived);
            this.Input.Subscribe<EventDataRaw>(this.OnEventDataReceived);
        }

        private async Task OnEventDataReceived(EventDataRaw arg)
        {
            var asArray = new[] {arg};
            await this.timeSeriesBufferedPersistingService.Buffer(this.StreamProcess.StreamId, asArray);
        }

        private async Task OnMultipleEventDataReceived(EventDataRaw[] arg)
        {
            await this.timeSeriesBufferedPersistingService.Buffer(this.StreamProcess.StreamId, arg);
        }

        private async Task OnParameterDataReceived(ParameterDataRaw arg)
        {
            await this.timeSeriesBufferedPersistingService.Buffer(this.StreamProcess.StreamId, arg);
        }

        public void Dispose()
        {

        }
    }
}