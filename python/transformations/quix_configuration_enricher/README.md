# Quix Configuration Enricher

[This code sample](https://github.com/quixio/quix-samples/tree/main/python/transformations/quix_configuration_enricher) demonstrates how to 
enrich your data using a `Quix Configuration Service` (through a topic managed by the service).

## How to run

Create a [Quix](https://portal.platform.quix.io/signup?xlink=github) account or log-in and visit the Samples to use this project.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.

## Environment Variables

The connector uses the following environment variables:

### Required
- **DATA_TOPIC**: The topic containing your data to be enriched.
- **CONFIG_TOPIC**: The topic managed by your Quix Configuration Service.
- **OUTPUT_TOPIC**: The topic to write the enriched data to.
- **LOOKUP_FIELDS_JSON**: a JSON-serialized string that contains the desired field names with corresponding config field references.  
  ex: `{"f1": {"type": "cfg-name", "default": "value", "jsonpath": "path.to.f1"}, "f2": {"type": "cfg-name", "default": null, "jsonpath": "path.to.f2"}}`

### Optional
- **CONSUMER_GROUP_NAME**: The name of the consumer group to use when consuming from Kafka.  
  Default: `quix-configuration-enricher`

## Requirements / Prerequisites

You will need to have a `Quix Configuration Service` instance running and any desired
configurations actively available on its corresponding topic.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you, and you'll receive $200 in Quix credit.

## Open Source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Please star us and mention us on social media to show your appreciation.