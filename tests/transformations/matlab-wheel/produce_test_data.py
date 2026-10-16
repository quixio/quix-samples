import os

from quixstreams import Application

VECTORS = [
    {"x": 1.0, "y": 0.0},
    {"x": 0.0, "y": 1.0},
    {"x": -2.0, "y": 0.0},
]


def main():
    app = Application(broker_address=os.environ["Quix__Broker__Address"])
    topic = app.topic(
        os.environ["TEST_INPUT_TOPIC"], key_serializer="str", value_serializer="json"
    )

    with app.get_producer() as producer:
        for i, vector in enumerate(VECTORS):
            message = topic.serialize(key=str(i), value=vector)
            producer.produce(topic=topic.name, key=message.key, value=message.value)

    print(f"Produced {len(VECTORS)} messages to {topic.name}")


if __name__ == "__main__":
    main()
