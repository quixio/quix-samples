# Netatmo

Netatmo is a company that manufactures smart home devices. 

[This project](https://github.com/quixio/quix-library/tree/main/python/sources/Netatmo){target="_blank"} allows you to connect to to their APIs to consume sensor data from installed devices. See [https://dev.netatmo.com](https://dev.netatmo.com/) 

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Library to use this project.

Clicking `Edit code` on the library item, forks the project to your own Git repo so you can customize it before deploying.

## Environment variables

The code sample uses the following environment variables:

- **output**: This is the output topic for Netatmo data.
- **client_id**: Your Netatmo app client id.
- **client_secret**: Your Netatmo app client secret.
- **username**: Your Netatmo account username.
- **password**: Your Netatmo account password.
- **device_id**: Your Netatmo device id.

### Netatmo Dev App
- In [Dev portal](https://dev.netatmo.com/), go to profile submenu in right top corner and enter **My apps** page.
- Create a new app and you will recieve:
  - **client_id**: ID of your app.
  - **client_secret**: Secret of your app.

### Netatmo device
- Go to your [Netatmo app](https://my.netatmo.com/app/station) and in the **Settings** menu enter **Manage my home**
- Find your device and copy **MAC address**
  - **device_id**: MAC address of your device.

### User account
- **username**: Email you use to log in into the Netatmo app.
- **password**: Password you use to log in into the Netatmo app.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-library){target="_blank"} repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-library){target="_blank"} repo.

Please star us and mention us on social to show your appreciation.

