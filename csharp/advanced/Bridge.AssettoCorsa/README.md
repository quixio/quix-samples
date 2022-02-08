# C# Bridge for Assetto Corsa
This bridge is capable of streaming the game's telemetry (PC or Console) to Quix platform. It is intended to be run on a pc on your local network.

## Requirements / Prerequisites
 - PC or Console on the same network with the Assetto Corsa game running on it.

## Variables

These are the variables that will be replaced in the code (`Program.cs`) if you save this sample as a Quix project:

- **output**: This is the output topic where the game telemetry data will be written
- **HostName**: This is the Assetto Corsa server host
- **Port**: This is the Assetto Corsa server port

## Content of the sample
- `Bridge.AssettoCorsa.sln`: The solution file describing what projects to include
- `Bridge.AssettoCorsa`: Main project implementing all the code needed to read from the game and publish to Quix platform using the SDK. 
  - `Program.cs`: It contains all the relevant code to write the telemetry data in real-time to Quix. It will let you learn and understand how to use our SDK.
- `Bridge.AssettoCorsa.Reader`: Contains game-specific logic for transforming the byte packets to usable data objects.

## Docs
Check out the [SDK Docs](https://quix.ai/docs/sdk/introduction.html) for detailed usage guidance

## How to Run
Run this code locally in a machine with access to the local network.

- Open `Bridge.AssettoCorsa.sln` with your IDE
- Build
- Run `Bridge.AssettoCorsa` project inside IDE or run `Bridge.AssettoCorsa.exe` from the bin folder
