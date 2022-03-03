namespace Bridge.Codemasters.V2019.Models.Session
{
    public struct MarshalZone
    {
        /// <summary>
        /// Fraction (0..1) of way through the lap the marshal zone starts
        /// </summary>
        public float ZoneStart;

        /// <summary>
        /// -1 = invalid/unknown, 0 = none, 1 = green, 2 = blue, 3 = yellow, 4 = red
        /// </summary>
        public sbyte ZoneFlag;

        public const int SizeOf = 5;
    }
}