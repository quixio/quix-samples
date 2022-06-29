namespace Bridge.Codemasters.V2019.Models.Participants
{
    public struct ParticipantData
    {
        /// <summary>
        /// Whether the vehicle is AI (1) or Human (0) controlled
        /// </summary>
        public byte AiControlled;

        /// <summary>
        /// Driver id - see appendix
        /// </summary>
        public byte DriverId;

        /// <summary>
        /// Team id - see appendix
        /// </summary>
        public byte TeamId;

        /// <summary>
        /// Race number of the car
        /// </summary>
        public byte RaceNumber;

        /// <summary>
        /// Nationality of the driver
        /// </summary>
        public byte Nationality;

        /// <summary>
        /// Name of participant in UTF-8 format – null terminated. Will be truncated with … (U+2026) if too long
        /// </summary>
        public string Name;

        /// <summary>
        /// The player's UDP setting, 0 = restricted, 1 = public
        /// </summary>
        public byte YourTelemetry;
        
        public const int SizeOf = 54;
    }
}