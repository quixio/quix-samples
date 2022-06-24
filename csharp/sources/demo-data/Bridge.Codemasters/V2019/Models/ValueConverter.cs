namespace Bridge.Codemasters.V2019.Models
{
    public static class ValueConverter
    {
        public static string ConvertSurfaceId(byte surfaceId)
        {
            switch (surfaceId)
            {
                case 0: return "Tarmac";
                case 1: return "Rumble strip";
                case 2: return "Concrete";
                case 3: return "Rock";
                case 4: return "Gravel";
                case 5: return "Mud";
                case 6: return "Sand";
                case 7: return "Grass";
                case 8: return "Water";
                case 9: return "Cobblestone";
                case 10: return "Metal";
                case 11: return "Ridged";
            }

            return $"unknown ({surfaceId})";
        }

        public static string ConvertTrackId(sbyte convertedTrackId)
        {
            switch (convertedTrackId)
            {
                case 0: return "Melbourne";
                case 1: return "Paul Ricard";
                case 2: return "Shanghai";
                case 3: return "Sakhir (Bahrain)";
                case 4: return "Catalunya";
                case 5: return "Monaco";
                case 6: return "Montreal";
                case 7: return "Silverstone";
                case 8: return "Hockenheim";
                case 9: return "Hungaroring";
                case 10: return "Spa";
                case 11: return "Monza";
                case 12: return "Singapore";
                case 13: return "Suzuka";
                case 14: return "Abu Dhabi";
                case 15: return "Texas";
                case 16: return "Brazil";
                case 17: return "Austria";
                case 18: return "Sochi";
                case 19: return "Mexico";
                case 20: return "Baku (Azerbaijan)";
                case 21: return "Sakhir Short";
                case 22: return "Silverstone Short";
                case 23: return "Texas Short";
                case 24: return "Suzuka Short";
            }

            return $"unknown ({convertedTrackId})";
        }

        public static string ConvertSessionType(byte sessionType)
        {
            switch (sessionType)
            {
                case 0: return "unknown";
                case 1: return "P1";
                case 2: return "P2";
                case 3: return "P3";
                case 4: return "Short P";
                case 5: return "Q1";
                case 6: return "Q2";
                case 7: return "Q3";
                case 8: return "Short Q";
                case 9: return "OSQ";
                case 10: return "R";
                case 11: return "R2";
                case 12: return "Time Trial";
            }

            return $"unknown ({sessionType})";
        }

        public static string ConvertFormula(byte formula)
        {
            switch (formula)
            {
                case 0: return "F1 Modern";
                case 1: return "F1 Classic";
                case 2: return "F2";
                case 3: return "F1 Generic";
            }

            return $"unknown ({formula})";
        }

        public static string ConvertNetworkGame(byte networkGame)
        {
            switch (networkGame)
            {
                case 0: return "Offline";
                case 1: return "Online";
            }

            return $"unknown ({networkGame})";
        }

        public static string ConvertSafetyCarStatus(byte carStatus)
        {
            switch (carStatus)
            {
                case 0: return "no safety car";
                case 1: return "full safety car";
                case 2: return "virtual safety car";
            }

            return $"unknown ({carStatus})";
        }

        public static string ConvertWeather(byte weather)
        {
            switch (weather)
            {
                case 0: return "clear";
                case 1: return "light cloud";
                case 2: return "overcast";
                case 3: return "light rain";
                case 4: return "heavy rain";
                case 5: return "storm";
            }

            return $"unknown ({weather})";
        }
    }
}