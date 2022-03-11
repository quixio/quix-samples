# Netatmo source

Netatmo is a company which manufactures smart home devices. 

It offers a set of APIs to consume sensor data from installed devices. See [https://dev.netatmo.com](https://dev.netatmo.com/) 

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

