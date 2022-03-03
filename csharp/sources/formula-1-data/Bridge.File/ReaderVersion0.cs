using System;
using System.IO;
using System.Threading;

namespace Bridge.File
{
    public class Version0Reader
    {
        private readonly string version;
        public event EventHandler<byte[]> DataPacketRead;

        public Version0Reader(string version)
        {
            this.version = version;
        }

        public void Read(BinaryReader reader, CancellationToken cancellationToken)
        {
            while (!cancellationToken.IsCancellationRequested && reader.BaseStream.Position != reader.BaseStream.Length)
            {
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