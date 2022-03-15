using System.Collections.Generic;

namespace QuixTracker.Models
{
    public class ParameterDataDTO
    {

        public int Epoch { get; set; }
        public long[] Timestamps { get; set; }
        public Dictionary<string, double[]> NumericValues { get; set; }
        public Dictionary<string, string[]> StringValues { get; set; }
        public Dictionary<string, string[]> BinaryValues { get; set; }
        public Dictionary<string, string[]> TagValues { get; set; }
    }
}
