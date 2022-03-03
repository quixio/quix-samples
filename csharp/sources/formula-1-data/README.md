# C# Bridge for Codemaster's F1 2019
This bridge is capable of streaming the game's telemetry (PC or Console).

## Environment variables

The code sample uses the following environment variables:

- **Topic**: Name of the output topic to write into.

# Requirements to run the sample
- .Net Core 3.0 SDK https://dotnet.microsoft.com/download/dotnet-core/3.0
- An IDE (Microsoft's Visual Studio, JetBrain's Rider or other) to compile it.

# Run the sample
- Open Bridge.Codemasters.sln with your IDE
- Build
- Run Bridge.Codemasters.Console project inside IDE or run Bridge.Codemasters.Console.exe from the bin folder

# Content of the sample
- Bridge.Codemasters.sln: The solution file describing what projects to include
- Bridge.Console: The console application wiring up the code so it can transform incoming data and send it to quix. This is what you need to configure.
- Bridge.Codemasters.Quix: Contains logic to transform data objects to quix and send it to the platform.
- Bridge.Codemasters: Contains game specific logic for transforming the byte packets to usable data objects.
- Bridge.File: Contains logic for recording to or replaying from file.
- Bridge.Readers: Contains an interface which if implemented can be used by Bridge.Codemasters.Console
- Bridge.UDP: Contains logic for exposing UDP packets for IReader interface


# Bridge.Codemasters.Console sppsettings.json
The application has two modes of running. 
- "udp": Set "Input" to "udp". This will listen to UDP packages on the network according to the "UDPInput" configuration.
- "file" Set "Input" to "file". This will replay one or more files specified under "FileInput" configuration.
More information can be found in Bridge.Codemasters.Console/Configuration/Config.cs.
