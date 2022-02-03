namespace Bridge.Codemasters.Console.Readers.File
{
    public static class TimeHelper
    {
        public static long TimeToWait(long first, long elapsed, long target, double timeDivider)
        {
            if (timeDivider == 0) return 0;
            var rawRemaining = target - elapsed - first;
            if (rawRemaining <= 0) return 0;
            var remaining = rawRemaining / timeDivider;
            return (long) remaining;
        }
    }
}