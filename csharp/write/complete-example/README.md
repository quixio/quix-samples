# C# Stream write sample
The sample contained in this folder gives an example on how to connect to kafka and write various messages.

# Requirements to run the sample
- A Quix account - [Signup here](https://quix.ai/signup)
- .Net Core 3.0 SDK https://dotnet.microsoft.com/download/dotnet-core/3.0
- An IDE (Microsoft's Visual Studio, JetBrain's Rider or other) to compile it.

# Run the sample
- Open WriteCompleteExample.sln or WriteCompleteExample.csproj with your IDE
- Build
- Run WriteCompleteExample project inside IDE or run WriteCompleteExample.exe from the bin folder

# Content of the sample
- WriteCompleteExample.sln: The solution file describing what projects to include
- WriteCompleteExample/Program.cs: contains logic necessary to connect to and write to a kafka topic
- WriteCompleteExample/Configuration.cs: contains property bag classes to parse the appsettings.json
- WriteCompleteExample/appsettings.json: contains the configuration of the kafka, topic and credentials
- WriteCompleteExample/nlog.config: contains configuration for NLog, the logger currently in use in the streaming library.
- WriteCompleteExample/WriteCompleteExample.csproj: the project file which holds together the project and describes some build related details

# Docs
Check out the [SDK Docs](https://quix.ai/docs/sdk/introduction.html) for detailed usage guidance
