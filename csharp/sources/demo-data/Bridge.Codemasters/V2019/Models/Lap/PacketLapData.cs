namespace Bridge.Codemasters.V2019.Models.Lap
{
    /// <summary>
    /// The lap data packet gives details of all the cars in the session.
    /// Frequency: Rate as specified in menus
    /// Size: 843 bytes
    /// Version: 1
    /// </summary>
    public struct PacketLapData : I2019CodemastersPacket
    {

        /// <summary>
        /// World space Y position
        /// </summary>
        public PacketHeader Header { get; set; }


        /// <summary>
        /// World space Y position
        /// </summary>
        public LapData[] LapData; // Lap data for all cars on track

        public const int SizeOf = 843;
        
        
        public PacketVersion Version => PacketVersion.V2019;
        public PacketType PacketType => PacketType.LapData;
        public ulong SessionId => Header.SessionUID;
    }
}