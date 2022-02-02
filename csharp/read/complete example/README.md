# C# Stream read sample
The sample contained in this folder gives an example on how to connect to kafka and read various messages.

# Requirements to run the sample
- A Quix account - [Signup here](https://quix.ai/signup)
- .Net Core 3.0 SDK https://dotnet.microsoft.com/download/dotnet-core/3.0
- An IDE (Microsoft's Visual Studio, JetBrain's Rider or other) to compile it.

# Run the sample
- Open ReadCompleteExample.sln or ReadCompleteExample.csproj with your IDE
- Build
- Run ReadCompleteExample project inside IDE or run ReadCompleteExample.exe from the bin folder

# Content of the sample
- ReadCompleteExample.sln: The solution file describing what projects to include
- ReadCompleteExample/Program.cs: contains logic necessary to connect to and read from a kafka topic
- ReadCompleteExample/Configuration.cs: contains property bag classes to parse the appsettings.json
- ReadCompleteExample/appsettings.json: contains the configuration of the kafka, topic and credentials
- ReadCompleteExample/nlog.config: contains configuration for NLog, the logger currently in use in the streaming library.
- ReadCompleteExample/ReadCompleteExample.csproj: the project file which holds together the project and describes some build related details

# Docs
Check out the [SDK Docs](https://quix.ai/docs/sdk/introduction.html) for detailed usage guidance
