using System;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using Microsoft.Extensions.Logging;

namespace Bridge.Codemasters.Console.Readers.Udp
{
    public class UdpReader : IReader
    {
        private IPAddress listenAddress;
        private ushort port;
        private bool isOpen;
        private object openLock = new object();
        private ILogger<UdpReader> logger;

        private CancellationTokenSource cTokenSource;

        public UdpReader(ILogger<UdpReader> logger, IPAddress listenAddress, ushort port)
        {
            this.logger = logger;
            this.listenAddress = listenAddress;
            this.port = port;
        }

        public event EventHandler<byte[]> DataPacketRead;
        public event EventHandler Finished;

        public void Open()
        {
            if (isOpen) return;
            lock (openLock)
            {
                if (isOpen) return;
                isOpen = true;
            }
            cTokenSource = new CancellationTokenSource();
            var endpoint= new IPEndPoint(this.listenAddress,this.port);
            var socket = new Socket(AddressFamily.InterNetwork, SocketType.Dgram, ProtocolType.Udp);
            socket.Bind(endpoint);
            this.logger.LogInformation("Socket bound with {0}:{1}", this.listenAddress, this.port);

            var state = new StateObject();
            state.Endpoint = new IPEndPoint(IPAddress.Any, 0);
            state.Socket = socket;
            socket.BeginReceiveFrom(state.Buffer, 0, StateObject.BufferSize, 0, ref state.Endpoint, ReceiveCallback, state);
        }

        private void ReceiveCallback(IAsyncResult ar)
        {
            var state = (StateObject) ar.AsyncState;  
            var socket = state.Socket;
            var bytesRead = socket.EndReceive(ar);
            var msg = new byte[bytesRead];
            Array.Copy(state.Buffer, 0, msg, 0, bytesRead);
            
            this.logger.LogTrace("Message received from {0}:", state.Endpoint);
            var packet = new UdpDataPacket(msg, state.Endpoint.ToString());

            if (!this.cTokenSource.Token.IsCancellationRequested)
            {
                socket.BeginReceiveFrom(state.Buffer, 0, StateObject.BufferSize, 0, ref state.Endpoint, ReceiveCallback,
                    state);
            }

            this.DataPacketRead?.Invoke(this, packet.Data);

            if (this.cTokenSource.Token.IsCancellationRequested)
            {
                Finished?.Invoke(this, EventArgs.Empty);
            }
        }

        public void Close()
        {
            if (!isOpen) return;
            lock (openLock)
            {
                if (!isOpen) return;
                isOpen = false;
            }
            
            cTokenSource.Cancel(false);
        }
    }
}