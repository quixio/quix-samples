# C# Bridge for Codemasters F1&reg; 2019

F1&reg; 2019 is the official FIA Formula One game series developed by [Codemasters](https://www.codemasters.com). You can take your gaming experience to the next level by live streaming your in-game telemetry data to Quix and performing visualisations, analytics and simulations just like the real Formula One teams do.

This guide shows you how to obtain, stream and visualise your F1&reg; 2019 game from a PC or gaming console to Quix. You can follow the same procedure for later editions of the game as long as the UDP format in the telemetry settings is 2019-compatible.

**It is intended to be run on a pc on your local network and not deployed within Quix**
**After saving the sample to your workspace please download or clone the code locally to run.**

## Requirements / Prerequisites
 - Codemasters F1&reg; 2019 on PC or Console

## Variables (appsettings.json)

These are the variables on the appsettings.json file that you should care about:

- **Topic**: The topic where game data will be output, choose a topic or enter a name for a new one to be created

## Setup

There is no special setup required for your game station except that it has an internet connection because the application uses UDP protocol to receive data from the game and stream it over the internet to Quix.

We will develop a dotnet core cross platform application that runs on a local computer and streams your game data to Quix. The only requirements are that you have [dotnet core runtime](https://dotnet.microsoft.com/download/dotnet/3.0) installed on the machine you are going to run this application on, that that machine is connected to the same network your game station is connected to and that the machine has an internet connection to connect to Quix.

If you do not yet have a Quix account, you can sign up for one from our [website](https://quix.ai). We assume that you have F1&reg; 2019 game installed on your preferred gaming platform.

## Create a project

All of the sample code will be saved to a project with the name you have entered. 

You will need to download the project code to run it locally, on the same network as your Codemasters F1&reg; 2019 game.

## Content of the sample
- Bridge.Codemasters.sln: The solution file describing what projects to include
- Bridge.Codemasters.Console: The console application wiring up the code so it can transform incoming data and send it to quix. This is what you can configure via appsettings.json.
- Bridge.Codemasters.Quix: Contains logic to transform data objects to quix and send it to the platform.
- Bridge.Codemasters: Contains game specific logic for transforming the byte packets to usable data objects.

## UDP or File mode (appsettings.json)
The application has two modes of running. 
- "udp": Set "Input" to "udp". This will listen to UDP packages on the network according to the "UDPInput" configuration.
- "file" Set "Input" to "file". This will replay one or more files specified under "FileInput" configuration.
More information can be found in Bridge.Codemasters.Console/Configuration/Config.cs.

## Docs
Check out the [SDK Docs](https://quix.ai/docs/sdk/introduction.html) for detailed usage guidance

## How to Run
Run this code locally in a machine with access to the local network.

- Open Bridge.Codemasters.sln with your IDE
- Update the appsettings.json as described above
- Build
- Run Bridge.Codemasters.Console project inside IDE or run Bridge.Codemasters.Console.exe from the bin folder

## Configure F1&reg; telemetry

While the Quix application is running, fire up the F1&reg; game and navigate to "Game Options" from the main menu.

- Select the "Settings" menu from game options.

- From the game settings, navigate to "Telemetry Settings".

- In the telemetry settings, make sure that "UDP Telemetry" is set to "On" and that the UDP port matches the port we configured our dotnet application with. If you are using a later edition of the game, please set the UDP format to 2019.

The steps above expose telemetry data over UDP which is what our client application is listening to. You are all set to go! Open any game mode and start a race. You will see your game telemetry appear on the application console as you race.

The dotnet application is creating individual streams for every race in the topic you initially created. If you go back to the Quix workspace, navigate to visualise from the left navigation panel, you can see all the streams and parameters you are streaming.

Select stream(s) and parameter(s) you like, and you can view and analyse your performance using our [Visualize](https://quix.ai/docs/guides/how-to/visualize/index.html) feature.
