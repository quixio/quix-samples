namespace Bridge.Codemasters.V2019.Models.CarSetup
{
    /// <summary>
    /// This packet details the car setups for each vehicle in the session. Note that in multiplayer games, other player cars will appear as blank, you will only be able to see your car setup and AI cars.
    /// Frequency: 2 per second
    /// Size: 843 bytes
    /// Version: 1
    /// </summary>
    public struct PacketCarSetupData : I2019CodemastersPacket
    {
        /// <summary>
        /// Header
        /// </summary>
        public PacketHeader Header { get; set; }

        public CarSetupData[] CarSetups;

        public const int SizeOf = 843;
        
        
        public PacketVersion Version => PacketVersion.V2019;
        public PacketType PacketType => PacketType.CarSetups;
        public ulong SessionId => Header.SessionUID;
    }
}