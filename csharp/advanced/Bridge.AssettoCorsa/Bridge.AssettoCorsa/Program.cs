using Quix.Sdk.Process.Models;
using Quix.Sdk.Process.Models.Utility;
using Quix.Sdk.Streaming;
using Bridge.AssettoCorsa.Reader;
using System;
using System.Threading;

namespace Bridge.AssettoCorsa
{
    class Program
    {
        private static readonly CancellationTokenSource cToken = new CancellationTokenSource();

        private static IStreamWriter stream;
        private static IOutputTopic outputTopic;

        static void Main()
        {
            System.Console.CursorVisible = false;
            System.Console.CancelKeyPress += ConsoleCancelKeyPressHandler;

            var outputTopicName = Environment.GetEnvironmentVariable("output");

            // Quix output topic
            outputTopic = new QuixStreamingClient().OpenOutputTopic(outputTopicName);

            var acServer = Environment.GetEnvironmentVariable("HostName");
            var acPort = Environment.GetEnvironmentVariable("Port") ?? "0";

            // Data Source reader
            var ACReader = new AssettoCorsaReader(acServer, int.Parse(acPort));
            ACReader.OnSessionStart += OnSessionStart;
            ACReader.OnSessionFinish += OnSessionFinish;
            ACReader.OnDataReceived += OnDataReceived;
            ACReader.OnLapCompleted += OnLapCompleted;
            ACReader.Start(cToken.Token);

            // Close stream
            stream?.Close();
        }

        // Stream properties and Metadata
        private static void OnSessionStart(HandshackerResponse data)
        {
            // Create new stream
            stream = outputTopic.CreateStream();

            // Set stream properties
            stream.Properties.TimeOfRecording = DateTime.UtcNow;
            stream.Properties.Name = $"Assetto Corsa - {data.DriverName} - {data.TrackName} - {data.CarName} {DateTime.UtcNow:yyyy-MM-dd-HH:mm:ss}";
            stream.Properties.Location = $"/Game/Kunos/AssettoCorsa/{data.TrackName}/{data.DriverName}";

            stream.Properties.Metadata["Driver"] = $"{data.DriverName}";
            stream.Properties.Metadata["Car"] = $"{data.CarName}";
            stream.Properties.Metadata["Track Name"] = $"{data.TrackName}";
            stream.Properties.Metadata["Track Configuration"] = $"{data.TrackConfig}";
            stream.Properties.Metadata["AC Server Version"] = $"{data.Version}";

            // Some extra configuration tune
            stream.Epoch = DateTime.UtcNow;
            stream.Parameters.Buffer.PacketSize = 100;
            stream.Parameters.Buffer.BufferTimeout = 1000;
            stream.Parameters.Buffer.DefaultTags["Default1"] = "1";
            stream.Parameters.Buffer.DefaultTags["Default2"] = "2";
            stream.Events.DefaultTags["Default1"] = "1";
            stream.Events.DefaultTags["Default2"] = "2";

            // Definitions
            SetParameterDefinitions();
            SetEventDefinitions();

            Console.WriteLine($"** Stream created. StreamId = {stream.StreamId}, Name = {stream.Properties.Name}");
        }

        private static void OnSessionFinish()
        {
            // Close stream
            stream?.Close();
            Console.WriteLine($"** Stream closed. StreamId = {stream.StreamId}, Name = {stream.Properties.Name}");
        }

        // Telemetry Data and tagging
        private static void OnDataReceived(long time, int lapNumber, DataResponse data)
        {
            stream.Parameters.Buffer.AddTimestampMilliseconds(time)
                .AddValue("speed_Kmh", data.Speed_Kmh)
                .AddValue("speed_Mph", data.Speed_Mph)
                .AddValue("speed_Ms", data.Speed_Ms)

                .AddValue("isAbsEnabled", Convert.ToDouble(data.IsAbsEnabled))
                .AddValue("isAbsInAction", Convert.ToDouble(data.IsAbsInAction))
                .AddValue("isTcInAction", Convert.ToDouble(data.IsTcInAction))
                .AddValue("isTcEnabled", Convert.ToDouble(data.IsTcEnabled))
                .AddValue("isInPit", Convert.ToDouble(data.IsInPit))
                .AddValue("isEngineLimiterOn", Convert.ToDouble(data.IsEngineLimiterOn))

                .AddValue("accG_vertical", data.AccG_vertical)
                .AddValue("accG_horizontal", data.AccG_horizontal)
                .AddValue("accG_frontal", data.AccG_frontal)

                .AddValue("lapTime", data.LapTime)
                .AddValue("lastLap", data.LastLap)
                .AddValue("bestLap", data.BestLap)
                .AddValue("lapCount", data.LapCount)

                .AddValue("gas", data.Gas)
                .AddValue("brake", data.Brake)
                .AddValue("clutch", data.Clutch)
                .AddValue("engineRPM", data.EngineRPM)
                .AddValue("steer", data.Steer)
                .AddValue("gear", data.Gear)
                .AddValue("cgHeight", data.CgHeight)

                .AddValue("wheelAngularSpeed.wheel1", data.WheelAngularSpeed.Wheel1)
                .AddValue("wheelAngularSpeed.wheel2", data.WheelAngularSpeed.Wheel2)
                .AddValue("wheelAngularSpeed.wheel3", data.WheelAngularSpeed.Wheel3)
                .AddValue("wheelAngularSpeed.wheel4", data.WheelAngularSpeed.Wheel4)
                .AddValue("slipAngle.wheel1", data.SlipAngle.Wheel1)
                .AddValue("slipAngle.wheel2", data.SlipAngle.Wheel2)
                .AddValue("slipAngle.wheel3", data.SlipAngle.Wheel3)
                .AddValue("slipAngle.wheel4", data.SlipAngle.Wheel4)
                .AddValue("slipAngle_ContactPatch.wheel1", data.SlipAngle_ContactPatch.Wheel1)
                .AddValue("slipAngle_ContactPatch.wheel2", data.SlipAngle_ContactPatch.Wheel2)
                .AddValue("slipAngle_ContactPatch.wheel3", data.SlipAngle_ContactPatch.Wheel3)
                .AddValue("slipAngle_ContactPatch.wheel4", data.SlipAngle_ContactPatch.Wheel4)
                .AddValue("slipRatio.wheel1", data.SlipRatio.Wheel1)
                .AddValue("slipRatio.wheel2", data.SlipRatio.Wheel2)
                .AddValue("slipRatio.wheel3", data.SlipRatio.Wheel3)
                .AddValue("slipRatio.wheel4", data.SlipRatio.Wheel4)
                .AddValue("tyreSlip.wheel1", data.TyreSlip.Wheel1)
                .AddValue("tyreSlip.wheel2", data.TyreSlip.Wheel2)
                .AddValue("tyreSlip.wheel3", data.TyreSlip.Wheel3)
                .AddValue("tyreSlip.wheel4", data.TyreSlip.Wheel4)
                .AddValue("ndSlip.wheel1", data.NdSlip.Wheel1)
                .AddValue("ndSlip.wheel2", data.NdSlip.Wheel2)
                .AddValue("ndSlip.wheel3", data.NdSlip.Wheel3)
                .AddValue("ndSlip.wheel4", data.NdSlip.Wheel4)
                .AddValue("load.wheel1", data.Load.Wheel1)
                .AddValue("load.wheel2", data.Load.Wheel2)
                .AddValue("load.wheel3", data.Load.Wheel3)
                .AddValue("load.wheel4", data.Load.Wheel4)
                .AddValue("Dy.wheel1", data.Dy.Wheel1)
                .AddValue("Dy.wheel2", data.Dy.Wheel2)
                .AddValue("Dy.wheel3", data.Dy.Wheel3)
                .AddValue("Dy.wheel4", data.Dy.Wheel4)
                .AddValue("Mz.wheel1", data.Mz.Wheel1)
                .AddValue("Mz.wheel2", data.Mz.Wheel2)
                .AddValue("Mz.wheel3", data.Mz.Wheel3)
                .AddValue("Mz.wheel4", data.Mz.Wheel4)
                .AddValue("tyreDirtyLevel.wheel1", data.TyreDirtyLevel.Wheel1)
                .AddValue("tyreDirtyLevel.wheel2", data.TyreDirtyLevel.Wheel2)
                .AddValue("tyreDirtyLevel.wheel3", data.TyreDirtyLevel.Wheel3)
                .AddValue("tyreDirtyLevel.wheel4", data.TyreDirtyLevel.Wheel4)

                .AddValue("camberRAD.wheel1", data.CamberRAD.Wheel1)
                .AddValue("camberRAD.wheel2", data.CamberRAD.Wheel2)
                .AddValue("camberRAD.wheel3", data.CamberRAD.Wheel3)
                .AddValue("camberRAD.wheel4", data.CamberRAD.Wheel4)
                .AddValue("tyreRadius.wheel1", data.TyreRadius.Wheel1)
                .AddValue("tyreRadius.wheel2", data.TyreRadius.Wheel2)
                .AddValue("tyreRadius.wheel3", data.TyreRadius.Wheel3)
                .AddValue("tyreRadius.wheel4", data.TyreRadius.Wheel4)
                .AddValue("tyreLoadedRadius.wheel1", data.TyreLoadedRadius.Wheel1)
                .AddValue("tyreLoadedRadius.wheel2", data.TyreLoadedRadius.Wheel2)
                .AddValue("tyreLoadedRadius.wheel3", data.TyreLoadedRadius.Wheel3)
                .AddValue("tyreLoadedRadius.wheel4", data.TyreLoadedRadius.Wheel4)

                .AddValue("suspensionHeight.wheel1", data.SuspensionHeight.Wheel1)
                .AddValue("suspensionHeight.wheel2", data.SuspensionHeight.Wheel2)
                .AddValue("suspensionHeight.wheel3", data.SuspensionHeight.Wheel3)
                .AddValue("suspensionHeight.wheel4", data.SuspensionHeight.Wheel4)
                .AddValue("carPositionNormalized", data.CarPositionNormalized)
                .AddValue("carSlope", data.CarSlope)

                .AddValue("carCoordinates.x", data.CarCoordinates.X)
                .AddValue("carCoordinates.y", data.CarCoordinates.Y)
                .AddValue("carCoordinates.z", data.CarCoordinates.Z)

                .AddTag("Lap", lapNumber.ToString())
                .AddTag("isAbsEnabled", data.IsAbsEnabled.ToString())
                .AddTag("isAbsInAction", data.IsAbsInAction.ToString())
                .AddTag("isTcInAction", data.IsTcInAction.ToString())
                .AddTag("isTcEnabled", data.IsTcEnabled.ToString())
                .AddTag("isInPit", data.IsInPit.ToString())
                .AddTag("isEngineLimiterOn", data.IsEngineLimiterOn.ToString())

                .Write();

            Console.SetCursorPosition(0, Console.CursorTop);
            Console.Write($"-> Timestamp: {time} - LapNumber {lapNumber} - Steer: {data.Steer}".PadRight(Console.WindowWidth));
        }

        // Telemetry Events
        private static void OnLapCompleted(long time, int lapNumber, long lapTime, bool bestLap)
        {
            Console.SetCursorPosition(0, Console.CursorTop);
            Console.WriteLine($"** Lap completed Event. LapNumber = {lapNumber} - LapTime = {(lapTime * (long)1e6).FromNanoseconds().ToString()} - bestLap = {bestLap}");

            stream.Events.AddTimestampMilliseconds(time)
                .AddValue("LapCompleted", $"Lap {lapNumber} completed.")
                .AddValue("ExtraEvent", $"Extra event.")
                .AddTag("Tag1", "1")
                .AddTag("Tag2", "2")
                .AddTag("Tag3", "3")
                .Write();

            if (bestLap)
            {
                stream.Events.AddTimestampMilliseconds(time)
                    .AddValue("BestLap", $"Best Lap time {(lapTime * (long)1e6).FromNanoseconds().ToString()}.")
                    .Write();
            }
        }

        private static void SetParameterDefinitions()
        {
            stream.Parameters.DefaultLocation = "/";
            stream.Parameters.AddDefinition("lapTime", "Lap time", "Indicates the current lap time in progress");
            stream.Parameters.AddDefinition("lastLap", "Last Lap time", "Last lap time");
            stream.Parameters.AddDefinition("bestLap", "Best Lap time", "Indicates the best lap timeof the session");
            stream.Parameters.AddDefinition("lapCount", "Number of laps completed").SetUnit("lap");

            stream.Parameters.DefaultLocation = "/Ecu";
            stream.Parameters.AddDefinition("isAbsEnabled", "Abs is Enabled");
            stream.Parameters.AddDefinition("isAbsInAction", "Abs is in Action");
            stream.Parameters.AddDefinition("isTcInAction", "Traction control is in Action");
            stream.Parameters.AddDefinition("isTcEnabled", "Traction control is Enabled");
            stream.Parameters.AddDefinition("isInPit", "Car is in Pit lane");
            stream.Parameters.AddDefinition("isEngineLimiterOn", "Engine Limiter is On");

            stream.Parameters.DefaultLocation = "/Chassis/Speed";
            stream.Parameters.AddDefinition("speed_Kmh", "Speed in Kmh").SetUnit("kmh");
            stream.Parameters.AddDefinition("speed_Mph", "Speed in Mph").SetUnit("Mph").SetFormat("Format");
            stream.Parameters.AddDefinition("speed_Kmh", "Speed in Kmh", "Description").SetUnit("kmh").SetRange(0, 300);
            stream.Parameters.AddDefinition("speed_Kmh", "Speed in Kmh", "Description").SetUnit("kmh").SetRange(0, 300);

            stream.Parameters.DefaultLocation = "/Chassis/Acc";
            stream.Parameters.AddDefinition("accG_vertical").SetCustomProperties("Patrick");
            stream.Parameters.AddDefinition("accG_horizontal").SetCustomProperties("Patrick");
            stream.Parameters.AddDefinition("accG_frontal").SetCustomProperties("Patrick");

            //stream.Parameters.Location = "/Chassis/Controls";
            stream.Parameters.AddLocation("/Chassis/Controls")
                .AddDefinition("gas", "Gas throttle", "Indicates gas throttle %").SetRange(0, 1)
                .AddDefinition("brake", "Brake", "Brake pedal pressure %").SetRange(0, 1)
                .AddDefinition("clutch", "Clutch")
                .AddDefinition("engineRPM", "Engine RPM")
                .AddDefinition("steer", "Steering wheel angle").SetRange(-400, 400)
                .AddDefinition("gear", "Gear number").SetRange(-1, 8)
                .AddDefinition("cgHeight");
        }

        private static void SetEventDefinitions()
        {
            stream.Events.DefaultLocation = "/MyGroup/Laps";
            stream.Events.AddDefinition("LapCompleted", "Lap completed", "A lap has been completed");
            stream.Events.AddDefinition("ExtraEvent", "Event for testing purposes");
            stream.Events.AddDefinition("BestLap", "Best lap time", "A best lap time has been produced").SetLevel(EventLevel.Information);
        }

        private static void ConsoleCancelKeyPressHandler(object sender, ConsoleCancelEventArgs e)
        {
            e.Cancel = true;
            cToken.Cancel(false);
        }

    }
}
