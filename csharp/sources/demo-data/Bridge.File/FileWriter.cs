using System;
using System.IO;

namespace Bridge.File
{
    public class FileWriter : IDisposable
    {
        private BinaryWriter binaryWriter;
        private object writeLock = new object();
        private string Version = "1.0.0";

        public FileWriter(string filePath)
        {
            this.binaryWriter = new BinaryWriter(System.IO.File.Open(filePath, FileMode.Create));
            this.binaryWriter.Write(Version);
        }
        
        /// <summary>
        /// Writes data at a given time
        /// </summary>
        /// <param name="data">The data to write to the file</param>
        /// <param name="time">Optional time. If not provided, defaults to <see cref="DateTime.UtcNow"/></param>
        public void Write(byte[] data, DateTime? time = null)
        {
            time = time ?? DateTime.UtcNow;
            lock (writeLock)
            {
                this.binaryWriter.Write(time.Value.ToBinary());
                this.binaryWriter.Write(data.Length);
                this.binaryWriter.Write(data);
            }
        }

        public void Dispose()
        {
            binaryWriter.Dispose();
        }
    }
}