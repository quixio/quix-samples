using System.Runtime.InteropServices;

namespace Bridge.Codemasters.V2019.Models.Event
{
    /// <summary>
    /// This packet gives details of events that happen during the course of a session.
    /// Frequency: When the event occurs
    /// Size: 32 bytes
    /// Version: 1
    /// </summary>
    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Auto)]
    public struct PacketEventData : I2019CodemastersPacket
    {
        public PacketHeader Header { get; set;}

        /// <summary>
        /// Event string code
        /// Session Started   - “SSTA”  -  Sent when the session starts
        /// Session Ended     - “SEND”  -  Sent when the session ends
        /// Fastest Lap       - “FTLP”  -  When a driver achieves the fastest lap
        /// Retirement        - “RTMT”  -  When a driver retires
        /// DRS enabled       - “DRSE”  -  Race control have enabled DRS
        /// DRS disabled      - “DRSD”  -  Race control have disabled DRS
        /// Team mate in pits - “TMPT”  - Your team mate has entered the pits
        /// Chequered flag    - “CHQF”  - The chequered flag has been waved
        /// Race Winner       - “RCWN”  - The race winner is announced 
        /// </summary>
        public string EventStringCode;


        /// <summary>
        /// The event details
        /// </summary>
        public IEventDataDetails EventDataDetails;

        public const int SizeOf = 32;
        
        
        public PacketVersion Version => PacketVersion.V2019;
        public PacketType PacketType => PacketType.Event;
        
        public ulong SessionId => Header.SessionUID;
    }
}