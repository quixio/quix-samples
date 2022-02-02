# C# Hello World Model
The sample contained in this folder gives an example on how to create a simple model that downsample 100Hz parameter to 10Hz using built in buffer.

# Requirements to run the sample
- A Quix account - [Signup here](https://quix.ai/signup)
- .Net Core 3.0 SDK https://dotnet.microsoft.com/download/dotnet-core/3.0
- An IDE (Microsoft's Visual Studio, JetBrain's Rider or other) to compile it.

# Run the sample
- Open HelloWorldModel.sln with your IDE
- Build
- Run HelloWorldModel project inside IDE or run HelloWorldModel.exe from the bin folder

# Content of the sample
- HelloWorldModel.sln: The solution file describing what projects to include
- HelloWorldModel/Program.cs: contains logic necessary to connect to kafka topic and read stream, downsample data and write it back to kafka in different topic.
- HelloWorldModel/HelloWorldModel.csproj: the project file which holds together the project and describes some build related details

# Docs
Check out the [SDK Docs](https://quix.ai/docs/sdk/introduction.html) for detailed usage guidance
