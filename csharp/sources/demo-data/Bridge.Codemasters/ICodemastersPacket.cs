namespace Bridge.Codemasters
{
    public interface ICodemastersPacket
    {
        PacketVersion Version { get; }

        ulong SessionId { get; }
    }
}