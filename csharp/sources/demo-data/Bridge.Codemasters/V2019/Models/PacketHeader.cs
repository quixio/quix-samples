namespace Bridge.Codemasters.V2019.Models
{
    public struct PacketHeader
    {
        /// <summary>
        /// 2019
        /// </summary>
        public ushort PacketFormat;

        /// <summary>
        /// Game major version - "X.00"
        /// </summary>
        public byte GameMajorVersion;

        /// <summary>
        /// // Game minor version - "1.XX"
        /// </summary>
        public byte GameMinorVersion;

        /// <summary>
        /// Version of this packet type, all start from 1
        /// </summary>
        public byte PacketVersion;

        /// <summary>
        /// Identifier for the packet type, see below
        /// </summary>
        public PacketType PacketId;

        /// <summary>
        /// Unique identifier for the session
        /// </summary>
        public ulong SessionUID;

        /// <summary>
        /// Session timestamp
        /// </summary>
        public float SessionTime;

        /// <summary>
        /// Identifier for the frame the data was retrieved on
        /// </summary>
        public uint FrameIdentifier;

        /// <summary>
        /// Index of player's car in the array
        /// </summary>
        public byte PlayerCarIndex;

        public const int SizeOf = 23;
    };
}