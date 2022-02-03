using System;

namespace Bridge.Codemasters.Console.Configuration
{
    public class RecordToFile
    {
        /// <summary>
        /// Whether the data should be recorded to a file
        /// </summary>
        public bool Enabled { get; set; }
        
        /// <summary>
        /// The root folder
        /// </summary>
        public string Folder { get; set; }
        
        /// <summary>
        /// The file prefix to use for the file created. The files will have the first packet arrival time suffixed to it.
        /// </summary>
        public string FilePrefix { get; set; }
    }

    public class UDPInput
    {
        /// <summary>
        /// The port to listen to
        /// </summary>
        public ushort Port { get; set; }
        
        
        /// <summary>
        /// Record settings
        /// </summary>
        public RecordToFile RecordToFile { get; set; }
    }

    public class FileInput
    {
        /// <summary>
        /// The files to play back
        /// </summary>
        public string[] FilePaths { get; set; }
        
        /// <summary>
        /// The divider for the playback speed. 1 = Normal, 2 = 2x fast, 0.5 = half speed, 0 = as fast as possible
        /// </summary>
        public double TimeDivider { get; set; }
    }

    public class Security
    {
        public string Token { get; set; }
    }

    public class StreamSettings
    {
        /// <summary>
        /// Whether other drivers in a session should be included or only player
        /// </summary>
        public bool IncludeOtherDrivers { get; set; }
    }

    public class QuixConfig
    {
        public string Topic { get; set; }
        public Security Security { get; set; }
    }

    public class ConsoleConfig
    {
        private string _input;

        public string Input
        {
            get => _input;
            set
            {
                _input = value.ToLower();
                if (_input != "udp" && _input != "file")
                {
                    throw new ArgumentOutOfRangeException("Input type must be 'udp' or 'file'");
                }
            }
        }

        public StreamSettings StreamSettings { get; set; }
        
        public UDPInput UdpInput { get; set; }
        public FileInput FileInput { get; set; }
        public QuixConfig QuixConfig { get; set; }
    }
}