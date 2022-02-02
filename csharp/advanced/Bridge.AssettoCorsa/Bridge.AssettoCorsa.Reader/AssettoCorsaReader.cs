using System;
using System.Net.Sockets;
using System.Threading;

namespace Bridge.AssettoCorsa.Reader
{
    public class AssettoCorsaReader
    {
        private readonly string hostname;
        private readonly int port;

        private long continuousTime = 0;
        private long lastLapTime = 0;
        private long firstLapTime = -1;
        private bool outLap = true;

        private CancellationToken cancellationToken;

        private HandshackerResponse response;

        public AssettoCorsaReader(string hostname, int port)
        {
            this.hostname = hostname;
            this.port = port;
        }

        public Action<HandshackerResponse> OnSessionStart { get; set; }
        public Action OnSessionFinish { get; set; }
        public Action<long, int, DataResponse> OnDataReceived { get; set; }
        public Action<long, int, long, bool> OnLapCompleted { get; set; }

        public void Start(CancellationToken cancellationToken = default)
        {
            this.cancellationToken = cancellationToken;

            UdpClient udpClient = new UdpClient(port+1);
            try
            {
                Console.WriteLine($"Hostname: {this.hostname}");
                Console.WriteLine($"Port UPD: {this.port}");
                Console.WriteLine($"Connecting to Assetto Corsa  ...");

                udpClient.Connect(hostname, port);

                while (!cancellationToken.IsCancellationRequested)
                {
                    if (ConnectToAssettoCorsa(udpClient))
                    {
                        ReadDataFromAssettoCorsa(udpClient);
                    }
                }

            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
            }
        }

        private bool ConnectToAssettoCorsa(UdpClient udpClient)
        {
            response = new HandshackerResponse();

            do
            {
                udpClient.Send(new HandshakerCommand(HandshackerCommandOperation.DISMISS));
                udpClient.Send(new HandshakerCommand(HandshackerCommandOperation.HANDSHAKE));
                udpClient.Receive(response, cancellationToken);

                if (this.cancellationToken.IsCancellationRequested) return false;
                if (response.Identifier == 4242) break;
                if (response.Identifier == 0) continue;

                Console.WriteLine("Received incorrect handshack message:");
                Console.WriteLine(response.ToJson());
                Thread.Sleep(1000);
            }
            while (true);

            Console.WriteLine("This is the handshack message received:");
            Console.WriteLine(response.ToJson());
            Console.WriteLine($"This message was sent from {response.remoteIpEndPoint.Address.ToString()} on their port number {response.remoteIpEndPoint.Port.ToString()}");

            return true;
        }

        private void ReadDataFromAssettoCorsa(UdpClient udpClient)
        {
            this.SessionStart();

            udpClient.Send(new HandshakerCommand(HandshackerCommandOperation.SUBSCRIBE_UPDATE));

            var data = new DataResponse();

            while (!this.cancellationToken.IsCancellationRequested)
            {
                if (!udpClient.Receive(data, cancellationToken)) break;

                if (firstLapTime == -1)
                {
                    firstLapTime = data.LapTime;
                }

                if (lastLapTime == data.LapTime) continue;

                if (lastLapTime > data.LapTime)
                {
                    continuousTime += this.lastLapTime;

                    if (data.LastLap != 0)
                    {
                        this.OnLapCompleted?.Invoke(this.continuousTime, data.LapCount, data.LastLap, data.BestLap == data.LastLap);
                    }
                    else
                    {
                        outLap = false;
                    }

                    if (data.LapCount == 0 && data.Gas == 0 && data.Gear == 0)
                    {
                        this.OnSessionFinish?.Invoke();
                        this.SessionStart();
                    }
                }

                lastLapTime = data.LapTime;

                var lapNumber = outLap ? 0 : data.LapCount + 1;
                this.OnDataReceived?.Invoke(this.continuousTime + data.LapTime - firstLapTime, lapNumber, data);
            }

            udpClient.Send(new HandshakerCommand(HandshackerCommandOperation.DISMISS));

            this.OnSessionFinish?.Invoke();
        }

        void SessionStart()
        {
            this.OnSessionStart?.Invoke(response);
            continuousTime = 0;
            lastLapTime = 0;
            firstLapTime = -1;
            outLap = true;
        }
    }
}
