using System;

namespace Strava.Watts
{
    public class WattModelOutput
    {
        public double WattOutput { get; set; }
        public double RollingResistence { get; set; }
        public double Gravity { get; set; }
        public double AerodynamicDrag { get; set; }
    }
    
    
    public class WattModel
    {
        private readonly double _weight;
        private const double A = 0.6; // Frontal area A(m2) 
        private const double Cd = 0.63; //Drag coefficient Cd
        private const double LossDt = 2; // Drivetrain loss Lossdt (%
        private const double CPi = 0.01; // Coefficient of rolling resistance Crr
        private const double Rho = 1.22601; //Air density Rho (kg/m3) 

        public WattModel(double weight)
        {
            this._weight = weight;
        }

        public WattModelOutput CalculateWattOutput(double speed, double grade)
        {
            var drivetrainLoss = Math.Pow(1 - (LossDt / 100), -1);

            var gravity = 9.8067 * this._weight * Math.Sin(Math.Atan(grade / 100));
            var rollingResistence = 9.8067 * this._weight * CPi * Math.Cos(Math.Atan(grade / 100));
            var aerodynamicDrag = 0.5 * Cd * A * Rho * Math.Pow(speed, 2);

            var wattOutput = drivetrainLoss * (gravity + rollingResistence + aerodynamicDrag) * speed;

            return new WattModelOutput
            {
                Gravity = gravity,
                AerodynamicDrag = aerodynamicDrag,
                RollingResistence = rollingResistence,
                WattOutput = wattOutput > 0 ? wattOutput : 0
            };
        } 
        
    }
}