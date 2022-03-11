using System;
using System.Diagnostics;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using Quix.Sdk;

namespace Bridge.File
{
    public class Version1Reader
    {
        private readonly string version;
        private readonly double playbackRate;
        private ILogger logger;
        public event EventHandler<byte[]> DataPacketRead;

        public Version1Reader(string version, double playbackRate)
        {
            this.logger = Logging.CreateLogger<Version1Reader>();
            this.version = version;
            this.playbackRate = playbackRate;
        }

        public async Task Read(BinaryReader reader, CancellationToken cancellationToken)
        {
            Console.WriteLine("Version 1");
            var sw = Stopwatch.StartNew();
            long? first = null;
            while (!cancellationToken.IsCancellationRequested && reader.BaseStream.Position != reader.BaseStream.Length)
            {
                var ms = ToMsFromBinary(reader.ReadInt64()); 
                first = first ?? ms;
                var timeToWait = TimeSpan.FromMilliseconds(TimeHelper.TimeToWait(first.Value, sw.ElapsedMilliseconds, ms, playbackRate)).TotalMilliseconds;
                logger.LogTrace("Elapsed: {0}ns, Target time: {1}ns, PlaybackRate: {2}. To wait: {3}ms", sw.ElapsedMilliseconds, (ms-first.Value), playbackRate, timeToWait);
                if (timeToWait > 10)
                {
                    await Task.Delay((int) timeToWait, cancellationToken);
                }
                var pos = reader.BaseStream.Position;
                var length = reader.ReadInt32();
                if (length + reader.BaseStream.Position > reader.BaseStream.Length)
                {
                    break; // invalid data
                }
                var bytes = reader.ReadBytes(length);
                        
                var packet = new FileDataPacket(bytes, pos);
                        
                DataPacketRead?.Invoke(this, packet.Data);
            }
        }

        private static long ToMsFromBinary(long binary)
        {
            var epoch = new DateTime(1970, 01, 01);
            var date = DateTime.FromBinary(binary);
            return (long)((date - epoch).TotalMilliseconds);
        }
    }
}