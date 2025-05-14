# TSBS Quix Data Generator

Using the [Time Series Benchmark Suite (TSBS)](https://github.com/timescale/tsbs) by Timescale, 
this generates a set of data for doing benchmarks with.

It rolls up the `tsbs_generate_data` and `tsbs_load_*` operations into one simple 
operation, producing data to a specified Quix Cloud topic.

## How to Use

First, we recommend checking out the [TSBS README](https://github.com/timescale/tsbs), 
as this simply extends it to produce data to a Kafka topic.

Just provide the necessary environment variables, which will 
configure how the data is generated, and what topic the data is dumped to.






