import cv2
import numpy as np
import time
import os
from os import path


class ImageProcessing:
    def __init__(self):
        self.output_layers = []
        self.classes = []
        self.net = None

        print("Creating ImageProcessing(...)")

        def try_download_files():
            if path.exists("yolov3.weights") and path.exists("yolov3.cfg"):
                print("Model files present => nothing to download")
                return

            import wget
            from zipfile import ZipFile

            print("Downloading model bundle")
            time.sleep(1)

            url = "https://quixstorageaccount.blob.core.windows.net/libraryassets/19519-yolov3.zip"
            weights_filename = wget.download(url)

            print("Extracting model bundle")
            zf = ZipFile(weights_filename, 'r')
            zf.extractall('.')
            zf.close()

            os.remove(weights_filename)
            print("Model ready")

        try_download_files()

        # Load YOLO Algorithm
        self.net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
        # To load all objects that have to be detected
        with open("coco.names", "r") as f:
            read = f.readlines()
        for i in range(len(read)):
            self.classes.append(read[i].strip("\n"))

        # Defining layer names
        layer_names = self.net.getLayerNames()

        for i in self.net.getUnconnectedOutLayers():
            self.output_layers.append(layer_names[i[0] - 1])

    def get_classes(self):
        return self.classes

    def img_from_base64(self, jpg_original):
        jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
        img = cv2.imdecode(jpg_as_np, flags=1)
        return img

    def img_to_binary(self, img):
        img_encode = cv2.imencode('.png', img)[1]
        data_encode = np.array(img_encode)
        return data_encode.tobytes()

    def process_image(self, img):
        # Loading the Image
        height, width, channels = img.shape
        # Extracting features to detect objects
        blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        # Inverting blue with red
        # bgr->rgb
        # We need to pass the img_blob to the algorithm
        self.net.setInput(blob)
        outs = self.net.forward(self.output_layers)
        # Displaying information on the screen
        class_ids = []
        confidences = []
        boxes = []
        for output in outs:
            for detection in output:
                # Detecting confidence in 3 steps
                scores = detection[5:]  # 1
                class_id = np.argmax(scores)  # 2
                confidence = scores[class_id]  # 3
                if confidence > 0.5:  # Means if the object is detected
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    # Drawing a rectangle
                    x = int(center_x - w / 2)  # top left value
                    y = int(center_y - h / 2)  # top left value
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        valid_detections = []

        # Removing Double Boxes
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.3, 0.4)
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = self.classes[class_ids[i]]  # name of the objects
                valid_detections.append(label)
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(img, label, (x, y), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)

        return img, valid_detections, confidences
