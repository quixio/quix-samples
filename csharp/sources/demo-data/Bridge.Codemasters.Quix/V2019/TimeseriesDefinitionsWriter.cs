using System;
using QuixStreams.Streaming.Models.StreamProducer;

namespace Bridge.Codemasters.Quix.V2019
{
    public class TimeseriesDefinitionsWriter
    {
        private readonly StreamTimeseriesProducer parameters;
        private readonly int? playerIndex;
        private readonly bool isPlayer;
        private readonly string root;

        public TimeseriesDefinitionsWriter(StreamTimeseriesProducer parameters, bool isPlayer, int? playerIndex = null)
        {
            if (!isPlayer && playerIndex == null)
            {
                throw new ArgumentOutOfRangeException(nameof(playerIndex));
            }

            this.parameters = parameters;
            this.playerIndex = playerIndex;
            this.isPlayer = isPlayer;
            root = isPlayer ? "/Player/" : $"/Player{playerIndex}/";
        }

        public TimeseriesDefinitionsWriter AddStatus()
        {
            var playerPrefix = isPlayer ? "" : $"Player{playerIndex}_";
            // parameters.AddLocation($"{root}Status/Misc")
            //     .AddDefinition($"{playerPrefix}Status_TractionControl", $"{playerPrefix}TractionControl").SetRange(0, 2)
            //     .AddDefinition($"{playerPrefix}Status_PitLimiterStatus", $"{playerPrefix}PitLimiterStatus").SetRange(0, 1)
            //     .AddDefinition($"{playerPrefix}Status_VehicleFiaFlags", $"{playerPrefix}VehicleFiaFlags").SetRange(-1, 4);
            // parameters.AddLocation($"{root}Status/Wing")
            //     .AddDefinition($"{playerPrefix}Status_RearWingDamage", $"{playerPrefix}RearWingDamage").SetRange(0, 100)
            //     .AddDefinition($"{playerPrefix}Status_FrontLeftWingDamage", $"{playerPrefix}FrontLeftWingDamage").SetRange(0, 100)
            //     .AddDefinition($"{playerPrefix}Status_FrontRightWingDamage", $"{playerPrefix}FrontRightWingDamage").SetRange(0, 100);
            // parameters.AddLocation($"{root}Status/Tyre")
            //     .AddDefinition($"{playerPrefix}Status_TyreVisualCompound", $"{playerPrefix}TyreVisualCompound")
                // .AddDefinition($"{playerPrefix}Status_ActualTyreCompound", $"{playerPrefix}ActualTyreCompound");
            // parameters.AddLocation($"{root}Status/Brake")
            //     .AddDefinition($"{playerPrefix}Status_AntiLockBrakes", $"{playerPrefix}AntiLockBrakes").SetRange(0, 1)
            //     .AddDefinition($"{playerPrefix}Status_FrontBrakeBias", $"{playerPrefix}FrontBrakeBias").SetRange(0, 100);
//            parameters.AddLocation($"{root}Status/Engine")
                // .AddDefinition($"{playerPrefix}Status_ersDeployedThisLap", $"{playerPrefix}ersDeployedThisLap")
                // .AddDefinition($"{playerPrefix}Status_ersHarvestedThisLapMGUH", $"{playerPrefix}ersHarvestedThisLapMGUH")
                // .AddDefinition($"{playerPrefix}Status_ersHarvestedThisLapMGUK", $"{playerPrefix}ersHarvestedThisLapMGUK")
                // .AddDefinition($"{playerPrefix}Status_DrsAllowed", $"{playerPrefix}DrsAllowed")
                // .AddDefinition($"{playerPrefix}Status_EngineDamage", $"{playerPrefix}DrsAllowed").SetRange(0, 1)
                // .AddDefinition($"{playerPrefix}Status_MaxRPM", $"{playerPrefix}MaxRPM").SetRange(0, 20000)
                // .AddDefinition($"{playerPrefix}Status_IdleRPM", $"{playerPrefix}IdleRPM").SetRange(0, 20000)
                // .AddDefinition($"{playerPrefix}Status_FuelCapacity", $"{playerPrefix}FuelCapacity").SetRange(0, 150)
                // .AddDefinition($"{playerPrefix}Status_MaxGears", $"{playerPrefix}MaxGears").SetRange(0, 10)
                // .AddDefinition($"{playerPrefix}Status_ersDeployMode", $"{playerPrefix}ersDeployMode").SetRange(0, 5)
                // .AddDefinition($"{playerPrefix}Status_ersStoreEnergy", $"{playerPrefix}ersStoreEnergy").SetRange(0, 4000000)
                // .AddDefinition($"{playerPrefix}Status_FuelRemainingLaps", $"{playerPrefix}FuelRemainingLaps").SetRange(0, 10)
                // .AddDefinition($"{playerPrefix}Status_FuelInTank", $"{playerPrefix}FuelInTank").SetRange(0, 10)
                // .AddDefinition($"{playerPrefix}Status_FuelMix", $"{playerPrefix}FuelMix").SetRange(0, 3);
            return this;
        }

        public TimeseriesDefinitionsWriter AddMotion()
        {
            var playerPrefix = isPlayer ? "" : $"Player{playerIndex}_";
            // parameters.AddLocation($"{root}Motion/Car")
            //     .AddDefinition($"{playerPrefix}Motion_Roll", $"{playerPrefix}Roll").SetRange(-0.1, 0.1).SetUnit("°") .AddDefinition($"{playerPrefix}Motion_Yaw", $"{playerPrefix}Yaw").SetRange(-10, 10).SetUnit("°")
            //     .AddDefinition($"{playerPrefix}Motion_Pitch", $"{playerPrefix}Pitch").SetRange(-0.1, 0.1).SetUnit("°");
            // parameters.AddLocation($"{root}Motion/Driver")
            //     .AddDefinition($"{playerPrefix}Motion_GForceLateral", $"{playerPrefix}GForceLateral").SetRange(-5, 5)
            //     .AddDefinition($"{playerPrefix}Motion_GForceLongitudinal", $"{playerPrefix}GForceLongitudinal").SetRange(-5, 5)
            //     .AddDefinition($"{playerPrefix}Motion_GForceVertical", $"{playerPrefix}GForceVertical").SetRange(-2, 2);
            parameters.AddLocation($"{root}Motion/World")
                .AddDefinition($"{playerPrefix}Motion_WorldPositionX", $"{playerPrefix}WorldPositionX").SetRange(-1000, 1000)
                .AddDefinition($"{playerPrefix}Motion_WorldPositionY", $"{playerPrefix}WorldPositionY").SetRange(-100, 0)
                .AddDefinition($"{playerPrefix}Motion_WorldPositionZ", $"{playerPrefix}WorldPositionZ").SetRange(-10000, 1000);
                // .AddDefinition($"{playerPrefix}Motion_WorldVelocityX", $"{playerPrefix}WorldVelocityX").SetRange(-100, 100)
                // .AddDefinition($"{playerPrefix}Motion_WorldVelocityY", $"{playerPrefix}WorldVelocityY").SetRange(-5, 5)
                // .AddDefinition($"{playerPrefix}Motion_WorldVelocityZ", $"{playerPrefix}WorldVelocityZ").SetRange(-100, 100)
                // .AddDefinition($"{playerPrefix}Motion_WorldForwardDirX", $"{playerPrefix}WorldForwardDirX").SetRange(-32768, 32767)
                // .AddDefinition($"{playerPrefix}Motion_WorldForwardDirY", $"{playerPrefix}WorldForwardDirY").SetRange(-4096, 4096)
                // .AddDefinition($"{playerPrefix}Motion_WorldForwardDirZ", $"{playerPrefix}WorldForwardDirZ").SetRange(-32768, 32767)
                // .AddDefinition($"{playerPrefix}Motion_WorldRightDirX", $"{playerPrefix}WorldRightDirX").SetRange(-32768, 32767)
                // .AddDefinition($"{playerPrefix}Motion_WorldRightDirY", $"{playerPrefix}WorldRightDirY").SetRange(-4096, 4096)
                // .AddDefinition($"{playerPrefix}Motion_WorldRightDirZ", $"{playerPrefix}WorldRightDirZ").SetRange(-32768, 32767);
            return this;
        }

        public TimeseriesDefinitionsWriter AddTelemetry()
        {
            var playerPrefix = isPlayer ? "" : $"Player{playerIndex}_";
            parameters.AddLocation($"{root}Telemetry/Input")
                .AddDefinition($"{playerPrefix}Steer").SetRange(-1, 1)
                //.AddDefinition($"{playerPrefix}RevLightsPercent").SetRange(0, 100).SetUnit("%")
                //.AddDefinition($"{playerPrefix}ButtonState").SetRange(0, 0x4888)
                .AddDefinition($"{playerPrefix}Throttle").SetRange(0, 1)
                .AddDefinition($"{playerPrefix}Brake", description: "Amount of brake applied").SetRange(0, 1);
            // parameters.AddLocation($"{root}Telemetry/Brake")
            //     .AddDefinition($"{playerPrefix}BrakeTemp_RearLeft").SetRange(20, 100).SetUnit("°")
            //     .AddDefinition($"{playerPrefix}BrakeTemp_RearRight").SetRange(20, 100).SetUnit("°")
            //     .AddDefinition($"{playerPrefix}BrakeTemp_FrontLeft").SetRange(20, 100).SetUnit("°")
            //     .AddDefinition($"{playerPrefix}BrakeTemp_FrontRight").SetRange(20, 100).SetUnit("°");
            // parameters.AddLocation($"{root}Telemetry/Tyre")
            //     .AddDefinition($"{playerPrefix}TyrePressure_RearLeft").SetRange(0, 30).SetUnit("psi")
            //     .AddDefinition($"{playerPrefix}TyrePressure_RearRight").SetRange(0, 30).SetUnit("psi")
            //     .AddDefinition($"{playerPrefix}TyrePressure_FrontLeft").SetRange(0, 30).SetUnit("psi")
            //     .AddDefinition($"{playerPrefix}TyrePressure_FrontRight").SetRange(0, 30).SetUnit("psi")
            //     .AddDefinition($"{playerPrefix}TyreInnerTemp_RearLeft").SetRange(50, 150).SetUnit("°")
            //     .AddDefinition($"{playerPrefix}TyreInnerTemp_RearRight").SetRange(50, 150).SetUnit("°")
            //     .AddDefinition($"{playerPrefix}TyreInnerTemp_FrontLeft").SetRange(50, 150).SetUnit("°")
            //     .AddDefinition($"{playerPrefix}TyreInnerTemp_FrontRight").SetRange(50, 150).SetUnit("°")
            //     .AddDefinition($"{playerPrefix}TyreSurfaceTemp_RearLeft").SetRange(50, 150).SetUnit("°")
            //     .AddDefinition($"{playerPrefix}TyreSurfaceTemp_RearRight").SetRange(50, 150).SetUnit("°")
            //     .AddDefinition($"{playerPrefix}TyreSurfaceTemp_FrontLeft").SetRange(50, 150).SetUnit("°")
            //     .AddDefinition($"{playerPrefix}TyreSurfaceTemp_FrontRight").SetRange(50, 150).SetUnit("°")
            //     .AddDefinition($"{playerPrefix}Status_TyresDamage_RearLeft", $"{playerPrefix}TyresDamage_RearLeft").SetRange(0, 100).SetUnit("%")
            //     .AddDefinition($"{playerPrefix}Status_TyresDamage_RearRight", $"{playerPrefix}TyresDamage_RearRight").SetRange(0, 100).SetUnit("%")
            //     .AddDefinition($"{playerPrefix}Status_TyresDamage_FrontLeft", $"{playerPrefix}TyresDamage_FrontLeft").SetRange(0, 100).SetUnit("%")
            //     .AddDefinition($"{playerPrefix}Status_TyresDamage_FrontRight", $"{playerPrefix}TyresDamage_FrontRight").SetRange(0, 100).SetUnit("%")
            //     .AddDefinition($"{playerPrefix}Status_TyresWear_RearLeft", $"{playerPrefix}TyresWear_RearLeft").SetRange(0, 100).SetUnit("%")
            //     .AddDefinition($"{playerPrefix}Status_TyresWear_RearRight", $"{playerPrefix}TyresWear_RearRight").SetRange(0, 100).SetUnit("%")
            //     .AddDefinition($"{playerPrefix}Status_TyresWear_FrontLeft", $"{playerPrefix}TyresWear_FrontLeft").SetRange(0, 100).SetUnit("%")
            //     .AddDefinition($"{playerPrefix}Status_TyresWear_FrontRight", $"{playerPrefix}TyresWear_FrontRight").SetRange(0, 100).SetUnit("%")
            //     .AddDefinition($"{playerPrefix}SurfaceType_RearLeft")
            //     .AddDefinition($"{playerPrefix}SurfaceType_RearRight")
            //     .AddDefinition($"{playerPrefix}SurfaceType_FrontLeft")
            //     .AddDefinition($"{playerPrefix}SurfaceType_FrontRight");
            parameters.AddLocation($"{root}Telemetry/Engine")
                .AddDefinition($"{playerPrefix}Speed").SetRange(0, 400)
                .AddDefinition($"{playerPrefix}Gear").SetRange(-1, 8)
                //.AddDefinition($"{playerPrefix}DRS", $"{playerPrefix}DRSActive").SetRange(0, 1)
                .AddDefinition($"{playerPrefix}EngineTemp").SetRange(0, 200)
                //.AddDefinition($"{playerPrefix}Clutch").SetRange(0, 200)
                .AddDefinition($"{playerPrefix}EngineRPM").SetRange(0, 20000);
                //.AddDefinition($"{playerPrefix}Status_GearBoxDamage", $"{playerPrefix}GearBoxDamage").SetRange(0, 100);
            parameters.AddLocation($"{root}Telemetry/Misc")
                .AddDefinition($"{playerPrefix}LapDistance").SetUnit("m")
                .AddDefinition($"{playerPrefix}TotalLapDistance").SetUnit("m");
            return this;
        }

        public TimeseriesDefinitionsWriter AddSetup()
        {
            var playerPrefix = isPlayer ? "" : $"Player{playerIndex}_";
            // parameters.AddLocation($"{root}Setup/Misc")
            //     .AddDefinition($"{playerPrefix}Setup_Ballast", $"{playerPrefix}Ballast").SetRange(0, 10).SetUnit("Ballast")
            //     .AddDefinition($"{playerPrefix}Setup_FuelLoad", $"{playerPrefix}FuelLoad").SetRange(0, 10)
            //     .AddDefinition($"{playerPrefix}Setup_OffThrottle", $"{playerPrefix}OffThrottle").SetRange(0, 100).SetUnit("%").SetFormat("{0}%")
            //     .AddDefinition($"{playerPrefix}Setup_OnThrottle", $"{playerPrefix}OnThrottle", "Differential adjustment on throttle (percentage)").SetRange(0, 100).SetUnit("%")
            //     .AddDefinition($"{playerPrefix}Setup_FrontAntiRollBar", $"{playerPrefix}FrontAntiRollBar", "Front anti-roll bar").SetRange(0, 10)
            //     .AddDefinition($"{playerPrefix}Setup_RearAntiRollBar", $"{playerPrefix}RearAntiRollBar", "Rear anti-roll bar").SetRange(0, 10);
            // parameters.AddLocation($"{root}Setup/Wing")
            //     .AddDefinition($"{playerPrefix}Setup_FrontWing", $"{playerPrefix}FrontWing", "Front wing aerodynamics").SetRange(-10, 10).SetUnit("°")
            //     .AddDefinition($"{playerPrefix}Setup_RearWing", $"{playerPrefix}RearWing", "Rear wing aerodynamics").SetRange(-10, 10).SetUnit("°");
            // parameters.AddLocation($"{root}Setup/Tyre")
            //     .AddDefinition($"{playerPrefix}Setup_FrontTyrePressure", $"{playerPrefix}FrontTyrePressure", "Front tyre pressure (PSI)").SetRange(0, 30).SetUnit("psi")
            //     .AddDefinition($"{playerPrefix}Setup_RearTyrePressure", $"{playerPrefix}RearTyrePressure", "Rear tyre pressure (PSI)").SetRange(0, 30).SetUnit("psi");
            // parameters.AddLocation($"{root}Setup/Brake")
            //     .AddDefinition($"{playerPrefix}Setup_BrakeBias", $"{playerPrefix}BrakeBias", "Brake bias").SetRange(0, 100).SetUnit("%")
            //     .AddDefinition($"{playerPrefix}Setup_BrakePressure", $"{playerPrefix}BrakePressure", "Brake pressure").SetRange(0, 100).SetUnit("%");
            // parameters.AddLocation($"{root}Setup/Suspension")
            //     .AddDefinition($"{playerPrefix}Setup_FrontSuspensionHeight", $"{playerPrefix}FrontSuspensionHeight", "Front ride height").SetRange(0, 10)
            //     .AddDefinition($"{playerPrefix}Setup_RearSuspensionHeight", $"{playerPrefix}RearSuspensionHeight", "Rear ride height").SetRange(0, 10)
            //     .AddDefinition($"{playerPrefix}Setup_RearSuspension", $"{playerPrefix}RearSuspension", "Rear suspension").SetRange(0, 10)
            //     .AddDefinition($"{playerPrefix}Setup_FrontSuspension", $"{playerPrefix}FrontSuspension", "Front suspension").SetRange(0, 10)
            //     .AddDefinition($"{playerPrefix}Setup_RearCamber", $"{playerPrefix}RearCamber", "Rear camber angle (suspension geometry)").SetRange(-10, 10).SetUnit("°")
            //     .AddDefinition($"{playerPrefix}Setup_FrontCamber", $"{playerPrefix}FrontCamber", "Front camber angle (suspension geometry)").SetRange(-10, 10).SetUnit("°")
            //     .AddDefinition($"{playerPrefix}Setup_FrontToe", $"{playerPrefix}FrontToe", "Front toe angle (suspension geometry)").SetRange(-5, 5).SetUnit("°")
            //     .AddDefinition($"{playerPrefix}Setup_RearToe", $"{playerPrefix}RearToe", "Rear toe angle (suspension geometry)").SetRange(-5, 5).SetUnit("°");
            return this;
        }
    }
}