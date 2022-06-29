using System.Runtime.InteropServices;

namespace Bridge.Codemasters.V2019.Models.CarStatus
{
    /// <summary>
    /// This packet details car statuses for all the cars in the race. It includes values such as the damage readings on the car.
    /// Frequency: Rate as specified in menus
    /// Size: 1143 bytes
    /// Version: 1
    /// </summary>
    [StructLayout(LayoutKind.Sequential)]
    public struct PacketCarStatusData : I2019CodemastersPacket
    {
        /// <summary>
        /// Header
        /// </summary>
        public PacketHeader Header { get; set; }

        public CarStatusData[] CarStatusData;

        public const int SizeOf = 1143;
        
        
        public PacketVersion Version => PacketVersion.V2019;
        public PacketType PacketType => PacketType.CarStatus;
        
        public ulong SessionId => Header.SessionUID;
    }
}