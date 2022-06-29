using System;
using System.Threading;
using Bridge.Codemasters.V2019.Models.CarSetup;
using Bridge.Codemasters.V2019.Models.CarStatus;
using Bridge.Codemasters.V2019.Models.Event;
using Bridge.Codemasters.V2019.Models.Participants;
using Bridge.File;
using Bridge.Readers;
using FluentAssertions;
using Xunit;

namespace Bridge.Codemasters.Tests.Services
{
    public class PacketConverterPacketConverterShould
    {
        /*[Fact]
        public void test()
        {
            var mre = new ManualResetEvent(false);
            var PacketConverter = new PacketConverterPacketConverter(); 
            IOutput output = new FileReader(@"C:\Work\Brdige.Codemasters\Bridge.Console\bin\Debug\netcoreapp3.1\Peter_UDP_Recording_2020_03_19_11_03_52.bin");
            ICodemastersPacket converted = null;
            output.DataPacketRead += (s, a) =>
            {
                var conv = PacketConverter.Convert(a) as PacketParticipantsData?;
                if (conv.HasValue)
                {
                    var fileInput =
                        new FileInput(
                            @"C:\Work\Brdige.Codemasters\Bridge.Console\bin\Debug\netcoreapp3.1\PacketCarSetupData", 0);
                    fileInput.Write(a);
                }
            };

            output.Finished += (sender, args) => { mre.Set(); };

            output.Open();
            mre.WaitOne(TimeSpan.FromSeconds(10));

            converted.Should().NotBeNull();
            var packetCarSetupData = (PacketCarSetupData) converted;
            packetCarSetupData.Should().NotBeNull();
        }*/
        
        [Fact]
        public void Convert_PacketParticipantsData_ShouldConvertToExpected()
        {
            var mre = new ManualResetEvent(false);
            
            IReader reader = new FileReader(@".\Resources\PacketParticipantsData", 0);
            ICodemastersPacket converted = null;
            reader.DataPacketRead += (s, a) =>
            {
                converted = PacketConverter.Convert(a);
            };

            reader.Finished += (sender, args) => { mre.Set(); };

            reader.Open();
            mre.WaitOne(TimeSpan.FromSeconds(10));

            converted.Should().NotBeNull();
            var packetParticipantsData = (PacketParticipantsData) converted;
            packetParticipantsData.Should().NotBeNull();
            packetParticipantsData.Participants[0].Name.Should().Be("Swal");
        }
        
        [Fact]
        public void Convert_PacketCarSetupData_ShouldConvertToExpected()
        {
            var mre = new ManualResetEvent(false);
            
            IReader reader = new FileReader(@".\Resources\PacketCarSetupData", 0);
            ICodemastersPacket converted = null;
            reader.DataPacketRead += (s, a) =>
            {
                converted = PacketConverter.Convert(a);
            };

            reader.Finished += (sender, args) => { mre.Set(); };

            reader.Open();
            mre.WaitOne(TimeSpan.FromSeconds(10));

            converted.Should().NotBeNull();
            var packetCarSetupData = (PacketCarSetupData) converted;
            packetCarSetupData.Should().NotBeNull();
        }
        
        [Fact]
        public void Convert_PacketCarStatusData_ShouldConvertToExpected()
        {
            var mre = new ManualResetEvent(false);
            
            IReader reader = new FileReader(@".\Resources\PacketCarStatusData", 0);
            ICodemastersPacket converted = null;
            reader.DataPacketRead += (s, a) =>
            {
                converted = PacketConverter.Convert(a);
            };

            reader.Finished += (sender, args) => { mre.Set(); };

            reader.Open();
            mre.WaitOne(TimeSpan.FromSeconds(10));

            converted.Should().NotBeNull();
            var packetCarStatusData = (PacketCarStatusData) converted;
            packetCarStatusData.CarStatusData.Length.Should().Be(20);
        }
        
        [Fact]
        public void Convert_PacketCarTelemetryData_ShouldConvertToExpected()
        {
            var mre = new ManualResetEvent(false);
            
            IReader reader = new FileReader(@".\Resources\PacketCarTelemetryData", 0);
            ICodemastersPacket converted = null;
            reader.DataPacketRead += (s, a) =>
            {
                converted = PacketConverter.Convert(a);
            };

            reader.Finished += (sender, args) => { mre.Set(); };

            reader.Open();
            mre.WaitOne(TimeSpan.FromSeconds(10));

            converted.Should().NotBeNull();
        }
        
        [Fact]
        public void Convert_PacketEventData_ShouldConvertToExpected()
        {
            var mre = new ManualResetEvent(false);
            
            IReader reader = new FileReader(@".\Resources\PacketEventData", 0);
            ICodemastersPacket converted = null;
            reader.DataPacketRead += (s, a) =>
            {
                converted = PacketConverter.Convert(a);
            };

            reader.Finished += (sender, args) => { mre.Set(); };

            reader.Open();
            mre.WaitOne(TimeSpan.FromSeconds(10));

            var packetEventData = (PacketEventData) converted;
            var fastestLapEventDetails = (FastestLapEventDetails)packetEventData.EventDataDetails;
            fastestLapEventDetails.vehicleIdx.Should().Be(0);
            fastestLapEventDetails.lapTime.Should().Be(92.6330032f);
        }
        
        [Fact]
        public void Convert_PacketLapData_ShouldConvertToExpected()
        {
            var mre = new ManualResetEvent(false);
            
            IReader reader = new FileReader(@".\Resources\PacketLapData", 0);
            ICodemastersPacket converted = null;
            reader.DataPacketRead += (s, a) =>
            {
                converted = PacketConverter.Convert(a);
            };

            reader.Finished += (sender, args) => { mre.Set(); };

            reader.Open();
            mre.WaitOne(TimeSpan.FromSeconds(10));

            converted.Should().NotBeNull();
        }
        
        [Fact]
        public void Convert_PacketMotionData_ShouldConvertToExpected()
        {
            var mre = new ManualResetEvent(false);
            
            IReader reader = new FileReader(@".\Resources\PacketMotionData", 0);
            ICodemastersPacket converted = null;
            reader.DataPacketRead += (s, a) =>
            {
                converted = PacketConverter.Convert(a);
            };

            reader.Finished += (sender, args) => { mre.Set(); };

            reader.Open();
            mre.WaitOne(TimeSpan.FromSeconds(10));

            converted.Should().NotBeNull();
        }
        
        [Fact]
        public void Convert_PacketSessionData_ShouldConvertToExpected()
        {
            var mre = new ManualResetEvent(false);
            
            IReader reader = new FileReader(@".\Resources\PacketSessionData", 0);
            ICodemastersPacket converted = null;
            reader.DataPacketRead += (s, a) =>
            {
                converted = PacketConverter.Convert(a);
            };

            reader.Finished += (sender, args) => { mre.Set(); };

            reader.Open();
            mre.WaitOne(TimeSpan.FromSeconds(10));

            converted.Should().NotBeNull();
        }
    }
}