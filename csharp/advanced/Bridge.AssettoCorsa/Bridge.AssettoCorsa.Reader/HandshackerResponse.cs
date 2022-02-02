using System;
using System.IO;
using System.Net;
using System.Text;
using System.Text.Json.Serialization;

namespace Bridge.AssettoCorsa.Reader
{
    /// <summary>
    /// https://docs.google.com/document/d/1KfkZiIluXZ6mMhLWfDX1qAGbvhGRC3ZUzjVIt5FQpp4/pub
    /// </summary>
    public class HandshackerResponse : IUdpResponse
    {
        public string CarName { get; set; }
        public string DriverName { get; set; }
        public int Identifier { get; set; }
        public int Version { get; set; }
        public string TrackName { get; set; } 
        public string TrackConfig { get; set; }

        [JsonIgnore]
        public IPEndPoint remoteIpEndPoint { get; set; }

        public void ReadFromBytes(byte[] bytes)
        {
            var reader = new BinaryReader(new MemoryStream(bytes));

            this.CarName = Encoding.Unicode.GetString(reader.ReadBytes(100)).RemoveFrom('%').RemoveFrom('\u0000'); 
            this.DriverName = Encoding.Unicode.GetString(reader.ReadBytes(100)).RemoveFrom('%').RemoveFrom('\u0000');
            this.Identifier = reader.ReadInt32();
            this.Version = reader.ReadInt32();
            this.TrackName = Encoding.Unicode.GetString(reader.ReadBytes(100)).RemoveFrom('%').RemoveFrom('\u0000');
            this.TrackConfig = Encoding.Unicode.GetString(reader.ReadBytes(100)).RemoveFrom('%').RemoveFrom('\u0000');
        }
    };
}
