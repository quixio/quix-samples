# C# Bridge for Assetto Corsa
This bridge is capable of streaming the game's telemetry (PC or Console) to Quix platform. It is intended to be run on a pc on your local network.

# Requirements to run the sample
- A Quix account - [Signup here](https://quix.ai/signup)
- .Net Core 3.0 SDK https://dotnet.microsoft.com/download/dotnet-core/3.0
- An IDE (Microsoft's Visual Studio, JetBrain's Rider or other) to compile it.
- PC or Console on the same network with the Assetto Corsa game running on it.

# Run the sample
- Open `Bridge.AssettoCorsa.sln` with your IDE
- Configure `appsettings.json` with the proper parameters for Assetto Corsa. Your Quix parameters and credentials should be already fill it if you have downloaded this sample from Quix platform.
- Build
- Run `Bridge.AssettoCorsa` project inside IDE or run `Bridge.AssettoCorsa.exe` from the bin folder

# Content of the sample
- `Bridge.AssettoCorsa.sln`: The solution file describing what projects to include
- `Bridge.AssettoCorsa`: Main project implementing all the code needed to read from the game and publish to Quix platform using the SDK. 
  - `Program.cs`: It contains all the relevant code to learn and understand how to use our SDK.
  - `appsettings.json`: This file contains all the configuration parameters of the application. ACServer section refers to Assetto Corsa IP and port. Your Quix parameters and credentials should be already fill it if you have downloaded this sample from Quix platform.
- `Bridge.AssettoCorsa.Reader`: Contains game-specific logic for transforming the byte packets to usable data objects.

# Docs
Check out the [SDK Docs](https://quix.ai/docs/sdk/introduction.html) for detailed usage guidance
