using System;
using System.IO;
using System.Net;
using System.Threading;
using System.Threading.Tasks;
using Bridge.Codemasters.Console.Configuration;
using Bridge.Codemasters.Console.Readers;
using Bridge.Codemasters.Console.Readers.File;
using Bridge.Codemasters.Console.Readers.Udp;
using Bridge.Codemasters.Quix;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Logging.Abstractions;
using Logging = Quix.Sdk.Logging;

namespace Bridge.Codemasters.Console
{
    class Program
    {
        private static CancellationTokenSource cToken = new CancellationTokenSource();
        private static FileWriter _fileWriter;
        private static bool loop = false;

        static void Main(string[] args)
        {
            var logger = Logging.CreateLogger<Program>();
            var configuration = new ConfigurationBuilder().AddJsonFile("appsettings.json", false).Build();
            var consoleConfig = new ConsoleConfig();
            configuration.Bind(consoleConfig);
            
            var streamingService = new StreamingService(consoleConfig.QuixConfig.Topic,
                consoleConfig.QuixConfig.Security.Token,
                consoleConfig.StreamSettings.IncludeOtherDrivers);
            do
            {
                cToken = new CancellationTokenSource();

                System.Console.CancelKeyPress += ConsoleCancelKeyPressHandler;

                IReader reader = SetupOutput(consoleConfig);
                reader.DataPacketRead += (sender, packet) =>
                {
                    var converted = PacketConverter.Convert(packet);
                    streamingService.AddData(converted);
                };
                
                reader.Finished += (sender, eventArgs) => cToken.Cancel(false);
                reader.Open();
                logger.LogInformation("Reader open");

                try
                {
                    Task.Delay(-1, cToken.Token).GetAwaiter().GetResult();
                }
                catch
                {

                }

                if (loop)
                {
                    logger.LogInformation("Looping!");
                }
                reader.Close();
            } while (loop);

            logger.LogInformation("Closing Stream");
            streamingService.Close();
            _fileWriter?.Dispose();
            logger.LogInformation("Closed!");
        }

        private static void OutputDataPacketReadHandler(object sender, byte[] e)
        {
            _fileWriter.Write(e);
        }
        
        private static IReader SetupOutput(ConsoleConfig config)
        {
            if (config.Input.Equals("udp"))
            {
                return SetupUdpOutput(config);
            }

            return SetupFileReader(config);
        }
        
        private static IReader SetupUdpOutput(ConsoleConfig config)
        {
            IReader reader = new UdpReader(new NullLogger<UdpReader>(), IPAddress.Any, config.UdpInput.Port);
            if (config.UdpInput.RecordToFile.Enabled)
            {
                Directory.CreateDirectory(config.UdpInput.RecordToFile.Folder);
                var path = Path.Combine(config.UdpInput.RecordToFile.Folder,
                    $"{config.UdpInput.RecordToFile.FilePrefix}_UDP_Recording_{DateTime.Now.ToString("yyyy_MM_dd_HH_mm_ss")}.bin");
                _fileWriter = new FileWriter(path);
                reader.DataPacketRead += OutputDataPacketReadHandler;
            }

            return reader;
        }

        private static IReader SetupFileReader(ConsoleConfig config)
        {
            IReader reader = new FileReader(config.FileInput.FilePaths, config.FileInput.TimeDivider);
            return reader;
        }

        private static void ConsoleCancelKeyPressHandler(object sender, ConsoleCancelEventArgs e)
        {
            e.Cancel = true;
            cToken.Cancel(false);
        }
    }
}