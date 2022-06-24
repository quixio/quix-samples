using System;

namespace Bridge.Readers
{
    public interface IReader
    {
        event EventHandler<byte[]> DataPacketRead;

        event EventHandler Finished;

        void Open();

        void Close();
    }
}