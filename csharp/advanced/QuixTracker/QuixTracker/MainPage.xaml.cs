using QuixTracker.Views;
using System;
using System.Collections.Generic;
using Xamarin.Essentials;
using Xamarin.Forms;

namespace QuixTracker
{
    public class MainMenuItem
    {
        public string Title { get; set; }
        public Type TargetType { get; set; }
        public string Icon { get; set; }

        public Func<Page> Factory { get; set; }
    }
    public partial class MainPage : MasterDetailPage
    {
        public static MainPage Instance { get; set; }
      

    


        public List<MainMenuItem> MainMenuItems => new List<MainMenuItem>()
        {
            new MainMenuItem() { Title = "Dashboard",TargetType = typeof(Dashboard), Factory = () => new Dashboard() },
            new MainMenuItem() { Title = "Settings", TargetType = typeof(Settings), Factory = () => new Settings()  }
        };

        public MainPage()
        {
            MainPage.Instance = this;
            InitializeComponent();

            BindingContext = this;

            // Build the Menu
 
            // Set the default page, this is the "home" page.
            Detail = new NavigationPage(new Dashboard());
 


            Geolocation.GetLocationAsync(new GeolocationRequest(GeolocationAccuracy.Best)).ContinueWith(_ =>
            {

            });

        }

        protected override void OnAppearing()
        {
            base.OnAppearing();

            Xamarin.Essentials.DeviceDisplay.KeepScreenOn = true;
          
        }

        protected override void OnDisappearing()
        {
            base.OnDisappearing();
            Xamarin.Essentials.DeviceDisplay.KeepScreenOn = false;
        }



        private void MainMenuItem_Selected(object sender, SelectedItemChangedEventArgs e)
        {
            var item = e.SelectedItem as MainMenuItem;
            if (item != null)
            {
                    Detail = new NavigationPage(item.Factory());

                MenuListView.SelectedItem = null;
                IsPresented = false;
            }

        }
    }

    public interface IStartService
    {

        void StartForegroundServiceCompat();

        void StopForegroundServiceCompat();
    }
}
