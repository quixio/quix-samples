# Demo CSV Data

[This project](https://github.com/quixio/quix-samples/tree/main/python/sources/simple_csv) streams data from a three column CSV file into a topic.

The sample is a demonstration of how you can publish your own CSV data into Quix.
See `Timeseries data`, below, for more info.

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Samples to use this project.

Clicking `Deploy` on the Sample, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.

## Environment variables

The code sample uses the following environment variables:

- **Topic**: Name of the output topic to write into.

## Your data

To publish your own data, replace the CSV data with your own.

After saving the sample to your workspace, you can copy and paste your data into the CSV file or upload your own CSV file and change the python code to look for your CSV file name instead of `demo-data.csv`.

### Timeseries data

If your data timeseries data and has a `Timestamp` column, this will be used to ensure the timing of the published data is similar to the timing of the published data.
e.g. if your data has gaps between the timestamps of 1, 2 and 5 seconds then the code will pause for 1, 2 and 5 seconds between those rows.

You can also choose to disable this functionality by changing `keep_timing` to `False`.

It's fine if your data does not have a `Timestamp` column, we generate the timestamps anyway so you can see the data appearing live in views line the live data explorer.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.

