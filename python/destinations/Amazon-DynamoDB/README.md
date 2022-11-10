# Amazon DynamoDB Sink

Publishes data to DynamoDB.

## Requirements / Prerequisites

AWS access key id and secret for a user having permission to perform `dynamodb:BatchWriteItem` on supplied `table_name`.
Optionally, `dynamodb:CreateTable` on resource `arn:aws:dynamodb:region:account-id:table/quix-*` for connector to auto
create DynamoDB table for you.

### Example policy for pre-created table

```json
{
  "Effect": "Allow",
  "Action": [
    "dynamodb:BatchWriteItem"
  ],
  "Resource": [
    "arn:aws:dynamodb:region:account-id:table/my_table"
  ]
}
```

### Example policy for creating table automatically

```json
{
  "Effect": "Allow",
  "Action": [
    "dynamodb:CreateTable",
    "dynamodb:BatchWriteItem"
  ],
  "Resource": [
    "arn:aws:dynamodb:region:account-id:table/quix-*"
  ]
}
```

## Environment Variables

The code sample uses the following environment variables:

- **input**: Name of the input topic to listen to. `Required`
- **table_name**: Name of the Amazon DynamoDB table, same as **input** if not provided.
- **aws_access_key_id**: AWS access key id. `Required`
- **aws_secret_access_key**: AWS secret access key `Required`
- **max_retry**: Max reties for failed batch of records
- **param_partition_key**: Parameter name to be used as partition key.
- **param_sort_key**: Parameter name to be used as sort key.

### Using param_partition_key and param_sort_key

Environment variables `param_partition_key` and `param_sort_key` can take any of below values:

1. Direct string type parameter name from the message OR
2. Derived key attribute name and [strftime](https://docs.python.org/3/library/datetime.html#datetime.date.strftime)
   pattern joined
   by pipe `|`. (e.g. `hour_of_day|%Y-%m-%d %H`)

For example message,

```json
{
  "timestamp": 1667844200703123, // 2022-11-07 19:03:20.703123
  "key1": "value1",
  "key2": 10,
  "key3": "value3"
}
```

### Example 1

```
# Note: Only string type parameter is allowed as parition key and sort key at the time.
param_partition_key = key1
param_sort_key = key3

DynamoDB Record

key1 (PK) | key3 (SK)     | timestamp (N)        | key2 (N)
value1    | value3        | 1667844200703123     | 10
```

### Example 2

```
param_partition_key = year_month|%Y-%m
param_sort_key = rest_of_ts|%d-%H:%M:%S.%f

DynamoDB Record

year_month (PK) | rest_of_ts (SK)     | timestamp (N)    | key1 (S)   | key2 (N) | key3 (S)
2022-11         | 07-19:03:20.703123  | 1667844200703123 | value1     | 10       | value3
```

### Example 3

```
param_partition_key = my_date_time|%Y-%m-%dT%H:%M:%S.%f
param_sort_key = (empty)

DynamoDB Record

my_date_time (PK)           | timestamp (N)    | key1 (S)   | key2 (N) | key3 (S)
2022-11-07T19:03:20.703123  | 1667844200703123 | value1     | 10       | value3
```

## Docs

Check out the [SDK Docs](https://quix.ai/docs/sdk/introduction.html) for detailed usage guidance

## How to Run

Create an account on [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) to Edit or Deploy this
application without a local environment setup.

Alternatively, you can check [here](https://quix.ai/docs/sdk/python-setup.html) how to setup your local environment.