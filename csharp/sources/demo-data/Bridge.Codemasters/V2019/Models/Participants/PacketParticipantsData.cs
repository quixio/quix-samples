namespace Bridge.Codemasters.V2019.Models.Participants
{
    /// <summary>
    /// This is a list of participants in the race. If the vehicle is controlled by AI, then the name will be the driver name. If this is a multiplayer game, the names will be the Steam Id on PC, or the LAN name if appropriate.
    /// N.B. on Xbox One, the names will always be the driver name, on PS4 the name will be the LAN name if playing a LAN game, otherwise it will be the driver name.
    /// The array should be indexed by vehicle index.
    /// Frequency: Every 5 seconds
    /// Size: 1104 bytes
    /// Version: 1
    /// </summary>
    public struct PacketParticipantsData : I2019CodemastersPacket
    {

        /// <summary>
        /// Header
        /// </summary>
        public PacketHeader Header { get; set; }


        /// <summary>
        /// Number of active cars in the data – should match number of cars on HUD
        /// </summary>
        public byte NumActiveCars;

        /// <summary>
        /// 
        /// </summary>
        public ParticipantData[] Participants;
        
        public const int SizeOf = 1104;

        public PacketVersion Version => PacketVersion.V2019;
        public PacketType PacketType => PacketType.Participants;
        public ulong SessionId => Header.SessionUID;
    }
}