using Android.Runtime;
using System;
using System.Linq;
using System.Threading;
using System.Collections.Concurrent;
using QuixTracker.Services;
using Android.Bluetooth;
using QuixTracker.Models;
using Android.Bluetooth.LE;

namespace QuixTracker.Droid
{
    public class HeartrateStrapCallback : BluetoothGattCallback
    {
        private readonly BlockingCollection<ParameterDataDTO> locationQueue;
        private readonly CurrentData currentData;
        private readonly ConnectionService connectionService;
        private readonly CancellationToken cancellationToken;

        public HeartrateStrapCallback(BlockingCollection<ParameterDataDTO> locationQueue, CurrentData currentData, ConnectionService connectionService, CancellationToken cancellationToken)
        {
            this.locationQueue = locationQueue;
            this.currentData = currentData;
            this.connectionService = connectionService;
            this.cancellationToken = cancellationToken;
        }

        public override void OnConnectionStateChange(BluetoothGatt gatt, [GeneratedEnum] GattStatus status, [GeneratedEnum] ProfileState newState)
        {
            base.OnConnectionStateChange(gatt, status, newState);

            gatt.DiscoverServices();
        }
        public override void OnServicesDiscovered(BluetoothGatt gatt, [GeneratedEnum] GattStatus status)
        {
            base.OnServicesDiscovered(gatt, status);
            var service = gatt.Services[2];

            var characteristics = gatt.Services.SelectMany(s => s.Characteristics);

            var characteristic = characteristics.FirstOrDefault(f => f.Uuid.ToString() == "00002a37-0000-1000-8000-00805f9b34fb");

            gatt.SetCharacteristicNotification(characteristic, true);

            var desc = characteristic.GetDescriptor(characteristic.Descriptors.First().Uuid);
            desc.SetValue(BluetoothGattDescriptor.EnableNotificationValue.ToArray());

            gatt.WriteDescriptor(desc);
        }

        public override void OnCharacteristicChanged(BluetoothGatt gatt, BluetoothGattCharacteristic characteristic)
        {
            base.OnCharacteristicChanged(gatt, characteristic);

            if (!this.cancellationToken.IsCancellationRequested)
            {
                var heartRate = characteristic.GetIntValue(GattFormat.Uint8, 1);

                var timestamp = (long)(DateTime.UtcNow - new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc)).TotalMilliseconds * 1000000;

                this.currentData.Heartrate = heartRate.ShortValue();
                this.connectionService.OnDataReceived(this.currentData);

                this.locationQueue.Add(new ParameterDataDTO
                {
                    Timestamps = new[]
                    {
                        timestamp
                    },
                    NumericValues = new System.Collections.Generic.Dictionary<string, double[]>()
                    {
                        { "HeartRate", new double[] { (int)heartRate } }
                    }
                });


            }

        }

        public override void OnDescriptorWrite(BluetoothGatt gatt, BluetoothGattDescriptor descriptor, [GeneratedEnum] GattStatus status)
        {
            base.OnDescriptorWrite(gatt, descriptor, status);
            gatt.ReadCharacteristic(descriptor.Characteristic);

        }

        public override void OnPhyRead(BluetoothGatt gatt, [GeneratedEnum] ScanSettingsPhy txPhy, [GeneratedEnum] ScanSettingsPhy rxPhy, [GeneratedEnum] GattStatus status)
        {
            base.OnPhyRead(gatt, txPhy, rxPhy, status);
        }

        public override void OnReadRemoteRssi(BluetoothGatt gatt, int rssi, [GeneratedEnum] GattStatus status)
        {
            base.OnReadRemoteRssi(gatt, rssi, status);
        }
    }
}