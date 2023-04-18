# Codemasters F1&reg; 2019

F1&reg; 2019 is the official FIA Formula One game series developed by [Codemasters](https://www.codemasters.com). You can take your gaming experience to the next level by live streaming your in-game telemetry data to Quix and performing visualisations, analytics and simulations just like the real Formula One teams do.

[This project](https://github.com/quixio/quix-samples/tree/main/csharp/advanced/Bridge.Codemasters) shows you how to obtain, stream and visualize your F1&reg; 2019 game telemetry from a PC or gaming console using Quix. You can follow the same procedure for later editions of the game as long as the UDP format in the telemetry settings is 2019-compatible.

When running, the project creates individual streams for every race. To locate these go to your Quix workspace and navigate to `Visualize` from the left navigation panel, you will see all the streams and parameters you are streaming.

## How to run

1. Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Library

2. Click `Edit code` on the library item to fork the project to your own Git repo

3. Clone or download the code to your local machine

4. Open `Bridge.Codemasters.sln` with your IDE

5. Update the `appsettings.json` as described below

6. Build

7. Run `Bridge.Codemasters.Console` project in your IDE or run `Bridge.Codemasters.Console.exe` from the bin folder

**This project is intended to be run on a PC on your local network and not deployed within Quix**
**After saving the sample to your workspace, please download or clone the code locally to run it**

### Configure F1&reg; telemetry

While the Quix application is running, fire up the F1&reg; game and navigate to `Game Options` from the main menu.

- Select the `Settings` menu from game options

- From the game settings, navigate to `Telemetry Settings`

- In the telemetry settings, make sure that `UDP Telemetry` is set to `On` and that the UDP port matches the port you configured the dotnet applications `appsettings.json` file. If you are using a later edition of the game, please set the UDP format to 2019.

The steps above expose telemetry data over UDP which is what our client application is listening to. You are all set to go! Open any game mode and start a race. You will see your game telemetry appear on the application console as you race.

## Content of the sample
- Bridge.Codemasters.sln: The solution file describing what projects to include
- Bridge.Codemasters.Console: The console application wiring up the code so it can transform incoming data and send it to quix. This is what you can configure via appsettings.json.
- Bridge.Codemasters.Quix: Contains logic to transform data objects to quix and send it to the platform.
- Bridge.Codemasters: Contains game specific logic for transforming the byte packets to usable data objects.

## Requirements / Prerequisites
 - Codemasters F1&reg; 2019 on PC or Console
 - [Dotnet core runtime](https://dotnet.microsoft.com/download/dotnet/3.0)

## Variables (appsettings.json)

These are the variables on the `appsettings.json` file that you should care about:

- **Topic**: The topic where game data will be output, choose a topic or enter a name for a new one to be created

## UDP or File mode (appsettings.json)
The application has two modes of running. 
- "udp": Set "Input" to "udp". This will listen to UDP packages on the network according to the "UDPInput" configuration
- "file" Set "Input" to "file". This will replay one or more files specified under "FileInput" configuration
More information can be found in Bridge.Codemasters.Console/Configuration/Config.cs

## Details

There is no special setup required for your game station except that it is on the same local network as your PC because the application uses the UDP protocol to receive data from the game and stream it over the internet to Quix.

This is a dotnet core cross platform application that runs on a local computer and streams your game data to Quix. You need to have [dotnet core runtime](https://dotnet.microsoft.com/download/dotnet/3.0) installed on the machine you are going to run this application on. The machine must also be connected to the same network your game station is connected to and it must have an internet connection to stream data to Quix.

If you do not yet have a Quix account, you can sign up for one via our [website](https://quix.io). We assume that you have F1&reg; 2019 game installed on your preferred gaming platform.


## Docs
Check out the [SDK Docs](https://docs.quix.io/sdk-intro.html) for detailed usage guidance


## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.

