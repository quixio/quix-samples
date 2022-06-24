namespace Bridge.Codemasters.V2019.Models.Event
{
    public interface IEventDataDetails
    {

    }

    public struct FastestLapEventDetails : IEventDataDetails
    {
        public byte vehicleIdx; // Vehicle index of car achieving fastest lap

        public float lapTime; // Lap time is in seconds
    }

    public struct RetirementEventDetails : IEventDataDetails
    {
        public byte vehicleIdx; // Vehicle index of car retiring
    }

    public struct TeamMateInPitsEventDetails : IEventDataDetails
    {
        public byte vehicleIdx; // Vehicle index of team mate
    }

    public struct RaceWinnerEventDetails : IEventDataDetails
    {
        public byte vehicleIdx; // Vehicle index of the race winner
    }

    public struct SessionStartedEventDetails : IEventDataDetails
    {

    }

    public struct SessionFinishedEventDetails : IEventDataDetails
    {

    }

    public struct ChequeredFlagWavedEventDetails : IEventDataDetails
    {

    }

    public struct DRSEnabledEventDetails : IEventDataDetails
    {
        public DRSEnabledEventDetails(bool isEnabled)
        {
            this.IsEnabled = isEnabled;
        }

        public readonly bool IsEnabled;
    }
}