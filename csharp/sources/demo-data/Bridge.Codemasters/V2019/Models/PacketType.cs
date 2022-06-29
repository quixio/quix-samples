namespace Bridge.Codemasters.V2019.Models
{
    public enum PacketType : byte
    {
        /// <summary>
        /// Contains all motion data for player’s car – only sent while player is in control
        /// </summary>
        Motion = 0,
        
        /// <summary>
        /// Data about the session – track, time left
        /// </summary>
        Session = 1,
        
        /// <summary>
        /// Data about all the lap times of cars in the session
        /// </summary>
        LapData = 2,
        
        /// <summary>
        /// Various notable events that happen during a session
        /// </summary>
        Event = 3,
        
        /// <summary>
        /// List of participants in the session, mostly relevant for multiplayer
        /// </summary>
        Participants = 4,
        
        /// <summary>
        /// Packet detailing car setups for cars in the race
        /// </summary>
        CarSetups = 5,
        
        /// <summary>
        /// Telemetry data for all cars
        /// </summary>
        CarTelemetry = 6,
        
        /// <summary>
        /// Status data for all cars such as damage
        /// </summary>
        CarStatus = 7
    }
}