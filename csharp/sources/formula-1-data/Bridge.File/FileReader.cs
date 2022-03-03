using System;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using Bridge.Readers;
using Microsoft.Extensions.Logging;
using Quix.Sdk;

namespace Bridge.File
{
    public class FileReader : IReader
    {
        private string[] filePaths;
        private readonly double timeDivider;
        private CancellationTokenSource cTokenSource;
        private bool isOpen;
        private object openLock = new object();
        private ILogger logger;

        /// <summary>
        /// Initializes a new instance of <see cref="FileReader"/>
        /// </summary>
        /// <param name="filePaths">The path for the files to play back</param>
        /// <param name="timeDivider">The number to divide the time difference between two data packets.  1 = Real Time, anything greater than 1 is faster than real time, anything less than 1 is slower than real time. 0 or less being as fast as possible</param>
        /// 
        public FileReader(string[] filePaths, double timeDivider)
        {
            this.logger = Logging.CreateLogger<FileReader>();
            this.filePaths = filePaths;
            this.timeDivider = timeDivider;
        }
        
        /// <summary>
        /// Initializes a new instance of <see cref="FileReader"/>
        /// </summary>
        /// <param name="filePath">The path for the file to play back</param>
        /// <param name="timeDivider">The number to divide the time difference between two data packets.  1 = Real Time, anything greater than 1 is faster than real time, anything less than 1 is slower than real time. 0 or less being as fast as possible</param>
        public FileReader(string filePath, double timeDivider) : this(new [] {filePath}, timeDivider)
        {
        }
        
        public event EventHandler<byte[]> DataPacketRead;
        public event EventHandler Finished;

        public void Open()
        {
            if (this.isOpen) return;
            lock (this.openLock)
            {
                if (this.isOpen) return;
                foreach (var filePath in filePaths)
                {
                    if (!System.IO.File.Exists(filePath))
                    {
                        throw new FileNotFoundException("File not found", filePath);
                    }   
                }
                this.isOpen = true;
            }
            this.cTokenSource = new CancellationTokenSource();

            Task.Run(ReadFile);
        }

        private async Task ReadFile()
        {
            foreach (var filePath in filePaths)
            {
                if (cTokenSource.Token.IsCancellationRequested) break;
                using (var reader = new BinaryReader(System.IO.File.Open(filePath, FileMode.Open)))
                {
                    var fileVersion = reader.ReadString();
                    if (fileVersion.Split('.').Length != 3)
                    {
                        // not a version string, maybe it is file before versioning
                        fileVersion = "0.0.0";
                        reader.BaseStream.Position = 0;
                    }

                    switch (fileVersion.Split('.')[0])
                    {
                        case "0": {
                            if (this.timeDivider != 0)
                            {
                                this.logger.LogWarning("{0} does not support playback speed.", filePath);
                            }
                            var versionReader = new Version0Reader(fileVersion);
                            versionReader.DataPacketRead += (s, e) => { DataPacketRead?.Invoke(this, e); };
                            versionReader.Read(reader, cTokenSource.Token);
                            break;
                        }
                        case "1": {
                            var speed =  1 * this.timeDivider * 100;
                            if (speed == 0) speed = Double.PositiveInfinity;
                            this.logger.LogInformation("{0} will be played back at {1:0}% speed", filePath, speed);
                            var versionReader = new Version1Reader(fileVersion, this.timeDivider);
                            versionReader.DataPacketRead += (s, e) => { DataPacketRead?.Invoke(this, e); };
                            await versionReader.Read(reader, cTokenSource.Token);
                            this.logger.LogInformation("Version 1 finished");
                            break;
                        }                        
                    }
                }
            }
            
            if (!this.isOpen) return;
            lock (this.openLock)
            {
                if (!this.isOpen) return;
                this.isOpen = false;
            }
            
            Finished?.Invoke(this, EventArgs.Empty);
        }

        public void Close()
        {
            if (!this.isOpen) return;
            lock (this.openLock)
            {
                if (!this.isOpen) return;
                this.isOpen = false;
            }
            
            this.cTokenSource.Cancel(false);
        }
    }
}