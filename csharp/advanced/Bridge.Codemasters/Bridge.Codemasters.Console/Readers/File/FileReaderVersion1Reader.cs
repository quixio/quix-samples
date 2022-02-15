using System;
using System.Diagnostics;
using System.IO;
using System.Threading;
using System.Threading.Tasks;

namespace Bridge.Codemasters.Console.Readers.File
{
    public class Version1Reader
    {
        private readonly string version;
        private readonly double timeDivider;
        public event EventHandler<byte[]> DataPacketRead;

        public Version1Reader(string version, double timeDivider)
        {
            this.version = version;
            this.timeDivider = timeDivider;
        }

        public async Task Read(BinaryReader reader, CancellationToken cancellationToken)
        {
            var sw = Stopwatch.StartNew();
            long? first = null;
            while (!cancellationToken.IsCancellationRequested && reader.BaseStream.Position != reader.BaseStream.Length)
            {
                var binaryTime = reader.ReadInt64();
                first = first ?? binaryTime;
                var timeToWait = TimeSpan.FromTicks(TimeHelper.TimeToWait(first.Value, sw.ElapsedTicks, binaryTime, timeDivider)).TotalMilliseconds;
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
    }
}