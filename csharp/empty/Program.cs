using System;
using Quix.Sdk.Streaming;
using Quix.Sdk.Streaming.Models;

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
           
            using var inputTopic = client.OpenInputTopic(Environment.GetEnvironmentVariable("input"));
            
            // for more samples, please see samples or docs
            throw new NotImplementedException(""); //
        }
    }
}