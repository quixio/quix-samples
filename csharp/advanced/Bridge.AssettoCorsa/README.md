# Assetto Corsa

[This project](https://github.com/quixio/quix-samples/tree/main/csharp/advanced/Bridge.AssettoCorsa) is capable of streaming the game's telemetry (PC or Console) to the Quix platform. It is intended to be run on a pc on your local network.

## Requirements / Prerequisites

 - PC or Console on the same network with the Assetto Corsa game running on it.

## Get the code

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Samples to use this project.

Clicking `Edit code` on the Sample, forks the project to your own Git repo. Clone the code to your local machine to run it.

# How to run

Run on a machine with access to the local network.

- Open `Bridge.AssettoCorsa.sln` with your IDE
- Build
- Run `Bridge.AssettoCorsa` project inside IDE or run `Bridge.AssettoCorsa.exe` from the bin folder

## Variables

These are the variables that will be replaced in the code (`Program.cs`) if you save this sample as a Quix project:

- **output**: This is the output topic where the game telemetry data will be written
- **HostName**: This is the Assetto Corsa server host
- **Port**: This is the Assetto Corsa server port

## Details

- `Bridge.AssettoCorsa.sln`: The solution file describing what projects to include
- `Bridge.AssettoCorsa`: Main project implementing all the code needed to read from the game and publish to Quix platform using the SDK. 
  - `Program.cs`: It contains all the relevant code to write telemetry data in real-time to Quix. It will let you learn and understand how to use our SDK.
- `Bridge.AssettoCorsa.Reader`: Contains game-specific logic for transforming the byte packets to usable data objects.

## Docs

Check out the [SDK Docs](https://docs.quix.io/sdk-intro.html) for detailed usage guidance

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.