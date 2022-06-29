namespace Bridge.Codemasters.V2019.Models.Session
{
    /// <summary>
    /// The session packet includes details about the current session in progress.
    /// Frequency: 2 per second
    /// Size: 149 bytes
    /// Version: 1
    /// </summary>
    public struct PacketSessionData : I2019CodemastersPacket
    {
        /// <summary>
        /// Header
        /// </summary>
        public PacketHeader Header { get; set; }

        /// <summary>
        /// The weather
        /// </summary>
        public string Weather;

        /// <summary>
        /// Track temp. in degrees celsius
        /// </summary>
        public sbyte TrackTemperature;

        /// <summary>
        /// Air temp. in degrees celsius
        /// </summary>
        public sbyte AirTemperature;

        /// <summary>
        /// Total number of laps in this race
        /// </summary>
        public byte TotalLaps;

        /// <summary>
        /// Track length in metres
        /// </summary>
        public ushort TrackLength;

        /// <summary>
        /// The session type
        /// </summary>
        public string SessionType;

        /// <summary>
        /// The track name
        /// </summary>
        public string Track;

        /// <summary>
        /// Formula
        /// </summary>
        public string Formula;

        /// <summary>
        /// Time left in session in seconds
        /// </summary>                  
        public ushort SessionTimeLeft;

        /// <summary>
        /// Session duration in seconds
        /// </summary>
        public ushort SessionDuration;

        /// <summary>
        /// Pit speed limit in kilometres per hour
        /// </summary>
        public byte PitSpeedLimit;

        /// <summary>
        /// Whether the game is paused
        /// </summary>
        public byte GamePaused;

        /// <summary>
        /// Whether the player is spectating
        /// </summary>
        public byte IsSpectating;

        /// <summary>
        /// Index of the car being spectated
        /// </summary>
        public byte SpectatorCarIndex;

        /// <summary>
        /// SLI Pro support,
        /// 0 = inactive,
        /// 1 = active
        /// </summary>
        public byte SliProNativeSupport;

        /// <summary>
        /// Number of marshal zones to follow
        /// </summary>
        public byte NumMarshalZones;

        /// <summary>
        /// List of marshal zones – max 21
        /// </summary>
        public MarshalZone[] MarshalZones;

        /// <summary>
        /// Safety car status
        /// </summary>
        public string SafetyCarStatus;

        /// <summary>
        /// Network game type (offline // online)
        /// </summary>
        public string NetworkGame;
        
        public const int SizeOf = 149;

        public PacketVersion Version => PacketVersion.V2019;
        public PacketType PacketType => PacketType.Session;
        public ulong SessionId => Header.SessionUID;
    }
}