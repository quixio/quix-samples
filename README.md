# Quix Code Samples

## Samples repository for the [Quix](https://quix.io) platform. 

The Quix Code Samples contains pre-built, open source code samples that you can use to quickly create a pipeline that transforms data in real time while it travels from source to destination. 

## The samples includes three types of samples: 

Sources: data connectors that you can plug and play. Or add an API gateway to push data. If you have a project in mind but the connector isn’t available, you can develop your own and share the code with Quix users by adding it to the samples repo. You never know what kind of projects you might be supporting.

Transformations: code samples you can use as-is or modify to make your application more functional. Extract and load, merge, synchronize, enrich, predict or anything else you might want to do with your data — the options are endless since you can extend the samples with any class, method, package or library.

Destinations: the connectors to analytics dashboards, alerts, data warehouses and any other form of delivery. What’s the good of transforming data if you can’t easily apply it?

Explore and deploy them using `quix app create` command of the [Quix CLI](https://quix.io/docs/quix-cli/cli-quickstart.html) or use them directly on [Quix Cloud](https://quix.io/docs/quix-cloud/quickstart.html).

## Contributing

Contributors are very welcome at Quix! Follow this guide to get a project into production on the platform.

Fork our samples repo and submit your unique projects to [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit. We might send you a cap or a t-shirt if you fix a bug too!

### Adding a new source, transformation or destination

1. Create a fork of the `quix-samples` repo

2. Add a folder to the directory that best suits your project (e.g., Python>Sources>New Folder)

3. Add your source code to the folder

4. Complete a library.json with the relevant details for your project

	- ensure you follow the guidelines in the Empty folder for each directory

	- ensure you include a thorough README.md that follows the template

	- ensure you include a library.json that follows the template

4.  Submit a PR for approval

### Adding a new application

Applications store all the code to run an end-to-end app. They are made up of multiple projects.

1. Create a fork of the `quix-samples` repo

2. Add a folder to the Applications directory and name it something short and obvious like "chat app with real-time sentiment scoring"

3. Add your source code to the folder

	- Create a sub-folder for each component project of your application, i.e., one for the chat app frontend and one for the real-time machine learning model on the backend

	- ensure you include a library.json with the relevant details

	- ensure you include a thorough README.md that follows the template

	- ensure you follow the guidelines in the Empty folder for each directory

4.  Submit a PR for approval

### Modifying a project

Follow the same pattern used when adding a new application 

1. Create a fork of the `quix-samples` repo

2. Modify your files

3. Check the readme.md and library.json files 

4. Submit a PR for approval

### Configuring library.json

Library.json contains the metadata that we use to provide a smooth developer experience in the Quix portal by powering the search and set-up features in the Samples. Both features make your code more reusable for other developers.

**"libraryItemId"**
A unique identifier for your project.

Create a GUID using an online generator like [Free Online GUID Generator](https://www.guidgenerator.com/online-guid-generator.aspx)


**"name"**
The display name for your project. Keep it short (<30 chars) and try to make it unique.

**"language"**
The projects language (Python, C#, Node.js, Shell Script, Javascript etc)

See here for a current list of languages.

**"tags"**
Additional search filters that show-up in the samples. Pick two or three of the most important tags like "Complexity," "SDK Usage" and "Pipeline State."
See Quix Code Samples for a current list of tags.
Add new tags with discretion — they may not be accepted.

**"shortDescription"**
A unique description of your project. Keep it less than 80 characters.

**"DefaultFile"**
Defines the default file to show when loading the project in a Code Explorer and is the default file displayed in the code preview in the Quix Code Samples.

**"EntryPoint"**

The build and deploy entry point (commonly a Dockerfile).

**"RunEntryPoint"**

The Run entry point (main code file to run).

**"Variables"**

Defines the external variables of the project. 

Variables are used to configure the project during setup in the Quix Code Samples or programatically from your application.

Each variable will create a unique setup field in the Quix Code Samples.

**"Name"** The display name for your variable

**"Type"** The type of variable. Use Environ

**"InputType"**

  - **"HiddenText"** for tokens and credentials 

  - **"FreeText"** for anything else

  - **"InputTopic"** for consuming data from topics. Multiple topics permitted.

  - **"OutputTopic"** for producing data to topics. Multiple topics permitted.

**"Description"** The public description of the variable

**"Required"** Boolean value

**"DefaultValue"** A default value for the variable

**"SampleTemplate"**

Defines whether the project is a Sample Template without ability to Save as Project or Explore the files (used for HTTP samples or similar templates using Placeholders)

**"IconFile"**

Defines an icon file to show in the project card. Optional. 

Only required for recognised logos and technologies - source the official logo.

Required shape: square

Recommended format: .png

Recommended size: 48x48 pixels 

**"DeploySettings"**

Defines the Instant Deploy settings for the project. Optional.

If you configure these properties, the project will have the "Setup & Deploy" button enabled in the Quix Code Samples. This provides users with the option to deploy the project without cloning it to their own repo. It’s particularly useful for connectors (source and destinations) and applications that don’t require customization.

If the settings are null, a Docker Image for this project will not be generated and the Deploy actions will not be available in the UI.

 - **"DeploymentType"**

	Type of deployment. Can be a Service or a Job.

 - **"CpuMillicores"**

	Maximum CPU millicores reserved for this deployment instance. 1 millicore = 1/1000th core

 - **"MemoryInMb"**

	Maximum memory reserved for this deployment instance. 1mb = 1/1000th GB

 - **"Replicas"**

	Number of duplicate instances of the deployment. Used for horizontal scale. 

	Each instance will reserve the max CPU & Memory allocations.

 - **"PublicAccess"**

	Whether the service has a publicly accessible url.

 - **"UrlPrefix"**

	Prefix of the public url.

 - **"ValidateConnection"**

	Whether the Deployment process should validate the connection of the project.

	Specific logic is needed in the code of the project to allow the UI to validate the connection.
