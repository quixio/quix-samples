namespace Bridge.Udp
{
    public class UdpDataPacket
    {
        public UdpDataPacket(byte[] data, string sender)
        {
            this.Data = data;
            this.Sender = sender;
        }
        
        public byte[] Data { get; }
        
        public string Sender { get; }
    }
}