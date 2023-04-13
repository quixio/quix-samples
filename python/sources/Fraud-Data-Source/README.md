# Fake transaction generator

[This project](https://github.com/quixio/quix-library/tree/main/python/sources/Fraud-Data-Source) generates fake credit card transaction data, including fraudulent transactions

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Library to use this project.

Clicking `Edit code` on the library item, forks the project to your own Git repo so you can customize it before deploying.

## Environment variables

The code sample uses the following environment variables:

- **producer_topic**: This is the output topic for dummy timeseries data.
- **nb_customers**: Input the number of customers to generate transactions for (Min 5).
- **start_date**: Enter the start date for transactions. YYYY-MM-DD.
- **end_date**: Enter the end date for transactions. YYYY-MM-DD.
- **use_transaction_date**: Use the transaction date as the data timestamp? Yes/No, True/False, 1/0. False value will use date at run time.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-library) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-library) repo.

Please star us and mention us on social to show your appreciation.

