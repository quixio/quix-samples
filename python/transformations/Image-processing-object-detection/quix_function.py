from quixstreaming import StreamWriter, ParameterData
import time
from collections import Counter
import traceback


class QuixFunction:
    def __init__(self, output_stream: StreamWriter, image_processor):
        self.output_stream = output_stream
        self.image_processor = image_processor
        self.image_processor_classes = self.image_processor.get_classes()

    # Callback triggered for each new parameter data.
    def on_parameter_data_handler(self, data: ParameterData):
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

                row = self.output_stream.parameters.buffer.add_timestamp_nanoseconds(timestamp.timestamp_nanoseconds) 

                for key, value in counter.items():
                    print("Key:{}".format(key))
                    row = row.add_value(key, value)

                row.add_value("image", self.image_processor.img_to_binary(img)) \
                    .add_value("lat", timestamp.parameters["lat"].numeric_value) \
                    .add_value("lon", timestamp.parameters["lon"].numeric_value) \
                    .add_value("delta", delta) \
                    .write()

            print("Done processing parameters")
        except Exception:
            print(traceback.format_exc())

