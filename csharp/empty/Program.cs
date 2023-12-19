using System;
using QuixStreams.Streaming;

namespace Service
{
    class Program
    {
        /// <summary>
        /// The service entry point
        /// </summary>
        static void Main(string[] args)
        {
            var client = new QuixStreamingClient();
           
            using var topicConsumer = client.GetTopicConsumer(Environment.GetEnvironmentVariable("input"));
            
            // for more samples, please see samples or docs
            throw new NotImplementedException(""); //
        }
    }
}