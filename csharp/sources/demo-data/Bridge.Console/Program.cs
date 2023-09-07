using System;
using System.IO;
using System.Net;
using System.Threading;
using System.Threading.Tasks;
using Bridge.Codemasters.Quix;
using Bridge.Console.Configuration;
using Bridge.File;
using Bridge.Readers;
using Bridge.Udp;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Logging.Abstractions;
using QuixStreams;

namespace Bridge.Codemasters.Console
{
    class Program
    {
        private static CancellationTokenSource cts = new CancellationTokenSource();
        private static CancellationTokenSource cToken = new CancellationTokenSource();
        private static FileWriter _fileWriter;

        static void Main(string[] args)
        {
            System.Console.CancelKeyPress += ConsoleCancelKeyPressHandler;

            AppDomain.CurrentDomain.ProcessExit += (s, e) =>
            {
                System.Console.WriteLine("Exiting ...");
                cToken.Cancel(false);
            };

            try
            {
                var logger = Logging.CreateLogger<Program>();
                var builder = new ConfigurationBuilder()
                    .SetBasePath(Directory.GetCurrentDirectory())
                    .AddJsonFile("appsettings.json")
                    .AddEnvironmentVariables();

                var appConfiguration = new AppConfiguration();
                var config = builder.Build();
                config.Bind(appConfiguration);

                string streamId = Guid.NewGuid().ToString();

                var streamingService = new StreamingService(appConfiguration.Topic,
                    appConfiguration.StreamSettings.IncludeOtherDrivers,
                    streamId
                    );

                var startedAt = DateTime.UtcNow;
                var connected = false;
                var loop = false;
                do
                {
                    loop = false;
                    var readerFinished = false;

                    cToken = new CancellationTokenSource();

                    IReader reader = SetupOutput(appConfiguration);

                    EventHandler<byte[]> dataPacketHandler;

                    reader.DataPacketRead += dataPacketHandler = (sender, packet) =>
                    {
                        var converted = PacketConverter.Convert(packet);
                        streamingService.AddData(converted);
                    };

                    EventHandler finishedHandler;

                    reader.Finished += finishedHandler = (sender, eventArgs) =>
                    {
                        readerFinished = true;
                        cToken.Cancel(false);
                    };

                    reader.Open();
                    logger.LogInformation("Reader open");

                    if (!connected)
                    {
                        System.Console.WriteLine("CONNECTED!");
                        connected = true;
                    }

                    try
                    {
                        Task.Delay(-1, cToken.Token).GetAwaiter().GetResult();
                    }
                    catch
                    {

                    }

                    reader.DataPacketRead -= dataPacketHandler;

                    var timeElapsed = DateTime.UtcNow - startedAt;
                    if (readerFinished && timeElapsed < TimeSpan.FromHours(8))
                    {
                        reader.Finished -= finishedHandler;
                        logger.LogInformation("Looping!");
                        loop = true;
                    }

                    reader.Close();

                } while (loop);

                logger.LogInformation("Closing Stream");
                streamingService.Close();
                _fileWriter?.Dispose();
                logger.LogInformation("Closed!");
            }
            catch (Exception ex)
            {
                System.Console.WriteLine("ERROR: {0}", ex.Message);
                Environment.ExitCode = -1;
                cts.Token.WaitHandle.WaitOne();
            }

        }

        private static void OutputDataPacketReadHandler(object sender, byte[] e)
        {
            _fileWriter.Write(e);
        }
        
        private static IReader SetupOutput(AppConfiguration config)
        {
            if (config.Input.Equals("udp"))
            {
                return SetupUdpOutput(config);
            }

            return SetupFileReader(config);
        }
        
        private static IReader SetupUdpOutput(AppConfiguration config)
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

        private static IReader SetupFileReader(AppConfiguration config)
        {
            IReader reader = new FileReader(config.FileInput.FilePaths, config.FileInput.PlaybackRate);
            return reader;
        }

        public static void ConsoleCancelKeyPressHandler(object sender, ConsoleCancelEventArgs e)
        {
            e.Cancel = true;
            cToken.Cancel(false);
        }
    }
}