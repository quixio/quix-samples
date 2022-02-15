namespace Bridge.Codemasters.Console.Readers.File
{
    public class FileDataPacket
    {
        public FileDataPacket(byte[] data, long pos)
        {
            Data = data;
            Pos = pos;
        }


        public byte[] Data { get; }
        public long Pos { get; }
    }
}