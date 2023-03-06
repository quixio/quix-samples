# Reddit

Use [this project](https://github.com/quixio/quix-library/tree/main/python/sources/Reddit) to integrate a Reddit feed into your Quix pipeline

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Library to use this project.

Clicking `Setup & deploy` on the library item, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the library item, forks the project to your own Git repo so you can customize it before deploying.

## Environment variables

The code sample uses the following environment variables:

- **output**: Name of the output topic to write data into.
- **reddit_username**: The Reddit user name to use.
- **reddit_password**: The password to use.
- **reddit_client_id**: The Reddit client id (shown under the app name).
- **reddit_client_secret**: The reddit secret (shown after creating the app in Reddit).
- **subreddit**: The sub Reddit to scrape.

## Requirements/prerequisites

You will need to create a Reddit App [here](https://www.reddit.com/prefs/apps). 

Steps:
- Provide a name
- Choose 'script'
- Provide a description
- Provide a 'redirect uri'
- Click 'create app'

Now you can use the 'client id' and 'secret' to configure the Reddit connector.

![Reddit config](reddit_app.png?raw=true)

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-library) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-library) repo.

Please star us and mention us on social to show your appreciation.

