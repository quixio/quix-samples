using Android.App;
using Android.Content;
using Android.OS;
using Android.Runtime;
using Android.Views;
using Android.Widget;
using QuixTracker.Droid;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Xamarin.Forms;

[assembly: Dependency(typeof(startServiceAndroid))]
namespace QuixTracker.Droid
{
	public class startServiceAndroid : IStartService
	{
		public void StartForegroundServiceCompat()
		{
			var intent = new Intent(MainActivity.Instance, typeof(PeriodicBackgroundService));


			if (Android.OS.Build.VERSION.SdkInt >= Android.OS.BuildVersionCodes.O)
			{
				MainActivity.Instance.StartForegroundService(intent);
			}
			else
			{
				MainActivity.Instance.StartService(intent);
			}
		}

		public void StopForegroundServiceCompat()
		{
			var intent = new Intent(MainActivity.Instance, typeof(PeriodicBackgroundService));
			MainActivity.Instance.StopService(intent);
		}
	}
}