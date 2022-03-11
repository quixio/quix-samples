using FluentAssertions;
using Xunit;

namespace Bridge.File.Tests
{
    public class TimeHelperShould
    {
        [Theory]
        [InlineData(0, 0, 100, 1, 100)]
        [InlineData(0, 0, 100, 2, 50)]
        [InlineData(0, 0, 100, 0.5, 200)]
        [InlineData(0, 0, 100, 0, 0)]
        [InlineData(50, 0, 100, 1, 50)]
        [InlineData(50, 0, 100, 2, 25)]
        [InlineData(50, 0, 100, 0.5, 100)]
        [InlineData(50, 0, 100, 0, 0)]
        [InlineData(0, 0, 0, 1, 0)]
        [InlineData(0, 0, 0, 2, 0)]
        [InlineData(0, 0, 0, 0.5, 0)]
        [InlineData(0, 0, 0, 0, 0)]
        [InlineData(150, 0, 100, 1, 0)]
        [InlineData(150, 0, 100, 2, 0)]
        [InlineData(150, 0, 100, 0.5, 0)]
        [InlineData(150, 0, 100, 0, 0)]
        [InlineData(0, 50, 100, 1, 50)]
        [InlineData(0, 50, 100, 2, 0)]
        [InlineData(0, 50, 100, 0.5, 150)]
        [InlineData(0, 50, 100, 0, 0)]
        [InlineData(25, 25, 100, 1, 50)]
        [InlineData(25, 25, 100, 2, 12)]
        [InlineData(50, 25, 200, 2, 50)]
        [InlineData(25, 25, 100, 0, 0)]
        public void Test(long first, long elapsed, long target, double timeDivider, long expectedToWait)
        {
            var result = TimeHelper.TimeToWait(first, elapsed, target, timeDivider);
            result.Should().Be(expectedToWait);
        }
    }
}