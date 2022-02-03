namespace Bridge.Codemasters.V2019.Models
{
    public interface I2019CodemastersPacket : ICodemastersPacket
    {
        PacketType PacketType { get; }

        PacketHeader Header { get; }
    }
}