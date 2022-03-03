namespace Bridge.File
{
    public static class TimeHelper
    {
        public static long TimeToWait(long first, long elapsed, long target, double playbackRate)
        {
            if (playbackRate == 0) return 0;
            var rawRemaining = target - elapsed * playbackRate - first;
            if (rawRemaining <= 0) return 0;
            var remaining = rawRemaining / playbackRate;
            return (long) remaining;
        }
    }
}