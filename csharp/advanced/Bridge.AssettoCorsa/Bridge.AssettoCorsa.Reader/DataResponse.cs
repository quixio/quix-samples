using System;
using System.IO;
using System.Net;
using System.Text;
using System.Text.Json.Serialization;

namespace Bridge.AssettoCorsa.Reader
{
    /// <summary>
    /// https://docs.google.com/document/d/1KfkZiIluXZ6mMhLWfDX1qAGbvhGRC3ZUzjVIt5FQpp4/pub
    /// </summary>
    public class DataResponse : IUdpResponse
    {
        public string Identifier { get; private set; }
        public int Size { get; private set; }

        public float Speed_Kmh { get; private set; }
        public float Speed_Mph { get; private set; }
        public float Speed_Ms { get; private set; }

        public bool IsAbsEnabled { get; private set; }
        public bool IsAbsInAction { get; private set; }
        public bool IsTcInAction { get; private set; }
        public bool IsTcEnabled { get; private set; }
        public bool IsInPit { get; private set; }
        public bool IsEngineLimiterOn { get; private set; }

        public string Flags { get; private set; } // read_length: 2 # These two bytes are unknown; they do not appear to change from \x00.

        public float AccG_vertical { get; private set; }
        public float AccG_horizontal { get; private set; }
        public float AccG_frontal { get; private set; }

        public int LapTime { get; private set; }
        public int LastLap { get; private set; }
        public int BestLap { get; private set; }
        public int LapCount { get; private set; }

        public float Gas { get; private set; }
        public float Brake { get; private set; }
        public float Clutch { get; private set; }
        public float EngineRPM { get; private set; }
        public float Steer { get; private set; }
        public int Gear { get; private set; }
        public float CgHeight { get; private set; }

        public WheelValues WheelAngularSpeed { get; private set; } = new WheelValues();
        public WheelValues SlipAngle { get; private set; } = new WheelValues();
        public WheelValues SlipAngle_ContactPatch { get; private set; } = new WheelValues();
        public WheelValues SlipRatio { get; private set; } = new WheelValues();
        public WheelValues TyreSlip { get; private set; } = new WheelValues();
        public WheelValues NdSlip { get; private set; } = new WheelValues();
        public WheelValues Load { get; private set; } = new WheelValues();
        public WheelValues Dy { get; private set; } = new WheelValues();
        public WheelValues Mz { get; private set; } = new WheelValues();
        public WheelValues TyreDirtyLevel { get; private set; } = new WheelValues();

        public WheelValues CamberRAD { get; private set; } = new WheelValues();
        public WheelValues TyreRadius { get; private set; } = new WheelValues();
        public WheelValues TyreLoadedRadius { get; private set; } = new WheelValues();


        public WheelValues SuspensionHeight { get; private set; } = new WheelValues();
        public float CarPositionNormalized { get; private set; }
        public float CarSlope { get; private set; }
        public CoordinatesValues CarCoordinates { get; private set; } = new CoordinatesValues();

        [JsonIgnore]
        public IPEndPoint remoteIpEndPoint { get; set; }

        public void ReadFromBytes(byte[] bytes)
        {
            var reader = new BinaryReader(new MemoryStream(bytes));

            this.Identifier = Encoding.Unicode.GetString(reader.ReadBytes(4)).RemoveFrom('\u0000');
            this.Size = reader.ReadInt32();

            if (this.Identifier[0] != 'a') return;

            this.Speed_Kmh = reader.ReadSingle();
            this.Speed_Mph = reader.ReadSingle();
            this.Speed_Ms = reader.ReadSingle();

            this.IsAbsEnabled = reader.ReadBoolean();
            this.IsAbsInAction = reader.ReadBoolean();
            this.IsTcInAction = reader.ReadBoolean();
            this.IsTcEnabled = reader.ReadBoolean();
            this.IsInPit = reader.ReadBoolean();
            this.IsEngineLimiterOn = reader.ReadBoolean();

            this.Flags = Encoding.Unicode.GetString(reader.ReadBytes(2)).RemoveFrom('\u0000');

            this.AccG_vertical = reader.ReadSingle();
            this.AccG_horizontal = reader.ReadSingle();
            this.AccG_frontal = reader.ReadSingle();

            this.LapTime = reader.ReadInt32();
            this.LastLap = reader.ReadInt32();
            this.BestLap = reader.ReadInt32();
            this.LapCount = reader.ReadInt32();

            this.Gas = reader.ReadSingle();
            this.Brake = reader.ReadSingle();
            this.Clutch = reader.ReadSingle();
            this.EngineRPM = reader.ReadSingle();
            this.Steer = reader.ReadSingle();
            this.Gear = reader.ReadInt32() - 1;
            this.CgHeight = reader.ReadSingle();

            this.WheelAngularSpeed.Read(reader);
            this.SlipAngle.Read(reader);
            this.SlipAngle_ContactPatch.Read(reader);
            this.SlipRatio.Read(reader);
            this.TyreSlip.Read(reader);
            this.NdSlip.Read(reader);
            this.Load.Read(reader);
            this.Dy.Read(reader);
            this.Mz.Read(reader);
            this.TyreDirtyLevel.Read(reader);

            this.CamberRAD.Read(reader);
            this.TyreRadius.Read(reader);
            this.TyreLoadedRadius.Read(reader);

            this.SuspensionHeight.Read(reader);
            this.CarPositionNormalized = reader.ReadSingle();
            this.CarSlope = reader.ReadSingle();
            this.CarCoordinates.Read(reader);
        }
    }

    public class WheelValues
    {
        public float Wheel1 { get; private set; }
        public float Wheel2 { get; private set; }
        public float Wheel3 { get; private set; }
        public float Wheel4 { get; private set; }

        internal void Read(BinaryReader reader)
        {
            this.Wheel1 = reader.ReadSingle();
            this.Wheel2 = reader.ReadSingle();
            this.Wheel3 = reader.ReadSingle();
            this.Wheel4 = reader.ReadSingle();
        }
    }

    public class CoordinatesValues
    {
        public float X { get; private set; }
        public float Y { get; private set; }
        public float Z { get; private set; }

        internal void Read(BinaryReader reader)
        {
            this.X = reader.ReadSingle();
            this.Y = reader.ReadSingle();
            this.Z = reader.ReadSingle();
        }
    }

}
