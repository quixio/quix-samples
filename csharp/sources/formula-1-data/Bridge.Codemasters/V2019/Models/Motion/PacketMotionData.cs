using System.Runtime.InteropServices;

namespace Bridge.Codemasters.V2019.Models.Motion
{
    /// <summary>
    /// The motion packet gives physics data for all the cars being driven. There is additional data for the car being driven with the goal of being able to drive a motion platform setup.
    /// N.B. For the normalised vectors below, to convert to float values divide by 32767.0f – 16-bit signed values are used to pack the data and on the assumption that direction values are always between -1.0f and 1.0f.
    /// Frequency: Rate as specified in menus
    /// Size: 1343 bytes
    /// Version: 1
    /// </summary>
    [StructLayout(LayoutKind.Sequential)]
    public struct PacketMotionData : I2019CodemastersPacket
    {
        /// <summary>
        /// Header
        /// </summary>
        public PacketHeader Header { get;set; }

        /// <summary>
        /// Data for all cars on track. Extra player car ONLY data
        /// </summary>
        public CarMotionData[] CarMotionData;

        /// <summary>
        /// Note: All wheel arrays have the following order:
        /// RL, RR, FL, FR
        /// </summary>
        public float[] SuspensionPosition;

        /// <summary>
        /// Note: All wheel arrays have the following order:
        /// RL, RR, FL, FR
        /// </summary>
        public float[] SuspensionVelocity;

        /// <summary>
        /// Note: All wheel arrays have the following order:
        /// RL, RR, FL, FR
        /// </summary>
        public float[] SuspensionAcceleration;

        /// <summary>
        /// Speed of each wheel
        /// Note: All wheel arrays have the following order:
        /// RL, RR, FL, FR
        /// </summary>
        public float[] WheelSpeed;

        /// <summary>
        /// Slip ratio for each wheel
        /// Note: All wheel arrays have the following order:
        /// RL, RR, FL, FR
        /// </summary>
        public float[] WheelSlip;

        /// <summary>
        /// Velocity in local space
        /// </summary>
        public float LocalVelocityX;

        /// <summary>
        /// Velocity in local space
        /// </summary>
        public float LocalVelocityY;

        /// <summary>
        /// Velocity in local space
        /// </summary>
        public float LocalVelocityZ;

        /// <summary>
        /// Angular velocity x-component
        /// </summary>
        public float AngularVelocityX;

        /// <summary>
        /// Angular velocity y-component
        /// </summary>
        public float AngularVelocityY;

        /// <summary>
        /// Angular velocity z-component
        /// </summary>
        public float AngularVelocityZ;

        /// <summary>
        /// Angular velocity x-component
        /// </summary>
        public float AngularAccelerationX;

        /// <summary>
        /// Angular velocity y-component
        /// </summary>
        public float AngularAccelerationY;

        /// <summary>
        /// Angular velocity z-component
        /// </summary>
        public float AngularAccelerationZ;

        /// <summary>
        /// Current front wheels angle in radians
        /// </summary>
        public float FrontWheelsAngle;
        
        public const int SizeOf = 1343;
        
        
        public PacketVersion Version => PacketVersion.V2019;
        public PacketType PacketType => PacketType.Motion;
        public ulong SessionId => Header.SessionUID;
    }
}