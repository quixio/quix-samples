using System.Runtime.InteropServices;

namespace Bridge.Codemasters.V2019.Models.CarTelemetry
{
    /// <summary>
    /// This packet details telemetry for all the cars in the race. It details various values that would be recorded on the car such as speed, throttle application, DRS etc.
    /// Frequency: Rate as specified in menus
    /// Size: 1347 bytes
    /// Version: 1
    /// </summary>
    [StructLayout(LayoutKind.Sequential)]
    public struct PacketCarTelemetryData : I2019CodemastersPacket
    {

        /// <summary>
        /// Header
        /// </summary>
        public PacketHeader Header { get; set; }

        /// <summary>
        /// Telemetry data for 20 cars
        /// </summary>
        public CarTelemetryData[] CarTelemetryData;

        /// <summary>
        /// Bit flags specifying which buttons are being pressed currently - see appendices
        /// </summary>
        public uint ButtonStatus;

        public const int SizeOf = 1347;
        
        
        public PacketVersion Version => PacketVersion.V2019;
        public PacketType PacketType => PacketType.CarTelemetry;
        
        public ulong SessionId => Header.SessionUID;
    }
}