using System.Net;

namespace Bridge.AssettoCorsa.Reader
{
    public interface IUdpResponse
    {
        IPEndPoint remoteIpEndPoint { get; set; }

        void ReadFromBytes(byte[] bytes);
    }
}