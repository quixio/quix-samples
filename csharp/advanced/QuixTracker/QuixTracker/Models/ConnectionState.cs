namespace QuixTracker.Models
{
    public enum ConnectionState
    {
        Disconnected,
        Reconnecting,
        Connecting,
        Connected,
        Draining
    }
}