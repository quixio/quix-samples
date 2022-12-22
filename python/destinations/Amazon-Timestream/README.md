# Amazon Timestream Sink

Publishes data to Amazon Timestream.

## Requirements / Prerequisites

AWS access key id and secret for a user having permission to perform `timestream:WriteRecords` on
supplied `database_name` and `table_name`.
Optionally, `timestream:CreateDatabase` and `timestream:CreateTable` to auto
create Timestream database and tables for you.

### Example policy for pre-created table

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "timestream:WriteRecords"
      ],
      "Resource": [
        "arn:aws:timestream:region:account:database/database-name/table/table-name"
      ]
    },
    {
      "Effect": "Allow",
      "Action": "timestream:DescribeEndpoints",
      "Resource": "*"
    }
  ]
}
```

### Example policy for creating database and table automatically

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "timestream:WriteRecords",
        "timestream:CreateDatabase",
        "timestream:CreateTable"
      ],
      "Resource": [
        "arn:aws:timestream:region:account:database/quix",
        "arn:aws:timestream:region:account:database/quix/table/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": "timestream:DescribeEndpoints",
      "Resource": "*"
    }
  ]
}
```

## Environment Variables

The code sample uses the following environment variables:

- **input**: Name of the input topic to listen to. `Required`
- **database_name**: Name of the Amazon Timestream database, Default: quix
- **table_name**: Name of the Amazon Timestream table, same as **input** if not provided.
- **batch_size**: Number of records to write in single batch. Minimum 1 to maximum 100. Default: 20
- **mem_store_retention_hours**: The Amazon Timestream table in memory retention time in hours. Default: 6 hours
- **disk_store_retention_days**: The Amazon Timestream table on disk retention time in days. Default: 73000 (200 years)
- **aws_access_key_id**: AWS access key id. `Required`
- **aws_secret_access_key**: AWS secret access key `Required`

## Docs

Check out the [SDK Docs](https://quix.ai/docs/sdk/introduction.html) for detailed usage guidance

## How to Run

Create an account on [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) to Edit or Deploy this
application without a local environment setup.

Alternatively, you can check [here](https://quix.ai/docs/sdk/python-setup.html) how to setup your local environment.