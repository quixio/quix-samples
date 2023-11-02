using System;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using Quix.SqlServer.Application.Metadata;
using Quix.SqlServer.Application.TimeSeries;
using QuixStreams.Telemetry;
using QuixStreams.Telemetry.Models;

namespace Quix.SqlServer.Application.Streaming
{
    public class StreamPersistingComponent : StreamComponent, IDisposable
    {
        private readonly ILogger<StreamPersistingComponent> logger;
        private readonly IMetadataBufferedPersistingService metadataBufferedPersistingService;
        private readonly ITimeSeriesBufferedPersistingService timeSeriesBufferedPersistingService;

        public StreamPersistingComponent(ILogger<StreamPersistingComponent> logger,
            IMetadataBufferedPersistingService metadataBufferedPersistingService,
            ITimeSeriesBufferedPersistingService timeSeriesBufferedPersistingService)
        {
            this.logger = logger;
            this.metadataBufferedPersistingService = metadataBufferedPersistingService;
            this.timeSeriesBufferedPersistingService = timeSeriesBufferedPersistingService;
            this.Input.LinkTo(this.Output);
            
            // main data
            this.Input.Subscribe<TimeseriesDataRaw>(this.OnParameterDataReceived);
            this.Input.Subscribe<EventDataRaw[]>(this.OnMultipleEventDataReceived);
            this.Input.Subscribe<EventDataRaw>(this.OnEventDataReceived);
            
            // metadata
            this.Input.Subscribe<ParameterDefinitions>(OnParameterDefinitionsReceived);
            this.Input.Subscribe<EventDefinitions>(OnEventDefinitionsReceived);
            this.Input.Subscribe<StreamProperties>(OnStreamPropertiesReceived);
            this.Input.Subscribe<StreamEnd>(OnStreamEndReceived);
        }

        private async Task OnEventDataReceived(EventDataRaw arg)
        {
            var asArray = new[] {arg};

            await this.metadataBufferedPersistingService.Buffer(this.StreamPipeline.StreamId, asArray);
            await this.timeSeriesBufferedPersistingService.Buffer(this.StreamPipeline.StreamId, asArray);
        }

        private async Task OnMultipleEventDataReceived(EventDataRaw[] arg)
        {
            await metadataBufferedPersistingService.Buffer(this.StreamPipeline.StreamId, arg);
            await this.timeSeriesBufferedPersistingService.Buffer(this.StreamPipeline.StreamId, arg);
        }

        private async Task OnParameterDataReceived(TimeseriesDataRaw arg)
        {
            var discardRange = await this.metadataBufferedPersistingService.GetDiscardRange(this.StreamPipeline.StreamId, arg.Epoch + arg.Timestamps.Min());
            await metadataBufferedPersistingService.Buffer(this.StreamPipeline.StreamId, arg);
            await this.timeSeriesBufferedPersistingService.Buffer(this.StreamPipeline.StreamId, arg);
        }

        private Task OnStreamEndReceived(StreamEnd arg)
        {
            return metadataBufferedPersistingService.Buffer(this.StreamPipeline.StreamId, arg);
        }

        private Task OnStreamPropertiesReceived(StreamProperties arg)
        {
            return metadataBufferedPersistingService.Buffer(this.StreamPipeline.StreamId, arg);
        }

        private Task OnEventDefinitionsReceived(EventDefinitions arg)
        {
            return metadataBufferedPersistingService.Buffer(this.StreamPipeline.StreamId, arg);
        }

        private Task OnParameterDefinitionsReceived(ParameterDefinitions arg)
        {
            return metadataBufferedPersistingService.Buffer(this.StreamPipeline.StreamId, arg);
        }
        
        public void Dispose()
        {

        }
    }
}