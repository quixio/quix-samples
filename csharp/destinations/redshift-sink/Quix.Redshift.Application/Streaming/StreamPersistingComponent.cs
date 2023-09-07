using System;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using Quix.Redshift.Application.TimeSeries;
using QuixStreams.Telemetry;
using QuixStreams.Telemetry.Models;

namespace Quix.Redshift.Application.Streaming
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
            this.Input.Subscribe<TimeseriesDataRaw>(this.OnParameterDataReceived);
            this.Input.Subscribe<EventDataRaw[]>(this.OnMultipleEventDataReceived);
            this.Input.Subscribe<EventDataRaw>(this.OnEventDataReceived);
        }

        private async Task OnEventDataReceived(EventDataRaw arg)
        {
            var asArray = new[] {arg};
            await this.timeSeriesBufferedPersistingService.Buffer(this.StreamPipeline.StreamId, asArray);
        }

        private async Task OnMultipleEventDataReceived(EventDataRaw[] arg)
        {
            await this.timeSeriesBufferedPersistingService.Buffer(this.StreamPipeline.StreamId, arg);
        }

        private async Task OnParameterDataReceived(TimeseriesDataRaw arg)
        {
            await this.timeSeriesBufferedPersistingService.Buffer(this.StreamPipeline.StreamId, arg);
        }

        public void Dispose()
        {

        }
    }
}