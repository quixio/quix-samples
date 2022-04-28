using System;
using System.Collections.Concurrent;
using System.Timers;

namespace Quix.Snowflake.Domain.Common
{
    /// <summary>
    /// Purpose of this is to have semi-second accurate timer callback without using up a lot of threads
    /// </summary>
    public class InaccurateSharedTimer
    {
        public static readonly InaccurateSharedTimer Instance = new InaccurateSharedTimer();

        private ConcurrentDictionary<Subsccription, object> subscriptions = new ConcurrentDictionary<Subsccription, object>();

        private readonly Timer timer;

        private InaccurateSharedTimer()
        {
            this.timer = new Timer()
            {
                Interval = 1000,
                AutoReset = true,
            };
            timer.Elapsed += (s, a) =>
            {
                foreach (var subscription in subscriptions)
                {
                    if (subscription.Key.Decrement()) subscriptions.TryRemove(subscription.Key, out var _);
                }
            };
            timer.Start();
        }

        public IDisposable Subscribe(int seconds, Action callback)
        {
            if (seconds < 1) throw new ArgumentOutOfRangeException(nameof(seconds));
            if (callback == null) throw new ArgumentNullException(nameof(callback));
            var sub = new Subsccription(seconds, callback);
            this.subscriptions[sub] = new object();
            return sub;
        }

        private class Subsccription : IDisposable
        {
            private int seconds;
            private readonly Action callback;
            private bool disposed = false;

            public Subsccription(int seconds, Action callback)
            {
                this.seconds = seconds;
                this.callback = callback;
            }

            public bool Decrement()
            {
                seconds--;
                if (seconds == 0)
                {
                    callback();
                    return true;
                }

                if (disposed) return true;

                return false;
            }
            
            public void Dispose()
            {
                seconds = -1;
                disposed = true;
            }
        } 
    }
}