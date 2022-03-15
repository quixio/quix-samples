using Android.App;
using System;
using AndroidX.Core.App;

namespace QuixTracker.Droid
{
	public class NotificationService
	{
		private readonly NotificationManager notificationManager;
		private readonly Service parentService;

		public NotificationService(NotificationManager notificationManager, Android.App.Service parentService)
		{
			this.notificationManager = notificationManager;
			this.parentService = parentService;
		}

		public void SendForegroundNotification(string title, string content)
		{
			Notification notification = CreateNotification(title, content);

			try
			{
				this.parentService.StartForeground(1, notification, Android.Content.PM.ForegroundService.TypeLocation);
			}
			catch
			{
				this.parentService.StartForeground(1, notification);
			}
		}

		public void SendNotifcation(string title, string content)
		{
			Notification notification = CreateNotification(title, content);

			this.notificationManager.Notify(2, notification);
		}

		private Notification CreateNotification(string title, string content)
		{
			String CHANNEL_ID = "my_channel_01";
			NotificationChannel channel = new NotificationChannel(CHANNEL_ID,
					"Quix tracking app",
					NotificationImportance.High);


			var notification = new NotificationCompat.Builder(this.parentService, CHANNEL_ID)
			  .SetAutoCancel(true) // Dismiss the notification from the notification area when the user clicks on it
			  .SetContentTitle(title) // Set the title
									  //.SetContentIntent(resultPendingIntent)
			  .SetNumber(3) // Display the count in the Content Info
			  .SetSmallIcon(Resource.Drawable.notification_tile_bg) // This is the icon to display
			  .SetContentText(content).Build();

			this.notificationManager.CreateNotificationChannel(channel);
			return notification;
		}
	}
}