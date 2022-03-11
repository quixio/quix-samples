using System;
using System.Collections.Generic;
using System.Threading;
using NUnit.Framework;
using QuixTracker.Services;

namespace StreamWriterTests
{
    public class Tests
    {
        [SetUp]
        public void Setup()
        {
        }

        [Test]
        public void Test1()
        {
            ConnectionService connectionService = new ConnectionService();
            QuixService service = new QuixService(connectionService);

            var xxx = service.StartOutputConnection();
            //this.outputConnection = CreateWebSocketConnection("writer");
            
            var streamId = service.CreateStream("device1", "rider1", "team1", "session1").Result;

            for (int x = 0; x < 2000; x++)
            {
                var timestamp =
                    (long) (DateTime.UtcNow - new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc)).TotalMilliseconds *
                    1000000;

                service.SendParameterData(streamId, new ParameterDataDTO
                {
                    Timestamps = new long[] {timestamp},
                    NumericValues = new Dictionary<string, double[]>()
                    {
                        {"Temperature", new double[] {x}}
                    }
                });
                Thread.Sleep(10);
            }

            Assert.Pass();
        }
    }
}