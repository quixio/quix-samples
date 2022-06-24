namespace Bridge.Codemasters.V2019.Models.CarSetup
{
    public struct CarSetupData
    {
        /// <summary>
        /// Front wing aero
        /// </summary>
        public byte FrontWing;

        /// <summary>
        /// Rear wing aero
        /// </summary>
        public byte RearWing;

        /// <summary>
        /// Differential adjustment on throttle (percentage)
        /// </summary>
        public byte OnThrottle;

        /// <summary>
        /// Differential adjustment off throttle (percentage)
        /// </summary>
        public byte OffThrottle;

        /// <summary>
        /// Front camber angle (suspension geometry)
        /// </summary>
        public float FrontCamber;

        /// <summary>
        /// Rear camber angle (suspension geometry)
        /// </summary>
        public float RearCamber;

        /// <summary>
        /// Front toe angle (suspension geometry)
        /// </summary>
        public float FrontToe;

        /// <summary>
        /// Rear toe angle (suspension geometry)
        /// </summary>
        public float RearToe;

        /// <summary>
        /// Front suspension
        /// </summary>
        public byte FrontSuspension;

        /// <summary>
        /// Rear suspension
        /// </summary>
        public byte RearSuspension;

        /// <summary>
        /// Front anti-roll bar
        /// </summary>
        public byte FrontAntiRollBar;

        /// <summary>
        /// Front anti-roll bar
        /// </summary>
        public byte RearAntiRollBar;

        /// <summary>
        /// Front ride height
        /// </summary>
        public byte FrontSuspensionHeight;

        /// <summary>
        /// Rear ride height
        /// </summary>
        public byte RearSuspensionHeight;

        /// <summary>
        /// Brake pressure (percentage)
        /// </summary>
        public byte BrakePressure;

        /// <summary>
        /// Brake bias (percentage)
        /// </summary>
        public byte BrakeBias;

        /// <summary>
        /// Front tyre pressure (PSI)
        /// </summary>
        public float FrontTyrePressure;

        /// <summary>
        /// Rear tyre pressure (PSI)
        /// </summary>
        public float RearTyrePressure;

        /// <summary>
        /// Ballast
        /// </summary>
        public byte Ballast;

        /// <summary>
        /// Fuel load
        /// </summary>
        public float FuelLoad;

        public const int SizeOf = 41;
    }
}