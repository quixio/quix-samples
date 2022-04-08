using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
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
    public async Task StreamRepositoryQuickTests()
    {
        // Arrange
        SnowflakeSchemaRegistry.Register();
        var repo = CreateStreamRepo();

        var streamUpdates = new List<WriteModel<TelemetryStream>>()
        {
            new UpdateOneModel<TelemetryStream>(Builders<TelemetryStream>.Filter.Eq(y => y.End, 123), Builders<TelemetryStream>.Update.Set(y => y.Location, "adb")),
            new UpdateOneModel<TelemetryStream>(Builders<TelemetryStream>.Filter.Eq(y => y.StreamId, "asdf"), Builders<TelemetryStream>.Update.Set(y => y.End, 123)),
            new UpdateOneModel<TelemetryStream>(Builders<TelemetryStream>.Filter.Eq(y => y.StreamId, "asdf"), Builders<TelemetryStream>.Update.Combine(Builders<TelemetryStream>.Update.Set(y => y.End, 123), Builders<TelemetryStream>.Update.Set(y => y.Start, 121))),
            new UpdateOneModel<TelemetryStream>(Builders<TelemetryStream>.Filter.Eq(y => y.StreamId, "asdf"), Builders<TelemetryStream>.Update.Set(y => y.Status, StreamStatus.Aborted)),
            new UpdateOneModel<TelemetryStream>(Builders<TelemetryStream>.Filter.Eq(y => y.StreamId, "asdf"), Builders<TelemetryStream>.Update.Set(y => y.Parents, new List<string> {"a", "b"})),
            new UpdateOneModel<TelemetryStream>(Builders<TelemetryStream>.Filter.And(Builders<TelemetryStream>.Filter.Eq(y => y.StreamId, "asdf"),Builders<TelemetryStream>.Filter.Eq(y => y.Name, "stuff")), Builders<TelemetryStream>.Update.Set(y => y.Metadata, new Dictionary<string, string>() {{"a", "2"}, {"b", "2"}}))
        };

        // Act
        await repo.BulkWrite(streamUpdates);

        // Assert
    }
    
    [Fact]
    public async Task EventRepositoryQuickTests()
    {
        // Arrange
        SnowflakeSchemaRegistry.Register();
        var repo = CreateEventRepo();

        var streamUpdates = new List<WriteModel<TelemetryEvent>>()
        {
            new UpdateOneModel<TelemetryEvent>(Builders<TelemetryEvent>.Filter.Eq(y => y.Name, "oldname"), Builders<TelemetryEvent>.Update.Set(y => y.Name, "newname")),
            new UpdateOneModel<TelemetryEvent>(Builders<TelemetryEvent>.Filter.Eq(y => y.StreamId, "asdf"), Builders<TelemetryEvent>.Update.Set(y => y.Level, TelemetryEventLevel.Error)),
            new UpdateOneModel<TelemetryEvent>(Builders<TelemetryEvent>.Filter.And(Builders<TelemetryEvent>.Filter.Eq(y => y.StreamId, "asdf"),Builders<TelemetryEvent>.Filter.Eq(y => y.EventId, "evid")), Builders<TelemetryEvent>.Update.Set(y => y.Level, TelemetryEventLevel.Error)),
            new UpdateOneModel<TelemetryEvent>(Builders<TelemetryEvent>.Filter.Eq(y => y.StreamId, "asdf"), Builders<TelemetryEvent>.Update.Combine(Builders<TelemetryEvent>.Update.Set(y => y.Description, "har"), Builders<TelemetryEvent>.Update.Set(y => y.Location, "/new"))),
        };

        // Act
        await repo.BulkWrite(streamUpdates);

        // Assert
    }
}