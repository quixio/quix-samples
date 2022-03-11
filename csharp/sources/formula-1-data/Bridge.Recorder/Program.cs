using System;
using System.IO;
using System.Net;
using System.Threading;
using System.Threading.Tasks;
using Bridge.File;
using Bridge.Readers;
using Bridge.Udp;
using Microsoft.Extensions.Logging.Abstractions;

namespace Bridge.Recorder
{
    class Program
    {
        private static CancellationTokenSource cToken = new CancellationTokenSource();
        private static FileWriter _fileWriter;
        
        static void Main(string[] args)
        {
            
            System.Console.CancelKeyPress += ConsoleCancelKeyPressHandler;

            var path = Path.Combine(Environment.CurrentDirectory, $"UDP_Recording_{DateTime.Now.ToString("yyyy_MM_dd_HH_mm_ss")}.bin");
            using (_fileWriter = new FileWriter(path))
            {

                IReader reader = new UdpReader(new NullLogger<UdpReader>(), IPAddress.Any, 20777);
                reader.DataPacketRead += OutputDataPacketReadHandler;

                reader.Open();
                System.Console.WriteLine("Output open");

                try
                {
                    Task.Delay(-1, cToken.Token).GetAwaiter().GetResult();
                }
                catch
                {

                }

                System.Console.WriteLine("Closing Output");
                reader.Close();
            }
        }

        private static void ConsoleCancelKeyPressHandler(object sender, ConsoleCancelEventArgs e)
        {
            e.Cancel = true;
            cToken.Cancel(false);
        }

        private static void OutputDataPacketReadHandler(object sender, byte[] e)
        {
            _fileWriter.Write(e);
            System.Console.WriteLine("Recorded data with length of {0}", e.Length);
        }
    }
}