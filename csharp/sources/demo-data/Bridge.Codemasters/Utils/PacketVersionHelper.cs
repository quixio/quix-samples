using Bridge.Codemasters.V2019.Serializers;

namespace Bridge.Codemasters.Utils
{
    internal static class PacketVersionHelper
    {
        internal static PacketVersion DetermineVersion(byte[] data)
        {
            // try V2019
            var vs2019 = PacketSerializer.SerializeHeader(data, 0);
            if (vs2019 != null)
            {
                if (vs2019.Value.PacketFormat == 2019) return PacketVersion.V2019;
            }

            return PacketVersion.Unknown;
        }
    }
}