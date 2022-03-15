using Android.Content;
using System;
using System.Linq;
using System.Threading;
using System.Collections.Concurrent;
using QuixTracker.Services;
using Android.Bluetooth;
using QuixTracker.Models;

namespace QuixTracker.Droid
{
    public class HeartRateDiscovery : IDisposable
    {
        private readonly BluetoothAdapter btAdapter;
        private readonly Context context;
        private readonly ConnectionService connectionService;
        private readonly CurrentData currentData;
        private readonly BlockingCollection<ParameterDataDTO> locationQueue;
        private readonly CancellationToken cancellationToken;
        private BluetoothGatt gatt;
        private bool connecting;

        public HeartRateDiscovery(BluetoothAdapter btAdapter, Context context, ConnectionService connectionService, CurrentData currentData, BlockingCollection<ParameterDataDTO> locationQueue, CancellationToken cancellationToken)
        {
            this.btAdapter = btAdapter;
            this.context = context;
            this.connectionService = connectionService;
            this.currentData = currentData;
            this.locationQueue = locationQueue;
            this.cancellationToken = cancellationToken;
        }

        public void Connect()
        {
            var devices = this.btAdapter.BondedDevices.ToList();
            var heartRateDevice = devices.FirstOrDefault(a => a.Name == "808S 0040986");


            if (heartRateDevice != null)
            {
                if (!connecting)
                {
                    this.gatt = heartRateDevice.ConnectGatt(this.context, false, new HeartrateStrapCallback(this.locationQueue, this.currentData, this.connectionService, this.cancellationToken));
                    //device.FetchUuidsWithSdp();
                    this.connecting = true;
                    //this.btAdapter.BluetoothLeScanner.StartScan(new Callback());


                }

            }
        }

        public void Dispose()
        {
            this.gatt.Dispose();
        }
    }
}