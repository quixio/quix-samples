using System;
using System.Text;
using Bridge.Codemasters.V2019.Models;
using Bridge.Codemasters.V2019.Models.CarSetup;
using Bridge.Codemasters.V2019.Models.CarStatus;
using Bridge.Codemasters.V2019.Models.CarTelemetry;
using Bridge.Codemasters.V2019.Models.Event;
using Bridge.Codemasters.V2019.Models.Lap;
using Bridge.Codemasters.V2019.Models.Motion;
using Bridge.Codemasters.V2019.Models.Participants;
using Bridge.Codemasters.V2019.Models.Session;

namespace Bridge.Codemasters.V2019.Serializers
{
    public static class PacketSerializer
    {
        public static PacketHeader? SerializeHeader(byte[] data, int offset)
        {
            if (data.Length - offset < 0) return null;

            return new PacketHeader
            {
                PacketFormat = BitConverter.ToUInt16(data, offset),
                GameMajorVersion = data[offset + 2],
                GameMinorVersion = data[offset + 3],
                PacketVersion = data[offset + 4],
                PacketId = (PacketType) data[offset + 5],
                SessionUID = BitConverter.ToUInt64(data, offset + 6),
                SessionTime = BitConverter.ToSingle(data, offset + 14),
                FrameIdentifier = BitConverter.ToUInt32(data, offset + 18),
                PlayerCarIndex = data[offset + 22]
            };
        }

        public static PacketEventData SerializePacketEventData(byte[] data, int offset)
        {
            var eventPacket = new PacketEventData
            {
                Header = SerializeHeader(data, offset).Value,
                EventStringCode = Encoding.UTF8.GetString(data, offset + PacketHeader.SizeOf, 4).Trim('\0')
            };

            switch (eventPacket.EventStringCode)
            {
                case "SSTA":
                    eventPacket.EventDataDetails = new SessionStartedEventDetails();
                    break;
                case "SEND":
                    eventPacket.EventDataDetails = new SessionFinishedEventDetails();
                    break;
                case "FTLP":
                    eventPacket.EventDataDetails = new FastestLapEventDetails
                    {
                        vehicleIdx = data[offset + PacketHeader.SizeOf + 4],
                        lapTime = BitConverter.ToSingle(data, offset + PacketHeader.SizeOf + 5)
                    };
                    break;
                case "RTMT":
                    eventPacket.EventDataDetails = new RetirementEventDetails
                    {
                        vehicleIdx = data[offset + PacketHeader.SizeOf + 4]
                    };
                    break;
                case "DRSE":
                    eventPacket.EventDataDetails = new DRSEnabledEventDetails(true);
                    break;
                case "DRSD":
                    eventPacket.EventDataDetails = new DRSEnabledEventDetails(false);
                    break;
                case "TMPT":
                    eventPacket.EventDataDetails = new TeamMateInPitsEventDetails
                    {
                        vehicleIdx = data[offset + PacketHeader.SizeOf + 4]
                    };
                    break;
                case "CHQF":
                    eventPacket.EventDataDetails = new ChequeredFlagWavedEventDetails();
                    break;
                case "RCWN":
                    eventPacket.EventDataDetails = new RaceWinnerEventDetails
                    {
                        vehicleIdx = data[offset + PacketHeader.SizeOf + 4]
                    };
                    break;
            }

            return eventPacket;
        }

        public static PacketCarStatusData SerializePacketCarStatusData(byte[] data, int offset)
        {
            var packetCarStatusData = new PacketCarStatusData
            {
                Header = SerializeHeader(data, offset).Value
            };

            var carStatusData = new CarStatusData[20];
            offset += PacketHeader.SizeOf;
            for (var i = 0; i < 20; i++)
            {
                var carData = new CarStatusData
                {
                    TractionControl = data[offset],
                    AntiLockBrakes = data[offset + 1],
                    FuelMix = data[offset + 2],
                    FrontBrakeBias = data[offset + 3],
                    PitLimiterStatus = data[offset + 4],
                    FuelInTank = BitConverter.ToSingle(data, offset + 5),
                    FuelCapacity = BitConverter.ToSingle(data, offset + 9),
                    FuelRemainingLaps = BitConverter.ToSingle(data, offset + 13),
                    MaxRPM = BitConverter.ToUInt16(data, offset + 17),
                    IdleRPM = BitConverter.ToUInt16(data, offset + 19),
                    MaxGears = data[offset + 21],
                    DrsAllowed = data[offset + 22],
                    TyresWear = new[]
                    {
                        data[offset + 23],
                        data[offset + 24],
                        data[offset + 25],
                        data[offset + 26]
                    },
                    ActualTyreCompound = data[offset + 27],
                    TyreVisualCompound = data[offset + 28],
                    TyresDamage = new[]
                    {
                        data[offset + 29],
                        data[offset + 30],
                        data[offset + 31],
                        data[offset + 32]
                    },
                    FrontLeftWingDamage = data[offset + 33],
                    FrontRightWingDamage = data[offset + 34],
                    RearWingDamage = data[offset + 35],
                    EngineDamage = data[offset + 36],
                    GearBoxDamage = data[offset + 37],
                    VehicleFiaFlags = (sbyte) data[offset + 38],
                    ErsStoreEnergy = BitConverter.ToSingle(data, offset + 39),
                    ErsDeployMode = data[offset + 43],
                    ErsHarvestedThisLapMGUK = BitConverter.ToSingle(data, offset + 44),
                    ErsHarvestedThisLapMGUH = BitConverter.ToSingle(data, offset + 48),
                    ErsDeployedThisLap = BitConverter.ToSingle(data, offset + 52)
                };
                carStatusData[i] = carData;
                offset += CarStatusData.SizeOf;
            }

            packetCarStatusData.CarStatusData = carStatusData;
            return packetCarStatusData;
        }

        public static PacketCarTelemetryData SerializePacketCarTelemetryData(byte[] data, int offset)
        {
            var packetCarTelemetryData = new PacketCarTelemetryData
            {
                Header = SerializeHeader(data, offset).Value
            };

            var carTelemetryData = new CarTelemetryData[20];
            offset += PacketHeader.SizeOf;
            for (var i = 0; i < 20; i++)
            {
                var carData = new CarTelemetryData
                {
                    Speed = BitConverter.ToUInt16(data, offset),
                    Throttle = BitConverter.ToSingle(data, offset + 2),
                    Steer = BitConverter.ToSingle(data, offset + 6),
                    Brake = BitConverter.ToSingle(data, offset + 10),
                    Clutch = data[offset + 14],
                    Gear = (sbyte) data[offset + 15],
                    EngineRPM = BitConverter.ToUInt16(data, offset + 16),
                    Drs = data[offset + 18],
                    RevLightsPercent = data[offset + 19],
                    BrakesTemperature = new[]
                    {
                        BitConverter.ToUInt16(data, offset + 20),
                        BitConverter.ToUInt16(data, offset + 22),
                        BitConverter.ToUInt16(data, offset + 24),
                        BitConverter.ToUInt16(data, offset + 26)
                    },
                    TyresSurfaceTemperature = new[]
                    {
                        BitConverter.ToUInt16(data, offset + 28),
                        BitConverter.ToUInt16(data, offset + 30),
                        BitConverter.ToUInt16(data, offset + 32),
                        BitConverter.ToUInt16(data, offset + 34)
                    },
                    TyresInnerTemperature = new[]
                    {
                        BitConverter.ToUInt16(data, offset + 36),
                        BitConverter.ToUInt16(data, offset + 38),
                        BitConverter.ToUInt16(data, offset + 40),
                        BitConverter.ToUInt16(data, offset + 42)
                    },
                    EngineTemperature = BitConverter.ToUInt16(data, offset + 44),
                    TyresPressure = new[]
                    {
                        BitConverter.ToSingle(data, offset + 46),
                        BitConverter.ToSingle(data, offset + 50),
                        BitConverter.ToSingle(data, offset + 54),
                        BitConverter.ToSingle(data, offset + 58)
                    },
                    SurfaceType = new[]
                    {
                        data[offset + 62],
                        data[offset + 63],
                        data[offset + 64],
                        data[offset + 65]
                    }
                };
                carTelemetryData[i] = carData;
                offset += CarTelemetryData.SizeOf;
            }

            packetCarTelemetryData.CarTelemetryData = carTelemetryData;

            packetCarTelemetryData.ButtonStatus = BitConverter.ToUInt32(data, offset);

            return packetCarTelemetryData;
        }

        public static PacketCarSetupData SerializePacketCarSetupData(byte[] data, int offset)
        {
            var packetCarSetupData = new PacketCarSetupData
            {
                Header = SerializeHeader(data, offset).Value
            };

            var carSetupData = new CarSetupData[20];
            offset += PacketHeader.SizeOf;
            for (var i = 0; i < 20; i++)
            {
                var carData = new CarSetupData
                {
                    FrontWing = data[offset],
                    RearWing = data[offset + 1],
                    OnThrottle = data[offset + 2],
                    OffThrottle = data[offset + 3],
                    FrontCamber = BitConverter.ToSingle(data, offset + 4),
                    RearCamber = BitConverter.ToSingle(data, offset + 8),
                    FrontToe = BitConverter.ToSingle(data, offset + 12),
                    RearToe = BitConverter.ToSingle(data, offset + 16),
                    FrontSuspension = data[offset + 20],
                    RearSuspension = data[offset + 21],
                    FrontAntiRollBar = data[offset + 22],
                    RearAntiRollBar = data[offset + 23],
                    FrontSuspensionHeight = data[offset + 24],
                    RearSuspensionHeight = data[offset + 25],
                    BrakePressure = data[offset + 26],
                    BrakeBias = data[offset + 27],
                    FrontTyrePressure = BitConverter.ToSingle(data, offset + 28),
                    RearTyrePressure = BitConverter.ToSingle(data, offset + 32),
                    Ballast = data[offset + 36],
                    FuelLoad = BitConverter.ToSingle(data, offset + 37)
                };
                carSetupData[i] = carData;
                offset += CarSetupData.SizeOf;
            }

            packetCarSetupData.CarSetups = carSetupData;

            return packetCarSetupData;
        }

        public static PacketParticipantsData SerializePacketParticipantsData(byte[] data, int offset)
        {
            var packetParticipantsData = new PacketParticipantsData
            {
                Header = SerializeHeader(data, offset).Value,
                NumActiveCars = data[PacketHeader.SizeOf]
            };

            var participantsData = new ParticipantData[20];
            offset += PacketHeader.SizeOf + 1;
            for (var i = 0; i < 20; i++)
            {
                var participantData = new ParticipantData
                {
                    AiControlled = data[offset],
                    DriverId = data[offset + 1],
                    TeamId = data[offset + 2],
                    RaceNumber = data[offset + 3],
                    Nationality = data[offset + 4],
                    Name = Encoding.UTF8.GetString(data, offset + 5, 48).Trim('\0').Trim(),
                    YourTelemetry = data[offset + 53]
                };
                participantsData[i] = participantData;
                offset += ParticipantData.SizeOf;
            }

            packetParticipantsData.Participants = participantsData;

            return packetParticipantsData;
        }

        public static PacketLapData SerializePacketLapData(byte[] data, int offset)
        {
            var packetLapData = new PacketLapData
            {
                Header = SerializeHeader(data, offset).Value
            };

            var lapsData = new LapData[20];
            offset += PacketHeader.SizeOf;
            for (var i = 0; i < 20; i++)
            {
                var lapData = new LapData
                {
                    LastLapTime = BitConverter.ToSingle(data, offset),
                    CurrentLapTime = BitConverter.ToSingle(data, offset + 4),
                    BestLapTime = BitConverter.ToSingle(data, offset + 8),
                    Sector1Time = BitConverter.ToSingle(data, offset + 12),
                    Sector2Time = BitConverter.ToSingle(data, offset + 16),
                    LapDistance = BitConverter.ToSingle(data, offset + 20),
                    TotalDistance = BitConverter.ToSingle(data, offset + 24),
                    SafetyCarDelta = BitConverter.ToSingle(data, offset + 28),
                    CarPosition = data[offset + 32],
                    CurrentLapNum = data[offset + 33],
                    PitStatus = data[offset + 34],
                    Sector = data[offset + 35],
                    CurrentLapInvalid = data[offset + 36],
                    Penalties = data[offset + 37],
                    GridPosition = data[offset + 38],
                    DriverStatus = data[offset + 39],
                    ResultStatus = data[offset + 40]
                };
                lapsData[i] = lapData;
                offset += CarSetupData.SizeOf;
            }

            packetLapData.LapData = lapsData;

            return packetLapData;
        }

        public static PacketSessionData SerializePacketSessionData(byte[] data, int offset)
        {
            var packetSessionData = new PacketSessionData
            {
                Header = SerializeHeader(data, offset).Value,
                Weather = ValueConverter.ConvertWeather(data[offset + PacketHeader.SizeOf]),
                TrackTemperature = (sbyte) data[offset + PacketHeader.SizeOf + 1],
                AirTemperature = (sbyte) data[offset + PacketHeader.SizeOf + 2],
                TotalLaps = data[offset + PacketHeader.SizeOf + 3],
                TrackLength = BitConverter.ToUInt16(data, offset + PacketHeader.SizeOf + 4),
                SessionType = ValueConverter.ConvertSessionType(data[offset + PacketHeader.SizeOf + 6]),
                Track = ValueConverter.ConvertTrackId((sbyte) data[offset + PacketHeader.SizeOf + 7]),
                Formula = ValueConverter.ConvertFormula(data[offset + PacketHeader.SizeOf + 8]),
                SessionTimeLeft = BitConverter.ToUInt16(data, offset + PacketHeader.SizeOf + 9),
                SessionDuration = BitConverter.ToUInt16(data, offset + PacketHeader.SizeOf + 11),
                PitSpeedLimit = data[offset + PacketHeader.SizeOf + 13],
                GamePaused = data[offset + PacketHeader.SizeOf + 14],
                IsSpectating = data[offset + PacketHeader.SizeOf + 15],
                SpectatorCarIndex = data[offset + PacketHeader.SizeOf + 16],
                SliProNativeSupport = data[offset + PacketHeader.SizeOf + 17],
                NumMarshalZones = data[offset + PacketHeader.SizeOf + 18]
            };

            var marshalZones = new MarshalZone[21];
            offset += PacketHeader.SizeOf + 19;
            for (var i = 0; i < 21; i++)
            {
                var marshalZone = new MarshalZone
                {
                    ZoneStart = BitConverter.ToSingle(data, offset),
                    ZoneFlag = (sbyte) data[offset + 4]
                };
                marshalZones[i] = marshalZone;
                offset += MarshalZone.SizeOf;
            }

            packetSessionData.MarshalZones = marshalZones;
            packetSessionData.SafetyCarStatus = ValueConverter.ConvertSafetyCarStatus(data[offset]);
            packetSessionData.NetworkGame = ValueConverter.ConvertNetworkGame(data[offset + 1]);

            return packetSessionData;
        }

        public static PacketMotionData SerializePacketMotionData(byte[] data, int offset)
        {
            var packetMotionData = new PacketMotionData
            {
                Header = SerializeHeader(data, offset).Value
            };

            var carMotionData = new CarMotionData[20];
            offset += PacketHeader.SizeOf;
            for (var i = 0; i < 20; i++)
            {
                var carData = new CarMotionData
                {
                    WorldPositionX = BitConverter.ToSingle(data, offset),
                    WorldPositionY = BitConverter.ToSingle(data, offset + 4),
                    WorldPositionZ = BitConverter.ToSingle(data, offset + 8),
                    WorldVelocityX = BitConverter.ToSingle(data, offset + 12),
                    WorldVelocityY = BitConverter.ToSingle(data, offset + 16),
                    WorldVelocityZ = BitConverter.ToSingle(data, offset + 20),
                    WorldForwardDirX = BitConverter.ToInt16(data, offset + 24),
                    WorldForwardDirY = BitConverter.ToInt16(data, offset + 26),
                    WorldForwardDirZ = BitConverter.ToInt16(data, offset + 28),
                    WorldRightDirX = BitConverter.ToInt16(data, offset + 30),
                    WorldRightDirY = BitConverter.ToInt16(data, offset + 32),
                    WorldRightDirZ = BitConverter.ToInt16(data, offset + 34),
                    GForceLateral = BitConverter.ToSingle(data, offset + 36),
                    GForceLongitudinal = BitConverter.ToSingle(data, offset + 40),
                    GForceVertical = BitConverter.ToSingle(data, offset + 44),
                    Yaw = BitConverter.ToSingle(data, offset + 48),
                    Pitch = BitConverter.ToSingle(data, offset + 52),
                    Roll = BitConverter.ToSingle(data, offset + 56)
                };
                carMotionData[i] = carData;
                offset += CarMotionData.SizeOf;
            }

            packetMotionData.CarMotionData = carMotionData;
            packetMotionData.SuspensionPosition = new[]
            {
                BitConverter.ToSingle(data, offset),
                BitConverter.ToSingle(data, offset + 4),
                BitConverter.ToSingle(data, offset + 8),
                BitConverter.ToSingle(data, offset + 12)
            };
            packetMotionData.SuspensionVelocity = new[]
            {
                BitConverter.ToSingle(data, offset + 16),
                BitConverter.ToSingle(data, offset + 20),
                BitConverter.ToSingle(data, offset + 24),
                BitConverter.ToSingle(data, offset + 28)
            };
            packetMotionData.SuspensionAcceleration = new[]
            {
                BitConverter.ToSingle(data, offset + 32),
                BitConverter.ToSingle(data, offset + 36),
                BitConverter.ToSingle(data, offset + 40),
                BitConverter.ToSingle(data, offset + 44)
            };
            packetMotionData.WheelSpeed = new[]
            {
                BitConverter.ToSingle(data, offset + 48),
                BitConverter.ToSingle(data, offset + 52),
                BitConverter.ToSingle(data, offset + 56),
                BitConverter.ToSingle(data, offset + 60)
            };
            packetMotionData.WheelSlip = new[]
            {
                BitConverter.ToSingle(data, offset + 64),
                BitConverter.ToSingle(data, offset + 68),
                BitConverter.ToSingle(data, offset + 72),
                BitConverter.ToSingle(data, offset + 76)
            };
            packetMotionData.LocalVelocityX = BitConverter.ToSingle(data, offset + 80);
            packetMotionData.LocalVelocityY = BitConverter.ToSingle(data, offset + 84);
            packetMotionData.LocalVelocityZ = BitConverter.ToSingle(data, offset + 88);
            packetMotionData.AngularVelocityX = BitConverter.ToSingle(data, offset + 92);
            packetMotionData.AngularVelocityY = BitConverter.ToSingle(data, offset + 96);
            packetMotionData.AngularVelocityZ = BitConverter.ToSingle(data, offset + 100);
            packetMotionData.AngularAccelerationX = BitConverter.ToSingle(data, offset + 104);
            packetMotionData.AngularAccelerationY = BitConverter.ToSingle(data, offset + 108);
            packetMotionData.AngularAccelerationZ = BitConverter.ToSingle(data, offset + 112);
            packetMotionData.FrontWheelsAngle = BitConverter.ToSingle(data, offset + 116);

            return packetMotionData;
        }
    }
}