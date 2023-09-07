using System;
using Bridge.Codemasters.Quix.V2019;
using Bridge.Codemasters.V2019.Models;
using QuixStreams.Streaming;

namespace Bridge.Codemasters.Quix
{
    public class StreamingService
    {
        private readonly StreamingService2019 streamingService2019;
        private readonly object addLock = new object();

        public StreamingService(string topic, bool includeOtherDrivers, string streamId)
        {
            var client = new QuixStreamingClient();
            this.streamingService2019 = new StreamingService2019(client, topic, includeOtherDrivers, streamId);
        }

        public void AddData(ICodemastersPacket converted)
        {
            if (converted == null) return;
            try
            {

                lock (addLock)
                {
                    switch (converted.Version)
                    {
                        case PacketVersion.V2019:
                            streamingService2019.AddData((I2019CodemastersPacket) converted);
                            return;
                        default:
                            throw new ArgumentOutOfRangeException();
                    }
                }
            }
            catch (Exception ex)
            {
                System.Console.Write(ex.ToString());
            }
        }

        public void Close()
        {
            this.streamingService2019.Close();
        }
    }
}