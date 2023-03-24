import quixstreams as qx
import time
from collections import Counter
import traceback


class QuixFunction:
    def __init__(self, stream_consumer: qx.StreamConsumer, image_processor):
        self.stream_consumer = stream_consumer
        self.image_processor = image_processor
        self.image_processor_classes = self.image_processor.get_classes()

    # Callback triggered for each new parameter data.
    def on_data_handler(self, stream_consumer: qx.StreamConsumer, data: qx.TimeseriesData):
        print("Received new parameter")

        try:
            for timestamp in data.timestamps:
                binary_value = timestamp.parameters['image'].binary_value
                source_img = self.image_processor.img_from_base64(binary_value)
                start = time.time()
                img, class_ids, confidences = self.image_processor.process_image(source_img)
                delta = start - time.time()

                print("Classes :{}".format(self.image_processor_classes))
                print("ClassIDs:{}".format(class_ids))

                counter = Counter(class_ids)

                row = self.stream_consumer.timeseries.buffer \
                    .add_timestamp_nanoseconds(timestamp.timestamp_nanoseconds)

                for key, value in counter.items():
                    print("Key:{}".format(key))
                    row = row.add_value(key, value)

                row.add_value("image", self.image_processor.img_to_binary(img))
                row.add_value("lat", timestamp.parameters["lat"].numeric_value)
                row.add_value("lon", timestamp.parameters["lon"].numeric_value)
                row.add_value("delta", delta)
                row.publish()

            print("Done processing parameters")
        except Exception:
            print(traceback.format_exc())

