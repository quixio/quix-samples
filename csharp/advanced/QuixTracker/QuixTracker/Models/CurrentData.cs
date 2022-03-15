namespace QuixTracker.Models
{
    public class CurrentData
    {
        public double Speed { get; set; }

        public double Accuracy { get; set; }

        public int LocationBufferSize { get; set; }
        public double Altitude { get; set; }
        public float Bearing { get; set; }
        public int Heartrate { get; set; }

        public string Message { get; set; }
    }
}