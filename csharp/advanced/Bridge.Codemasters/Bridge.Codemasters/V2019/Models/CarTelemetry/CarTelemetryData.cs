namespace Bridge.Codemasters.V2019.Models.CarTelemetry
{
    public struct CarTelemetryData
    {
        /// <summary>
        /// Speed of car in kilometres per hour
        /// </summary>
        public ushort Speed;

        /// <summary>
        /// Amount of throttle applied (0.0 to 1.0)
        /// </summary>
        public float Throttle;

        /// <summary>
        /// Steering (-1.0 (full lock left) to 1.0 (full lock right))
        /// </summary>
        public float Steer;

        /// <summary>
        /// Amount of brake applied (0.0 to 1.0)
        /// </summary>
        public float Brake;

        /// <summary>
        /// Amount of clutch applied (0 to 100)
        /// </summary>
        public byte Clutch;

        /// <summary>
        /// Gear selected (1-8, N=0, R=-1)
        /// </summary>
        public sbyte Gear;

        /// <summary>
        /// Engine RPM
        /// </summary>
        public ushort EngineRPM;

        /// <summary>
        /// 0 = off,
        /// 1 = on
        /// </summary>
        public byte Drs;

        /// <summary>
        /// Rev lights indicator (percentage)
        /// </summary>
        public byte RevLightsPercent;

        /// <summary>
        /// Brakes temperature (celsius)
        /// Note: All wheel arrays have the following order:
        /// RL, RR, FL, FR
        /// </summary>
        public ushort[] BrakesTemperature;

        /// <summary>
        /// Tyres surface temperature (celsius)
        /// Note: All wheel arrays have the following order:
        /// RL, RR, FL, FR
        /// </summary>
        public ushort[] TyresSurfaceTemperature;

        /// <summary>
        /// Tyres inner temperature (celsius)
        /// Note: All wheel arrays have the following order:
        /// RL, RR, FL, FR
        /// </summary>
        public ushort[] TyresInnerTemperature;

        /// <summary>
        /// Engine temperature (celsius)
        /// </summary>
        public ushort EngineTemperature;

        /// <summary>
        /// Tyres pressure (PSI)
        /// Note: All wheel arrays have the following order:
        /// RL, RR, FL, FR
        /// </summary>
        public float[] TyresPressure;

        /// <summary>
        /// Driving surface, see appendices
        /// Note: All wheel arrays have the following order:
        /// RL, RR, FL, FR
        /// </summary>
        public byte[] SurfaceType;

        public const int SizeOf = 66;
    }
}