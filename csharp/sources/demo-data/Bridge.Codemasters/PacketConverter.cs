using System;
using Bridge.Codemasters.Utils;
using Bridge.Codemasters.V2019.Models;
using Bridge.Codemasters.V2019.Serializers;

namespace Bridge.Codemasters
{
    public class PacketConverter
    {
        public static ICodemastersPacket Convert(byte[] data)
        {
            var version = PacketVersionHelper.DetermineVersion(data);
            switch (version)
            {
                case PacketVersion.V2019:
                    return V2019PacketConverter.Convert(data);
            }

            return null;
        }
    }

    internal class V2019PacketConverter
    {
        public static I2019CodemastersPacket Convert(byte[] data)
        {
            // try V2019
            var header = PacketSerializer.SerializeHeader(data, 0);
            if (header == null) return null;
            if (header.Value.PacketFormat != 2019) return null;

            switch (header.Value.PacketId)
            {
                case PacketType.Motion:
                    return PacketSerializer.SerializePacketMotionData(data, 0);
                case PacketType.Session:
                    return PacketSerializer.SerializePacketSessionData(data, 0);
                case PacketType.LapData:
                    return PacketSerializer.SerializePacketLapData(data, 0);
                case PacketType.Event:
                    return PacketSerializer.SerializePacketEventData(data, 0);
                case PacketType.Participants:
                    return PacketSerializer.SerializePacketParticipantsData(data, 0);
                case PacketType.CarSetups:
                    return PacketSerializer.SerializePacketCarSetupData(data, 0);
                case PacketType.CarTelemetry:
                    return PacketSerializer.SerializePacketCarTelemetryData(data, 0);
                case PacketType.CarStatus:
                    return PacketSerializer.SerializePacketCarStatusData(data, 0);
                default:
                    throw new ArgumentOutOfRangeException();
            }
        }
    }
}