using System.Net;
using System.Net.Sockets;

namespace Bridge.Codemasters.Console.Readers.Udp
{
    internal class StateObject
    {
        // Size of receive buffer.  
        public const int BufferSize = 8192;

        // Receive buffer.  
        public byte[] Buffer = new byte[BufferSize];

        public EndPoint Endpoint;

        // Client  socket.  
        public Socket Socket = null;
    }
}