# OPC UA Client

[This connector](https://github.com/quixio/quix-samples/tree/main/python/sources/opc_ua_client) allows you to connect to your OPC UA server to capture and handle your data in Quix.

## How to run

Create a [Quix](https://portal.cloud.quix.io/signup?utm_campaign=github) account or log-in and visit the `Connectors` tab to use this connector.

Locate and click the connector tile, fill in the required parameters, then click `Test connection & deploy` to deploy the connector to your Quix instance.

Clicking `Customise` allows you to view or save the code to the repo that backs your Quix cloud instance.

## Environment Variables

The connector uses the following environment variables:

- **output**: Name of the output topic to publish to.
- **PARAMETER_NAMES_TO_PROCESS**: List of parameters from your OPC UA server that you want to process. e.g. ['a', 'b', 'c']. NB:Use single quotes.

The server details come from the shared **`opcua-connection`** Variable Group, so this
source and the bundled OPC UA Server sample stay in agreement:

- **OPC_SERVER_URL**: URL of your OPC UA server (Default: `https://intopcserver:4840/freeopcua/server/`,
  which is the OPC UA Server sample's internal service name)
- **OPC_NAMESPACE**: The namespace of the data coming from your OPC UA server
  (Default: `http://quix.freeopcua.io`)


## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.
