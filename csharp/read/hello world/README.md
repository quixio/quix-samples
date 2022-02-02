# C# Hello World
The sample contained in this folder gives an example on how to connect to kafka and detect the arrival of a new stream and read 'HelloWorld' parameter

# Requirements to run the sample
- .Net Core 3.0 SDK https://dotnet.microsoft.com/download/dotnet-core/3.0
- An IDE (Microsoft's Visual Studio, JetBrain's Rider or other) to compile it.

# Run the sample
- Open ReadHelloWorld.sln with your IDE
- Build
- Run ReadHelloWorld project inside IDE or run ReadHelloWorld.exe from the bin folder

# Content of the sample
- ReadHelloWorld.sln: The solution file describing what projects to include
- ReadHelloWorld/Program.cs: contains logic necessary to connect to kafka topic and read stream
- ReadHelloWorld/ReadHelloWorld.csproj: the project file which holds together the project and describes some build related details
