import os
import json

from quixstreams.dataframe.joins.lookups.quix_configuration_service import QuixConfigurationService
from quixstreams.dataframe.joins.lookups.quix_configuration_service.lookup import JSONField
from quixstreams import Application


def get_fields():
    """
    The LOOKUP_FIELDS_JSON should be a JSON formatted like this example:
    {
        "f1": {"type": "cfg-name", "default": "value", "jsonpath": "path.to.f1"},
        "f2": {"type": "cfg-name", "default": null, "jsonpath": "path.to.f2"},
        "f3": {"type": "cfg-name", "default": 1.0, "jsonpath": "path.to.f3"},
    }

    If this environment-based approach is too restrictive, replace it with custom logic.
    """
    return {
        field_name: JSONField(**field)
        for field_name, field in json.loads(os.environ["LOOKUP_FIELDS_JSON"]).items()
    }


def main():
    """
    This template deploys a simple enricher using the QuixConfigurationService, which
    enriches by performing a join by adding fields specified by the user in the
    LOOKUP_FIELDS_JSON environment variable.

    The join is achieved by retrieves configs from a specified topic maintained by a
    `Quix Dynamic Configuration Service`.

    The `Quix Dynamic Configuration Service` itself helps manage versioning of configs,
    and the QuixConfigurationService helps streamline interacting with it.

    The respective config applied is based on a combination of message key and the config "type"
    specified.
    """

    app = Application(consumer_group=os.environ["CONSUMER_GROUP_NAME"])

    data_topic = app.topic(name=os.environ["DATA_TOPIC"], key_deserializer="str")
    config_topic = app.topic(name=os.environ["CONFIG_TOPIC"])
    output_topic = app.topic(name=os.environ["OUTPUT_TOPIC"])
    sdf = app.dataframe(topic=data_topic)

    # Enrich data using the config service (lookup_join)
    # Other transformations could be added here if desired.
    sdf = sdf.join_lookup(
        lookup=QuixConfigurationService(
            topic=config_topic,
            app_config=app.config,
        ),
        fields=get_fields()
    )

    # Finish off by writing to the final result to the output topic
    sdf.to_topic(output_topic)
    # With our pipeline defined, now run the Application
    app.run()


if __name__ == '__main__':
    main()