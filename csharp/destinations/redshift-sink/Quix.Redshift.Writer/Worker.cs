using System;
using System.Diagnostics;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Quix.Redshift.Application.Streaming;
using Quix.Redshift.Application.TimeSeries;
using Quix.Redshift.Writer.Helpers;
using QuixStreams.Telemetry;
using QuixStreams.Telemetry.Kafka;
using QuixStreams.Telemetry.Models;
using QuixStreams.Transport.Kafka;

namespace Quix.Redshift.Writer
{
    public class Worker : BackgroundService
    {

        private readonly ILogger<Worker> logger;
        private readonly IServiceProvider serviceProvider;
        private readonly ITimeSeriesBufferedPersistingService timeSeriesBufferedPersistingService;
        private readonly QuixConfigHelper quixConfigHelper;

        public Worker(ILogger<Worker> logger,
            IServiceProvider serviceProvider,
            ITimeSeriesBufferedPersistingService timeSeriesBufferedPersistingService,
            QuixConfigHelper quixConfigHelper)
        {
            this.logger = logger;
            this.serviceProvider = serviceProvider;
            this.timeSeriesBufferedPersistingService = timeSeriesBufferedPersistingService;
            this.quixConfigHelper = quixConfigHelper;
        }

        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
        {
            this.logger.LogInformation("Register codecs");
            CodecRegistry.Register();

            this.logger.LogInformation("Creating Kafka Reader");

            var (kafkaConfiguration, topicId) = quixConfigHelper.GetConfiguration().GetAwaiter().GetResult();

            var kafkaReader = new TelemetryKafkaConsumer(kafkaConfiguration, topicId);

            kafkaReader.OnCommitting += (sender, args) =>
            {
                var sw = Stopwatch.StartNew();
                this.logger.LogTrace("Saving to database the messages read so far.");
                var taskTimeSeries = this.timeSeriesBufferedPersistingService.Save();
                Task.WaitAll(taskTimeSeries); // Very important. The save has to complete within this callback
                this.logger.LogDebug("Saved to database the messages read so far in {0:g}.", sw.Elapsed);
            };
            
            kafkaReader.ForEach(streamId =>
            {
                this.logger.LogTrace("New stream opened for read: {0}.", streamId);
                var scope = this.serviceProvider.CreateScope();
                var memoryLimiter = scope.ServiceProvider.GetRequiredService<MemoryLimiterComponent>();
                var persistingComponent = scope.ServiceProvider.GetRequiredService<StreamPersistingComponent>();

                var streamPipeline = new StreamPipeline(streamId)
                    .AddComponent(memoryLimiter)
                    .AddComponent(persistingComponent);
                
                return streamPipeline;
            });

            kafkaReader.OnStreamsRevoked += streams =>
            {
                var streamIds = streams.Select(y => y.StreamId).ToArray();
                this.timeSeriesBufferedPersistingService.ClearBuffer(streamIds);
            };

            kafkaReader.OnReceiveException += (s, e) =>
            {
                this.logger.LogError(e, "Kafka reader exception");
            };

            kafkaReader.Start();

            try
            {
                await Task.Delay(-1, stoppingToken);
            }
            catch (TaskCanceledException ex)
            {
                // shutting down
            }


            this.logger.LogInformation("Service stopping, closing Kafka");
            var sw = Stopwatch.StartNew();
            kafkaReader.Stop();
            sw.Stop();
            this.logger.LogInformation("Kafka stopped in {0:g}", sw.Elapsed);
        }
    }
}