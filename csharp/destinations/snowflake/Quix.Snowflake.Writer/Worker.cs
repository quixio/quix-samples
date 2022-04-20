using System;
using System.Diagnostics;
using System.Linq;
using System.Net.Http;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Quix.Snowflake.Application.Streaming;
using Quix.Snowflake.Application.TimeSeries;
using Quix.Snowflake.Writer.Configuration;
using Quix.Snowflake.Writer.Helpers;
using Quix.Sdk.Process;
using Quix.Sdk.Process.Kafka;
using Quix.Sdk.Process.Models;
using Quix.Snowflake.Application.Metadata;

namespace Quix.Snowflake.Writer
{
    public class Worker : BackgroundService
    {

        private readonly ILogger<Worker> logger;
        private readonly IServiceProvider serviceProvider;
        private readonly IMetadataBufferedPersistingService metadataBufferedPersistingService;
        private readonly ITimeSeriesBufferedPersistingService timeSeriesBufferedPersistingService;
        private readonly QuixConfigHelper quixConfigHelper;

        public Worker(ILogger<Worker> logger,
            IServiceProvider serviceProvider,
            IMetadataBufferedPersistingService metadataBufferedPersistingService,
            ITimeSeriesBufferedPersistingService timeSeriesBufferedPersistingService,
            QuixConfigHelper quixConfigHelper)
        {
            this.logger = logger;
            this.serviceProvider = serviceProvider;
            this.metadataBufferedPersistingService = metadataBufferedPersistingService;
            this.timeSeriesBufferedPersistingService = timeSeriesBufferedPersistingService;
            this.quixConfigHelper = quixConfigHelper;
        }

        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
        {
            this.logger.LogInformation("Registering codecs");
            CodecRegistry.Register();

            this.logger.LogInformation("Creating Kafka Reader");

            var (kafkaConfiguration, topicId) = quixConfigHelper.GetConfiguration().GetAwaiter().GetResult();

            var kafkaReader = new KafkaReader(kafkaConfiguration, topicId);

            kafkaReader.OnCommitting += (sender, args) =>
            {
                var sw = Stopwatch.StartNew();
                this.logger.LogTrace("Saving to database the messages read so far.");
                var taskMetadata = this.metadataBufferedPersistingService.Save();
                var taskTimeSeries = this.timeSeriesBufferedPersistingService.Save();
                Task.WaitAll(taskMetadata, taskTimeSeries); // Very important. The save has to complete within this callback
                this.logger.LogDebug("Saved to database the messages read so far in {0:g}.", sw.Elapsed);
            };
            
            kafkaReader.ForEach(streamId =>
            {
                this.logger.LogTrace("New stream opened for read: {0}.", streamId);
                var scope = this.serviceProvider.CreateScope();
                var memoryLimiter = scope.ServiceProvider.GetRequiredService<MemoryLimiterComponent>();
                var persistingComponent = scope.ServiceProvider.GetRequiredService<StreamPersistingComponent>();

                var streamProcess = new StreamProcess(streamId)
                    .AddComponent(memoryLimiter)
                    .AddComponent(persistingComponent);
                
                return streamProcess;
            });

            kafkaReader.OnStreamsRevoked += streams =>
            {
                var streamIds = streams.Select(y => y.StreamId).ToArray();
                this.metadataBufferedPersistingService.ClearBuffer(streamIds);
                this.timeSeriesBufferedPersistingService.ClearBuffer(streamIds);
            };

            kafkaReader.OnReadException += (s, e) =>
            {
                this.logger.LogError(e, "Kafka reader exception");
            };

            this.logger.LogInformation("Created Kafka Reader");
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