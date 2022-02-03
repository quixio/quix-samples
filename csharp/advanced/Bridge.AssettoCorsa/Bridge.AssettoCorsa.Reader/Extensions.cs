using System;
using System.Net;
using System.Net.Sockets;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;

namespace Bridge.AssettoCorsa.Reader
{
    static class Helpers
    {
        public static string RemoveFrom(this string s, char c)
        {
            var pos = s.IndexOf(c);
            return pos >= 0 ? s.Remove(pos) : s;
        }

        public static string ToJson(this object obj)
        {
            var options = new JsonSerializerOptions
            {
                WriteIndented = true
            };

            return JsonSerializer.Serialize(obj, options);
        }

        public static void Send (this UdpClient udpClient, IUdpCommand udpCommand)
        {
            var sendBytes = udpCommand.ToByteArray();
            udpClient.Send(sendBytes, sendBytes.Length);
        }

        public static bool Receive<T>(this UdpClient udpClient, T udpResponse, CancellationToken cancellationToken = default) where T: IUdpResponse
        {
            //IPEndPoint object will allow us to read datagrams sent from any source.
            IPEndPoint remoteIpEndPoint = new IPEndPoint(IPAddress.Any, 0);

            int delay = 1;
            while (udpClient.Available == 0 && !cancellationToken.IsCancellationRequested)
            {
                try
                {
                    Task.Delay(delay, cancellationToken).GetAwaiter().GetResult();
                }
                catch (OperationCanceledException)
                {
                    Console.WriteLine($"\nThe operation was cancelled by the user.");
                }

                if (cancellationToken.IsCancellationRequested) return false;

                if (delay < 1000) delay *= 10;
                else
                {
                    Console.Write(".");
                    return false;
                }
            }

            Byte[] receivedBytes = udpClient.Receive(ref remoteIpEndPoint);
            udpResponse.remoteIpEndPoint = remoteIpEndPoint;
            udpResponse.ReadFromBytes(receivedBytes);

            return true;
        }

    }
}
