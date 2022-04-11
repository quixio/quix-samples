using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging.Abstractions;
using Quix.Snowflake.Domain.Common;
using Quix.Snowflake.Domain.Models;
using Quix.Snowflake.Infrastructure.Metadata;
using Quix.Snowflake.Infrastructure.Shared;
using Xunit;

namespace Quix.Snowflake.Infrastructure.Tests;

public class UnitTest1
{
    private StreamRepository CreateStreamRepo()
    {
        return new StreamRepository(null, new NullLoggerFactory());
    }
    
    private EventRepository CreateEventRepo()
    {
        return new EventRepository(null, new NullLoggerFactory());
    }
    
    [Fact]
    public async Task StreamRepository_BulkWrite_QuickTests()
    {
        // Arrange
        SnowflakeSchemaRegistry.Register();
        var repo = CreateStreamRepo();

        var stream = new TelemetryStream("baseStream");

        var streamUpdates = new List<WriteModel<TelemetryStream>>()
        {
            new UpdateOneModel<TelemetryStream>(stream, Builders<TelemetryStream>.Update.Set(y => y.Location, "adb")),
            new UpdateOneModel<TelemetryStream>(stream, Builders<TelemetryStream>.Update.Set(y => y.End, 123)),
            new UpdateOneModel<TelemetryStream>(stream, Builders<TelemetryStream>.Update.Combine(Builders<TelemetryStream>.Update.Set(y => y.End, 123), Builders<TelemetryStream>.Update.Set(y => y.Start, 121))),
            new UpdateOneModel<TelemetryStream>(stream, Builders<TelemetryStream>.Update.Set(y => y.Status, StreamStatus.Aborted)),
            new UpdateOneModel<TelemetryStream>(stream, Builders<TelemetryStream>.Update.Set(y => y.Parents, new List<string> {"a", "b"})),
            new UpdateOneModel<TelemetryStream>(stream, Builders<TelemetryStream>.Update.Set(y => y.Metadata, new Dictionary<string, string>() {{"a", "2"}, {"b", "2"}})),
            new DeleteManyModel<TelemetryStream>(Builders<TelemetryStream>.Filter.Eq(y => y.StreamId, "asdf").And(Builders<TelemetryStream>.Filter.Eq(y => y.Name, "stuff"))),
            new InsertOneModel<TelemetryStream>(new TelemetryStream("somestream")
            {
                End = 123,
                Location = "test",
                Metadata = new Dictionary<string, string>()
                {
                    {"a", "1"},
                    {"b", "2"}
                },
                Parents = new List<string>() { "parent1", "parent2"}
            })
        };

        // Act
        await repo.BulkWrite(streamUpdates);

        // Assert
    }
    
    [Fact]
    public async Task StreamRepository_Get_QuickTests()
    {
        // Arrange
        SnowflakeSchemaRegistry.Register();
        var repo = CreateStreamRepo();

        var displayName = "test";
        var streamsToNotLoad = new List<string>() { "stream1", "stream2", "stream3" };

        var filter = Builders<TelemetryStream>.Filter.Eq(y => y.Status, StreamStatus.Open)
            .And(Builders<TelemetryStream>.Filter.Eq(y => y.Topic, displayName).Not())
            .And(Builders<TelemetryStream>.Filter.In(y => y.StreamId, streamsToNotLoad).Not());
        // Act
        await repo.Get(filter);

        // Assert
    }
    
    [Fact]
    public async Task EventRepositoryQuickTests()
    {
        // Arrange
        SnowflakeSchemaRegistry.Register();
        var repo = CreateEventRepo();
        var tEvent = new TelemetryEvent("mystreamId");

        var streamUpdates = new List<WriteModel<TelemetryEvent>>()
        {
            new UpdateOneModel<TelemetryEvent>(tEvent, Builders<TelemetryEvent>.Update.Set(y => y.Name, "newname")),
            new UpdateOneModel<TelemetryEvent>(tEvent, Builders<TelemetryEvent>.Update.Set(y => y.Level, TelemetryEventLevel.Error)),
            new UpdateOneModel<TelemetryEvent>(tEvent, Builders<TelemetryEvent>.Update.Set(y => y.Level, TelemetryEventLevel.Error)),
            new UpdateOneModel<TelemetryEvent>(tEvent, Builders<TelemetryEvent>.Update.Combine(Builders<TelemetryEvent>.Update.Set(y => y.Description, "har"), Builders<TelemetryEvent>.Update.Set(y => y.Location, "/new"))),
        };

        // Act
        await repo.BulkWrite(streamUpdates);

        // Assert
    }
}