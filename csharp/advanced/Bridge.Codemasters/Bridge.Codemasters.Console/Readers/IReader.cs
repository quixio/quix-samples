using System;

namespace Bridge.Codemasters.Console.Readers
{
    public interface IReader
    {
        event EventHandler<byte[]> DataPacketRead;

        event EventHandler Finished;

        void Open();

        void Close();
    }
}