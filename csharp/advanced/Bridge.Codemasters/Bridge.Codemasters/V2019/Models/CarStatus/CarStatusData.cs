namespace Bridge.Codemasters.V2019.Models.CarStatus
{
    public struct CarStatusData
    {
        /// <summary>
        /// 0 (off) - 2 (high)
        /// </summary>
        public byte TractionControl;

        /// <summary>
        /// 0 (off) - 1 (on)
        /// </summary>
        public byte AntiLockBrakes;

        /// <summary>
        /// Fuel mix - 0 = lean, 1 = standard, 2 = rich, 3 = max
        /// </summary>
        public byte FuelMix;

        /// <summary>
        /// Front brake bias (percentage)
        /// </summary>
        public byte FrontBrakeBias;

        /// <summary>
        /// Pit limiter status - 0 = off, 1 = on
        /// </summary>
        public byte PitLimiterStatus;

        /// <summary>
        /// Current fuel mass
        /// </summary>
        public float FuelInTank;

        /// <summary>
        /// Fuel capacity
        /// </summary>
        public float FuelCapacity;

        /// <summary>
        /// Fuel remaining in terms of laps (value on MFD)
        /// </summary>
        public float FuelRemainingLaps;

        /// <summary>
        /// Cars max RPM, point of rev limiter
        /// </summary>
        public ushort MaxRPM;

        /// <summary>
        ///  Cars idle RPM
        /// </summary>
        public ushort IdleRPM;

        /// <summary>
        ///  Maximum number of gears
        /// </summary>
        public byte MaxGears;

        /// <summary>
        /// 0 = not allowed,
        /// 1 = allowed,
        /// -1 = unknown
        /// </summary>
        public byte DrsAllowed;

        /// <summary>
        /// Tyre wear percentage
        /// </summary>
        public byte[] TyresWear;

        /// <summary>
        /// F1 Modern -
        /// 16 = C5,
        /// 17 = C4,
        /// 18 = C3,
        /// 19 = C2,
        /// 20 = C1
        /// 7 = inter,
        /// 8 = wet
        /// 
        /// F1 Classic -
        /// 9 = dry,
        /// 10 = wet
        /// 
        /// F2 –
        /// 11 = super soft,
        /// 12 = soft,
        /// 13 = medium,
        /// 14 = hard
        /// 15 = wet
        /// </summary>
        public byte ActualTyreCompound;

        /// <summary>
        /// F1 visual (can be different from actual compound)
        /// 16 = soft,
        /// 17 = medium,
        /// 18 = hard,
        /// 7 = inter,
        /// 8 = wet
        /// F1 Classic –
        /// 9 = dry,
        /// 10 = wet
        /// F2 –
        /// 11 = super soft,
        /// 12 = soft,
        /// 13 = medium,
        /// 14 = hard
        /// 15 = wet
        /// </summary>
        public byte TyreVisualCompound;

        /// <summary>
        /// Tyre damage (percentage)
        /// </summary>
        public byte[] TyresDamage;

        /// <summary>
        /// Front left wing damage (percentage)
        /// </summary>
        public byte FrontLeftWingDamage;

        /// <summary>
        /// Front right wing damage (percentage)
        /// </summary>
        public byte FrontRightWingDamage;

        /// <summary>
        /// Rear wing damage (percentage)
        /// </summary>
        public byte RearWingDamage;

        /// <summary>
        /// Engine damage (percentage)
        /// </summary>
        public byte EngineDamage;

        /// <summary>
        /// Gear box damage (percentage)
        /// </summary>
        public byte GearBoxDamage;

        /// <summary>
        /// -1 = invalid/unknown,
        /// 0 = none,
        /// 1 = green
        /// 2 = blue,
        /// 3 = yellow,
        /// 4 = red
        /// </summary>
        public sbyte VehicleFiaFlags;

        /// <summary>
        /// ERS energy store in Joules
        /// </summary>
        public float ErsStoreEnergy;

        /// <summary>
        /// ERS deployment mode,
        /// 0 = none,
        /// 1 = low,
        /// 2 = medium
        /// 3 = high,
        /// 4 = overtake,
        /// 5 = hotlap
        /// </summary>
        public byte ErsDeployMode;

        /// <summary>
        /// ERS energy harvested this lap by MGU-K
        /// </summary>
        public float ErsHarvestedThisLapMGUK;

        /// <summary>
        /// ERS energy harvested this lap by MGU-H
        /// </summary>
        public float ErsHarvestedThisLapMGUH;

        /// <summary>
        /// ERS energy deployed this lap
        /// </summary>
        public float ErsDeployedThisLap;

        public const int SizeOf = 56;
    }
}