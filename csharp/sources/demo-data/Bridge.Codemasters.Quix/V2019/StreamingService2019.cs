using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using Bridge.Codemasters.V2019.Models;
using Bridge.Codemasters.V2019.Models.CarSetup;
using Bridge.Codemasters.V2019.Models.CarStatus;
using Bridge.Codemasters.V2019.Models.CarTelemetry;
using Bridge.Codemasters.V2019.Models.Event;
using Bridge.Codemasters.V2019.Models.Lap;
using Bridge.Codemasters.V2019.Models.Motion;
using Bridge.Codemasters.V2019.Models.Participants;
using Bridge.Codemasters.V2019.Models.Session;
using Microsoft.Extensions.Logging;
using QuixStreams;
using QuixStreams.Streaming;
using QuixStreams.Streaming.Exceptions;
using QuixStreams.Streaming.Models;
using QuixStreams.Telemetry.Models;

namespace Bridge.Codemasters.Quix.V2019
{
    public class StreamingService2019 : IDisposable
    {
        private readonly bool includeOtherDrivers;
        private readonly string streamId;
        private Dictionary<ulong, List<I2019CodemastersPacket>> delayedEvents = new Dictionary<ulong, List<I2019CodemastersPacket>>();
        private readonly Lazy<ITopicProducer> topicProducer;
        private ConcurrentDictionary<ulong, StreamWrap> streams = new ConcurrentDictionary<ulong, StreamWrap>();
        private object streamLock = new object();
        private QuixStreamingClient client;
        private ILogger logger;
        
        public StreamingService2019(QuixStreamingClient client, string topic, bool includeOtherDrivers, string streamId)
        {
            this.logger = Logging.CreateLogger<StreamingService2019>();
            this.includeOtherDrivers = includeOtherDrivers;
            this.streamId = streamId;
            this.client = client;
            this.topicProducer = new Lazy<ITopicProducer>(() => this.client.GetTopicProducer(topic));
        }

        public void AddData(I2019CodemastersPacket converted)
        {
            if (IsDelayedPacket(converted)) return;
            var stream = this.GetStream(converted);
            HandlePacket(converted, stream);
        }

        private void HandlePacket(I2019CodemastersPacket converted, StreamWrap stream)
        {
            logger.LogTrace("Time: " + converted.Header.SessionTime + "ms");
            switch (converted.PacketType)
            {
                case PacketType.Motion:
                    this.AddMotionPacketData((PacketMotionData) converted, stream);
                    break;
                case PacketType.Session:
                    this.AddSessionPacketData((PacketSessionData) converted, stream);
                    break;
                case PacketType.LapData:
                    this.AddLapPacketData((PacketLapData) converted, stream);
                    break;
                case PacketType.Event:
                    this.AddValuePacketData((PacketEventData) converted, stream);
                    break;
                case PacketType.Participants:
                    this.AddParticipantsPacketData((PacketParticipantsData) converted, stream);
                    break;
                case PacketType.CarSetups:
                    //this.AddCarSetupPacketData((PacketCarSetupData) converted, stream);
                    break;
                case PacketType.CarTelemetry:
                    this.AddCarTelemetryPacketData((PacketCarTelemetryData) converted, stream);
                    break;
                case PacketType.CarStatus:
                    //this.AddCarStatusPacketData((PacketCarStatusData) converted, stream);
                    break;
                default:
                    throw new ArgumentOutOfRangeException();
            }
        }

        private bool IsDelayedPacket(I2019CodemastersPacket converted)
        {
            bool Delayed()
            {
                if (this.streams.ContainsKey(converted.SessionId)) return false;
                if (converted.PacketType == PacketType.Event)
                {
                    return true;
                }
                return false;
            }

            if (!Delayed()) return false;
            
            if (!this.delayedEvents.TryGetValue(converted.Header.SessionUID, out var list))
            {
                list = new List<I2019CodemastersPacket>();
                this.delayedEvents[converted.Header.SessionUID] = list;
            }
            list.Add(converted);
            return true;
        }

        private StreamWrap GetStream(I2019CodemastersPacket converted)
        {
            StreamWrap streamWrap = null;
            lock (streamLock) // for safety
            {
                if (!streams.TryGetValue(converted.SessionId, out streamWrap))
                {
                    this.logger.LogDebug("Package creating stream: " + converted.PacketType.ToString());
                    var stream = this.topicProducer.Value.GetOrCreateStream(this.streamId);
                    streamWrap = new StreamWrap
                    {
                        Stream = stream
                    };
                    stream.Epoch = DateTime.UtcNow - TimeSpan.FromSeconds(converted.Header.SessionTime);
                    stream.Timeseries.Buffer.TimeSpanInMilliseconds = 200;
                    streams[converted.SessionId] = streamWrap;
                    this.SetupStreamProperties(stream, converted);
                    this.SetupParameterMetaInfo(streamWrap);
                    if (this.delayedEvents.TryGetValue(converted.Header.SessionUID, out var list))
                    {
                        foreach (var codemastersPacket in list)
                        {
                            HandlePacket(codemastersPacket, streamWrap);
                        }
                    }
                    
                }
            }

            return streamWrap;
        }

        private void SetupStreamProperties(IStreamProducer stream, I2019CodemastersPacket converted)
        {
            var props = stream.Properties;
            props.Metadata["GameVersion"] = $"{converted.Header.GameMajorVersion}.{converted.Header.GameMinorVersion}";
            props.Metadata["PacketFormat"] = converted.Header.PacketFormat.ToString();
            props.Location = "/Game/Codemasters/F1-2019"; // this might not be correct always, maybe there is some info in a packet to help with this
            props.TimeOfRecording = DateTime.UtcNow;
            props.Name = $"F1 Game - [player] - [track] {props.TimeOfRecording:yyyy-MM-dd-HH:mm:ss}";
            
            this.logger.LogInformation($"Setting up new stream {stream.StreamId} with name '{props.Name}'");
        }

        private void AddCarStatusPacketData(PacketCarStatusData converted,StreamWrap stream)
        {
            for (var index = 0; index < stream.CarActive.Length; index++)
            {
                var isCarActive = stream.CarActive[index];
                if (!isCarActive) continue;
                var isPlayer = index == converted.Header.PlayerCarIndex;
                if (!this.includeOtherDrivers && !isPlayer) continue;
                var carStatusData = converted.CarStatusData[index];
                var pdata = new TimeseriesData();
                var ts = pdata.AddTimestamp(TimeSpan.FromSeconds(converted.Header.SessionTime));
                foreach (var kpair in stream.Tags[index])
                {
                    ts.AddTag(kpair.Key, kpair.Value);
                }
                AppendStatusDataToParameterDataTimestamp(ts, carStatusData, index, isPlayer);
                stream.Stream.Timeseries.Buffer.Publish(pdata);
                /* TODO
                 var prefix = isPlayer ? "" : $"Player{index}_";
                  var engineRpm = stream.Stream..GetParameterProperties($"{prefix}EngineRPM");
                if (engineRpm != null) engineRpm.MaximumValue = carStatusData.m_maxRPM;
                var playGear = stream.DataProperties.GetParameterProperties($"{prefix}Gear");
                if (playGear != null) playGear.MaximumValue = carStatusData.m_maxGears;*/
            }
        }
        
        private void AppendStatusDataToParameterDataTimestamp(TimeseriesDataTimestamp builder, CarStatusData carData, int carIndex, bool isPlayer)
        {
            var playerPrefix = isPlayer ? "" : $"Player{carIndex}_";
            builder.AddValue($"{playerPrefix}Status_DrsAllowed", carData.DrsAllowed);
            builder.AddValue($"{playerPrefix}Status_EngineDamage", carData.EngineDamage);
            builder.AddValue($"{playerPrefix}Status_FuelCapacity", carData.FuelCapacity);
            builder.AddValue($"{playerPrefix}Status_FuelMix", carData.FuelMix);
            builder.AddValue($"{playerPrefix}Status_MaxGears", carData.MaxGears);
            builder.AddValue($"{playerPrefix}Status_TractionControl", carData.TractionControl);
            builder.AddValue($"{playerPrefix}Status_ActualTyreCompound", carData.ActualTyreCompound);
            builder.AddValue($"{playerPrefix}Status_AntiLockBrakes", carData.AntiLockBrakes);
            builder.AddValue($"{playerPrefix}Status_ersDeployMode", carData.ErsDeployMode);
            builder.AddValue($"{playerPrefix}Status_ersStoreEnergy", carData.ErsStoreEnergy);
            builder.AddValue($"{playerPrefix}Status_FrontBrakeBias", carData.FrontBrakeBias);
            builder.AddValue($"{playerPrefix}Status_FuelInTank", carData.FuelInTank);
            builder.AddValue($"{playerPrefix}Status_FuelRemainingLaps", carData.FuelRemainingLaps);
            builder.AddValue($"{playerPrefix}Status_GearBoxDamage", carData.GearBoxDamage);
            builder.AddValue($"{playerPrefix}Status_PitLimiterStatus", carData.PitLimiterStatus);
            builder.AddValue($"{playerPrefix}Status_RearWingDamage", carData.RearWingDamage);
            builder.AddValue($"{playerPrefix}Status_TyreVisualCompound", carData.TyreVisualCompound);
            builder.AddValue($"{playerPrefix}Status_VehicleFiaFlags", carData.VehicleFiaFlags);
            builder.AddValue($"{playerPrefix}Status_ersDeployedThisLap", carData.ErsDeployedThisLap);
            builder.AddValue($"{playerPrefix}Status_FrontLeftWingDamage", carData.FrontLeftWingDamage);
            builder.AddValue($"{playerPrefix}Status_FrontRightWingDamage", carData.FrontRightWingDamage);
            builder.AddValue($"{playerPrefix}Status_IdleRPM", carData.IdleRPM);
            builder.AddValue($"{playerPrefix}Status_MaxRPM", carData.MaxRPM);
            builder.AddValue($"{playerPrefix}Status_ersHarvestedThisLapMGUH", carData.ErsHarvestedThisLapMGUH);
            builder.AddValue($"{playerPrefix}Status_ersHarvestedThisLapMGUK", carData.ErsHarvestedThisLapMGUK);
            builder.AddValue($"{playerPrefix}Status_TyresDamage_RearLeft", carData.TyresDamage[0]);
            builder.AddValue($"{playerPrefix}Status_TyresDamage_RearRight", carData.TyresDamage[1]);
            builder.AddValue($"{playerPrefix}Status_TyresDamage_FrontLeft", carData.TyresDamage[2]);
            builder.AddValue($"{playerPrefix}Status_TyresDamage_FrontRight", carData.TyresDamage[3]);
            builder.AddValue($"{playerPrefix}Status_TyresWear_RearLeft", carData.TyresWear[0]);
            builder.AddValue($"{playerPrefix}Status_TyresWear_RearRight", carData.TyresWear[1]);
            builder.AddValue($"{playerPrefix}Status_TyresWear_FrontLeft", carData.TyresWear[2]);
            builder.AddValue($"{playerPrefix}Status_TyresWear_FrontRight", carData.TyresWear[3]);

        }

        private void AddCarTelemetryPacketData(PacketCarTelemetryData converted,StreamWrap stream)
        {
            for (var index = 0; index < stream.CarActive.Length; index++)
            {
                if (!stream.CarActive[index]) continue;
                var isPlayer = index == converted.Header.PlayerCarIndex;
                if (!this.includeOtherDrivers && !isPlayer) continue;
                var carTelemetryData = converted.CarTelemetryData[index];
                var pdata = new TimeseriesData();
                var ts = pdata.AddTimestamp(TimeSpan.FromSeconds(converted.Header.SessionTime));
                foreach (var kpair in stream.Tags[index])
                {
                    ts.AddTag(kpair.Key, kpair.Value);
                }
                AppendCarTelemetryDataToParameterData(ts, carTelemetryData, index, isPlayer);
                stream.Stream.Timeseries.Buffer.Publish(pdata);
            }
        }
        
        private void AppendCarTelemetryDataToParameterData(TimeseriesDataTimestamp builder, CarTelemetryData carTelemetryData, int carIndex, bool isPlayer)
        {
            var playerPrefix = isPlayer ? "" : $"Player{carIndex}_";
            builder.AddValue($"{playerPrefix}Speed", carTelemetryData.Speed);
            builder.AddValue($"{playerPrefix}Brake", carTelemetryData.Brake);
            builder.AddValue($"{playerPrefix}Gear", carTelemetryData.Gear);
            builder.AddValue($"{playerPrefix}Steer", carTelemetryData.Steer);
            //builder.AddValue($"{playerPrefix}Clutch", carTelemetryData.Clutch);
            // builder.AddValue($"{playerPrefix}DRS", carTelemetryData.Drs);
            // builder.AddValue($"{playerPrefix}Throttle", carTelemetryData.Throttle);
            builder.AddValue($"{playerPrefix}EngineTemp", carTelemetryData.EngineTemperature);
            // builder.AddValue($"{playerPrefix}RevLightsPercent", carTelemetryData.RevLightsPercent);
            builder.AddValue($"{playerPrefix}EngineRPM", carTelemetryData.EngineRPM);
            // builder.AddValue($"{playerPrefix}BrakeTemp_RearLeft", carTelemetryData.BrakesTemperature[0]);
            // builder.AddValue($"{playerPrefix}BrakeTemp_RearRight", carTelemetryData.BrakesTemperature[1]);
            // builder.AddValue($"{playerPrefix}BrakeTemp_FrontLeft", carTelemetryData.BrakesTemperature[2]);
            // builder.AddValue($"{playerPrefix}BrakeTemp_FrontRight", carTelemetryData.BrakesTemperature[3]);
            // builder.AddValue($"{playerPrefix}TyrePressure_RearLeft", carTelemetryData.TyresPressure[0]);
            // builder.AddValue($"{playerPrefix}TyrePressure_RearRight", carTelemetryData.TyresPressure[1]);
            // builder.AddValue($"{playerPrefix}TyrePressure_FrontLeft", carTelemetryData.TyresPressure[2]);
            // builder.AddValue($"{playerPrefix}TyrePressure_FrontRight", carTelemetryData.TyresPressure[3]);
            // builder.AddValue($"{playerPrefix}TyreInnerTemp_RearLeft", carTelemetryData.TyresInnerTemperature[0]);
            // builder.AddValue($"{playerPrefix}TyreInnerTemp_RearRight", carTelemetryData.TyresInnerTemperature[1]);
            // builder.AddValue($"{playerPrefix}TyreInnerTemp_FrontLeft", carTelemetryData.TyresInnerTemperature[2]);
            // builder.AddValue($"{playerPrefix}TyreInnerTemp_FrontRight", carTelemetryData.TyresInnerTemperature[3]);
            // builder.AddValue($"{playerPrefix}TyreSurfaceTemp_RearLeft", carTelemetryData.TyresSurfaceTemperature[0]);
            // builder.AddValue($"{playerPrefix}TyreSurfaceTemp_RearRight", carTelemetryData.TyresSurfaceTemperature[1]);
            // builder.AddValue($"{playerPrefix}TyreSurfaceTemp_FrontLeft", carTelemetryData.TyresSurfaceTemperature[2]);
            // builder.AddValue($"{playerPrefix}TyreSurfaceTemp_FrontRight", carTelemetryData.TyresSurfaceTemperature[3]);
	           //
            // builder.AddValue($"{playerPrefix}SurfaceType_RearLeft", ValueConverter.ConvertSurfaceId(carTelemetryData.SurfaceType[0]));
            // builder.AddValue($"{playerPrefix}SurfaceType_RearRight", ValueConverter.ConvertSurfaceId(carTelemetryData.SurfaceType[1]));
            // builder.AddValue($"{playerPrefix}SurfaceType_FrontLeft",  ValueConverter.ConvertSurfaceId(carTelemetryData.SurfaceType[2]));
            // builder.AddValue($"{playerPrefix}SurfaceType_FrontRight",ValueConverter.ConvertSurfaceId(carTelemetryData.SurfaceType[3]));
        }

        private void AddCarSetupPacketData(PacketCarSetupData converted,StreamWrap stream)
        {
            for (var index = 0; index < stream.CarActive.Length; index++)
            {
                var isCarActive = stream.CarActive[index];
                if (!isCarActive) continue;
                var isPlayer = index == converted.Header.PlayerCarIndex;
                if (!this.includeOtherDrivers && !isPlayer) continue;                
                var carSetupData = converted.CarSetups[index];
                var pdata = new TimeseriesData();
                var ts = pdata.AddTimestamp(TimeSpan.FromSeconds(converted.Header.SessionTime));
                foreach (var kpair in stream.Tags[index])
                {
                    ts.AddTag(kpair.Key, kpair.Value);
                }
                AppendCarSetupDataToParameterData(ts, carSetupData, index, isPlayer);
                stream.Stream.Timeseries.Buffer.Publish(pdata);
            }
        }
        
        private void AppendCarSetupDataToParameterData(TimeseriesDataTimestamp builder, CarSetupData carSetupData, int carIndex, bool isPlayer)
        {
            var playerPrefix = isPlayer ? "" : $"Player{carIndex}_";
            builder.AddValue($"{playerPrefix}Setup_Ballast", carSetupData.Ballast );
            builder.AddValue($"{playerPrefix}Setup_BrakeBias",  carSetupData.BrakeBias );
            builder.AddValue($"{playerPrefix}Setup_BrakePressure",  carSetupData.BrakePressure );
            builder.AddValue($"{playerPrefix}Setup_FrontCamber",  carSetupData.FrontCamber );
            builder.AddValue($"{playerPrefix}Setup_FrontSuspension",  carSetupData.FrontSuspension );
            builder.AddValue($"{playerPrefix}Setup_FrontToe",  carSetupData.FrontToe );
            builder.AddValue($"{playerPrefix}Setup_FrontWing",  carSetupData.FrontWing );
            builder.AddValue($"{playerPrefix}Setup_FuelLoad",  carSetupData.FuelLoad );
            builder.AddValue($"{playerPrefix}Setup_OffThrottle",  carSetupData.OffThrottle );
            builder.AddValue($"{playerPrefix}Setup_OnThrottle",  carSetupData.OnThrottle );
            builder.AddValue($"{playerPrefix}Setup_RearCamber",  carSetupData.RearCamber );
            builder.AddValue($"{playerPrefix}Setup_RearSuspension",  carSetupData.RearSuspension );
            builder.AddValue($"{playerPrefix}Setup_RearToe",  carSetupData.RearToe );
            builder.AddValue($"{playerPrefix}Setup_RearWing",  carSetupData.RearWing );
            builder.AddValue($"{playerPrefix}Setup_FrontSuspensionHeight",  carSetupData.FrontSuspensionHeight );
            builder.AddValue($"{playerPrefix}Setup_FrontTyrePressure",  carSetupData.FrontTyrePressure );
            builder.AddValue($"{playerPrefix}Setup_RearSuspensionHeight",  carSetupData.RearSuspensionHeight );
            builder.AddValue($"{playerPrefix}Setup_RearTyrePressure",  carSetupData.RearTyrePressure );
            builder.AddValue($"{playerPrefix}Setup_FrontAntiRollBar",  carSetupData.FrontAntiRollBar );
            builder.AddValue($"{playerPrefix}Setup_RearAntiRollBar",  carSetupData.RearAntiRollBar );
        }

        private void AddParticipantsPacketData(PacketParticipantsData converted,StreamWrap stream)
        {
            if (stream.ParticipantAdded) return;
            stream.ParticipantAdded = true;
            stream.CarActive = new bool[converted.Participants.Length];
            var encounteredIds = new List<int>();
            for (var index = 0; index < converted.Participants.Length; index++)
            {
                var isPlayer = converted.Header.PlayerCarIndex == index;
                if (!this.includeOtherDrivers && !isPlayer) continue;
                var data = converted.Participants[index];
                if (data.DriverId == 0 || encounteredIds.Contains(data.DriverId))
                {
                    stream.CarActive[index] = false;
                    continue;
                }
                stream.Stream.Properties.Metadata[$"Player{index}_Name"] = data.Name;
                stream.Stream.Properties.Metadata[$"Player{index}_Id"] = data.DriverId.ToString();
                encounteredIds.Add(data.DriverId);
                stream.CarActive[index] = true;
                var writer = new TimeseriesDefinitionsWriter(stream.Stream.Timeseries, isPlayer, index);
                writer
                    .AddMotion()
                    .AddSetup()
                    .AddStatus()
                    .AddTelemetry();
                stream.Stream.Timeseries.Flush();
            }
            var props = stream.Stream.Properties;
            var player = converted.Participants[converted.Header.PlayerCarIndex];
            var newName = props.Name.Replace("[player]", player.Name);
            if (newName != props.Name)
            {
                props.Name = newName;
                this.logger.LogInformation($"Updating stream {stream.Stream.StreamId} with name '{props.Name}'");
            }
        }

        private void AddValuePacketData(PacketEventData converted, StreamWrap stream)
        {
            switch (converted.EventDataDetails)
            {
                case ChequeredFlagWavedEventDetails chequeredFlagWavedEventDetails:
                    stream.Stream.Events
                        .AddTimestamp(TimeSpan.FromSeconds(converted.Header.SessionTime))
                        .AddValue("ChequeredFlagWaved", "waved")
                        .Publish();
                    this.logger.LogInformation("Checkered flag waved");
                    break;
                case DRSEnabledEventDetails drsEnabledEventDetails:
                    stream.Stream.Events
                        .AddTimestamp(TimeSpan.FromSeconds(converted.Header.SessionTime))
                        .AddValue("DRSEnabledChanged", drsEnabledEventDetails.IsEnabled ? "enabled" : "disabled")
                        .Publish();
                    this.logger.LogInformation($"DRS {(drsEnabledEventDetails.IsEnabled ? "enabled" : "disabled")}");
                    break;
                case FastestLapEventDetails fastestLapEventDetails:
                    stream.Stream.Events
                        .AddTimestamp(TimeSpan.FromSeconds(converted.Header.SessionTime))
                        .AddValue("FastestLap", $"DriverID: {fastestLapEventDetails.vehicleIdx}, time: {TimeSpan.FromSeconds(fastestLapEventDetails.lapTime):g}s")
                        .Publish();
                    this.logger.LogInformation($"New fastest lap for DriverID: {fastestLapEventDetails.vehicleIdx}, time: {TimeSpan.FromSeconds(fastestLapEventDetails.lapTime):g}s");
                    break;
                case RaceWinnerEventDetails raceWinnerEventDetails:
                    stream.Stream.Events
                        .AddTimestamp(TimeSpan.FromSeconds(converted.Header.SessionTime))
                        .AddValue("RaceWinner", $"DriverID: {raceWinnerEventDetails.vehicleIdx}")
                        .Publish();
                    this.logger.LogInformation($"Race won by DriverID: {raceWinnerEventDetails.vehicleIdx}");
                    break;
                case RetirementEventDetails retirementEventDetails:
                    stream.Stream.Events
                        .AddTimestamp(TimeSpan.FromSeconds(converted.Header.SessionTime))
                        .AddValue("Retired", $"DriverID: {retirementEventDetails.vehicleIdx}")
                        .Publish();
                    this.logger.LogInformation($"Retired DriverID: {retirementEventDetails.vehicleIdx}");
                    break;
                case SessionFinishedEventDetails fed:
                    stream.Stream.Close();
                    this.streams.TryRemove(converted.SessionId, out var _);
                    this.delayedEvents.Remove(converted.Header.SessionUID);
                    this.logger.LogInformation($"Stream ended");
                    break;
                case SessionStartedEventDetails sessionStartedEventDetails:
                    this.logger.LogInformation($"Stream started");
                    break;
                case TeamMateInPitsEventDetails teamMateInPitsEventDetails:
                    stream.Stream.Events
                        .AddTimestamp(TimeSpan.FromSeconds(converted.Header.SessionTime))
                        .AddValue("TeamMateInPits", $"DriverId: {teamMateInPitsEventDetails.vehicleIdx}")
                        .Publish();
                    this.logger.LogInformation($"Team mate in pits, DriverId: {teamMateInPitsEventDetails.vehicleIdx}");
                    break;
            }
        }

        private void AddLapPacketData(PacketLapData converted,StreamWrap stream)
        {
            for (var index = 0; index < converted.LapData.Length; index++)
            {
                var isPlayer = index == converted.Header.PlayerCarIndex;
                if (!this.includeOtherDrivers && !isPlayer) continue;
                var lapData = converted.LapData[index];
                stream.Tags[index]["LapValidity"] = lapData.CurrentLapInvalid == 1 ? "Invalid" : "Valid";
                stream.Tags[index]["LapNumber"] = lapData.CurrentLapNum.ToString();
                stream.Tags[index]["PitStatus"] = lapData.PitStatus == 0
                    ? "None"
                    : (lapData.PitStatus == 1 ? "Pitting" : "In_Pit_Area");
                stream.Tags[index]["Sector"] = lapData.Sector.ToString();
                stream.Tags[index]["DriverStatus"] = lapData.DriverStatus == 0 ? "In_garage" : "Flying_lap";
                
                var pdata = new TimeseriesData();
                var ts = pdata.AddTimestamp(TimeSpan.FromSeconds(converted.Header.SessionTime));
                foreach (var kpair in stream.Tags[index])
                {
                    ts.AddTag(kpair.Key, kpair.Value);
                }
                AppendLapDataToParameterData(ts, lapData, index, isPlayer);
                stream.Stream.Timeseries.Buffer.Publish(pdata);
                
                if (!isPlayer || stream.LastPacketLapData == null) continue;
                // add a few events for players
                var lastPlayerLapData = stream.LastPacketLapData.Value.LapData[converted.Header.PlayerCarIndex];
                if (lastPlayerLapData.CarPosition != lapData.CarPosition)
                {
                    stream.Stream.Events
                        .AddTimestamp(TimeSpan.FromSeconds(converted.Header.SessionTime))
                        .AddValue("Player_Position_Changed", $"Position {lastPlayerLapData.CarPosition} -> {lapData.CarPosition}")
                        .Publish();
                }
                if (lastPlayerLapData.CurrentLapNum != lapData.CurrentLapNum)
                {
                    stream.Stream.Events
                        .AddTimestamp(TimeSpan.FromSeconds(converted.Header.SessionTime))
                        .AddValue("Player_NewLap", $"Lap {lapData.CurrentLapNum} started")
                        .Publish();
                }
            }

            stream.LastPacketLapData = converted;
        }
        
        private void AppendLapDataToParameterData(TimeseriesDataTimestamp builder, LapData lapData, int carIndex, bool isPlayer)
        {
            var playerPrefix = isPlayer ? "" : $"Player{carIndex}_";
            builder.AddValue($"{playerPrefix}LapDistance", lapData.LapDistance );
            builder.AddValue($"{playerPrefix}TotalLapDistance",  lapData.TotalDistance );
        }

        private void AddSessionPacketData(PacketSessionData converted,StreamWrap stream)
        {
            var props = stream.Stream.Properties;
            props.Metadata["Track"] = converted.Track;
            //props.Metadata["NetworkGame"] = converted.NetworkGame;
            //props.Metadata["Formula"] = converted.Formula;
            //props.Metadata["SessionType"] = converted.SessionType;
            props.Metadata["SessionId"] = converted.SessionId.ToString();
            var newName = props.Name.Replace("[track]", converted.Track);
            if (newName != props.Name)
            {
                props.Name = newName;
                this.logger.LogInformation($"Updating stream {stream.Stream.StreamId} with name '{props.Name}'");
            }

            props.Location = $"/Game/Codemasters/F1-2019/{converted.Track}";
            //
            // var pdata = new ParameterData();
            // var ts = pdata.AddTimestamp(TimeSpan.FromSeconds(converted.Header.SessionTime));
            // ts.AddValue("Session_Weather", converted.Weather)
            //     .AddValue("Session_SafetyCarStatus", converted.SafetyCarStatus);
            // stream.Stream.Parameters.Buffer.Write(pdata);
        }

        private void AddMotionPacketData(PacketMotionData converted,StreamWrap stream)
        {
            for (var index = 0; index < stream.CarActive.Length; index++)
            {
                if (!stream.CarActive[index]) continue;
                var isPlayer = index == converted.Header.PlayerCarIndex;
                if (!this.includeOtherDrivers && !isPlayer) continue;
                var carMotionData = converted.CarMotionData[index];

                var pdata = new TimeseriesData();
                var ts = pdata.AddTimestamp(TimeSpan.FromSeconds(converted.Header.SessionTime));
                foreach (var kpair in stream.Tags[index])
                {
                    ts.AddTag(kpair.Key, kpair.Value);
                }
                AppendCarMotionDataToParameterData(ts, carMotionData, index, isPlayer);
                stream.Stream.Timeseries.Buffer.Publish(pdata);
            }
        }


        private void AppendCarMotionDataToParameterData(TimeseriesDataTimestamp builder, CarMotionData carMotionData, int carIndex, bool isPlayer)
        {
            var playerPrefix = isPlayer ? "" : $"Player{carIndex}_";
            // builder.AddValue($"{playerPrefix}Motion_Pitch", carMotionData.Pitch);
            // builder.AddValue($"{playerPrefix}Motion_Roll", carMotionData.Roll);
            // builder.AddValue($"{playerPrefix}Motion_Yaw", carMotionData.Yaw);
            // builder.AddValue($"{playerPrefix}Motion_GForceLateral", carMotionData.GForceLateral);
            // builder.AddValue($"{playerPrefix}Motion_GForceLongitudinal", carMotionData.GForceLongitudinal);
            // builder.AddValue($"{playerPrefix}Motion_GForceVertical", carMotionData.GForceVertical);
            builder.AddValue($"{playerPrefix}Motion_WorldPositionX", carMotionData.WorldPositionX);
            builder.AddValue($"{playerPrefix}Motion_WorldPositionY", carMotionData.WorldPositionY);
            builder.AddValue($"{playerPrefix}Motion_WorldPositionZ", carMotionData.WorldPositionZ);
            // builder.AddValue($"{playerPrefix}Motion_WorldVelocityX", carMotionData.WorldVelocityX);
            // builder.AddValue($"{playerPrefix}Motion_WorldVelocityY", carMotionData.WorldVelocityY);
            // builder.AddValue($"{playerPrefix}Motion_WorldVelocityZ", carMotionData.WorldVelocityZ);
            // builder.AddValue($"{playerPrefix}Motion_WorldForwardDirX", carMotionData.WorldForwardDirX);
            // builder.AddValue($"{playerPrefix}Motion_WorldForwardDirY", carMotionData.WorldForwardDirY);
            // builder.AddValue($"{playerPrefix}Motion_WorldForwardDirZ", carMotionData.WorldForwardDirZ);
            // builder.AddValue($"{playerPrefix}Motion_WorldRightDirX", carMotionData.WorldRightDirX);
            // builder.AddValue($"{playerPrefix}Motion_WorldRightDirY", carMotionData.WorldRightDirY);
            // builder.AddValue($"{playerPrefix}Motion_WorldRightDirZ", carMotionData.WorldRightDirZ);
        }

        public void Close()
        {
            foreach (var stream in streams.Values)
            {
                try
                {
                    stream.Stream.Close();
                }
                catch (StreamClosedException)
                {
                    
                }

                stream.Stream.Dispose();
            }
        }

        private void SetupParameterMetaInfo(StreamWrap streamWrap)
        {
            // streamWrap.Stream.Parameters
            //     .AddLocation("session")
            //     .AddDefinition("Session_Weather", "Weather")
            //     .AddDefinition("Session_SafetyCarStatus", "SafetyCarStatus");

            streamWrap.Stream.Events.AddDefinition("Player_NewLap", "Player NewLap").SetLevel(EventLevel.Information)
                .AddDefinition("Player_Position_Changed", "Player Position Changed").SetLevel(EventLevel.Critical)
                .AddDefinition("RaceWinner", "Race Winner").SetLevel(EventLevel.Critical)
                .AddDefinition("ChequeredFlagWaved", "Chequered Flag Waved").SetLevel(EventLevel.Information);
        }

        private class StreamWrap
        {
            public StreamWrap()
            {
                Tags = new Dictionary<string, string>[20];
                for (var index = 0; index < Tags.Length; index++)
                {
                    Tags[index] = new Dictionary<string, string>();
                }
            }

            public IStreamProducer Stream { get; set; }
            public bool ParticipantAdded { get; set; }
            
            public bool[] CarActive = new bool[20];
            
            public PacketLapData? LastPacketLapData { get; set; }

            public Dictionary<string, string>[] Tags { get; set; }
        }

        public void Dispose()
        {
            this.Close();
        }
    }
}