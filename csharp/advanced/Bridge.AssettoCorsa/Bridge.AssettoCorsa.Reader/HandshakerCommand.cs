using System.IO;
using System.Net.Sockets;

namespace Bridge.AssettoCorsa.Reader
{
    /// <summary>
    /// https://docs.google.com/document/d/1KfkZiIluXZ6mMhLWfDX1qAGbvhGRC3ZUzjVIt5FQpp4/pub
    /// </summary>
    public class HandshakerCommand: IUdpCommand
    {
        private readonly int Identifier = 1;
        private readonly int Version = 1;
        private readonly HandshackerCommandOperation OperationId;

        public HandshakerCommand(HandshackerCommandOperation operationId)
        {
            OperationId = operationId;
        }

        public byte[] ToByteArray()
        {
            var stream = new MemoryStream();
            var writer = new BinaryWriter(stream);

            writer.Write(this.Identifier);
            writer.Write(this.Version);
            writer.Write((int)this.OperationId);

            return stream.ToArray();
        }
    };

    public enum HandshackerCommandOperation
    {
        // This operation identifier must be set when the client wants to start the communication.
        HANDSHAKE,

        // This operation identifier must be set when the client wants to be updated from the specific ACServer.
        SUBSCRIBE_UPDATE,

        // This operation identifier must be set when the client wants to be updated from the specific ACServer just for SPOT Events (e.g.: the end of a lap).
        SUBSCRIBE_SPOT,

        // This operation identifier must be set when the client wants to leave the communication with ACServer.
        DISMISS,
    }
}
