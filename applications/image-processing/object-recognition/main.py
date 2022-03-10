from quixstreaming import SecurityOptions, QuixStreamingClient, ParameterData, StreamReader
import time

client = QuixStreamingClient()

# for more samples, please see library or docs

output_topic = client.open_output_topic("{placeholder:topic_processed}")
stream = output_topic.create_stream("input-image")



import cv2
import numpy as np

from datetime import datetime
import base64
import sys
import signal
import threading

def tryDownloadFiles():
    import os
    from os import path
    if path.exists("yolov3.weights") and path.exists("yolov3.cfg"):
        print("Model files present => nothing to download")
        return

    import wget
    from zipfile import ZipFile

    print("Downloading model bundle")
    url = "https://quixstorageaccount.blob.core.windows.net/libraryassets/19519-yolov3.zip"
    weightsFilename = wget.download(url)

    print("Extracting model bundle")
    zf = ZipFile(weightsFilename, 'r')
    zf.extractall('.')
    zf.close()

    os.remove(weightsFilename)
    print("Model ready")



print("-------------------")
print("DOWNLOADING Weights")
url = "https://quixstorageaccount.blob.core.windows.net/libraryassets/19519-image-processing-yolov3.weights"
weightsFilename = wget.download(url)

#Load YOLO Algorithm
net=cv2.dnn.readNet("yolov3.weights","yolov3.cfg")
#To load all objects that have to be detected
classes=[]
with open("coco.names","r") as f:
    read=f.readlines()
for i in range(len(read)):
    classes.append(read[i].strip("\n"))
#Defining layer names
layer_names=net.getLayerNames()
output_layers=[]
for i in net.getUnconnectedOutLayers():
    output_layers.append(layer_names[i[0]-1])


def imgFromBase64(string):
    jpg_original = base64.b64decode(string)
    jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
    img = cv2.imdecode(jpg_as_np, flags=1)
    return img

def imgToBase64(img):
    return base64.b64encode(cv2.imencode('.png', img)[1]).decode()


def processImage(img):
    #Loading the Image
    height,width,channels=img.shape
    #Extracting features to detect objects
    blob=cv2.dnn.blobFromImage(img,0.00392,(416,416),(0,0,0),True,crop=False)
                                                            #Inverting blue with red
                                                            #bgr->rgb
    #We need to pass the img_blob to the algorithm
    net.setInput(blob)
    outs=net.forward(output_layers)
    #Displaying informations on the screen
    class_ids=[]
    confidences=[]
    boxes=[]
    for output in outs:
        for detection in output:
            #Detecting confidence in 3 steps
            scores=detection[5:]                #1
            class_id=np.argmax(scores)          #2
            confidence =scores[class_id]        #3
            if confidence >0.5: #Means if the object is detected
                center_x=int(detection[0]*width)
                center_y=int(detection[1]*height)
                w=int(detection[2]*width)
                h=int(detection[3]*height)
                #Drawing a rectangle
                x=int(center_x-w/2) # top left value
                y=int(center_y-h/2) # top left value
                boxes.append([x,y,w,h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    #Removing Double Boxes
    indexes=cv2.dnn.NMSBoxes(boxes,confidences,0.3,0.4)
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = classes[class_ids[i]]  # name of the objects
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(img, label, (x, y), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)

    return img


input_topic = client.open_input_topic('{placeholder:topic_raw}')
def read_stream(new_stream: StreamReader):

    buffer = new_stream.parameters.create_buffer()

    print("Received new stream")

    def on_parameter_data_handler(data: ParameterData):
        print("Received new parameter")
        for timestamp in data.timestamps:
            ts = timestamp.timestamp_nanoseconds
            string = timestamp.parameters['image'].string_value
            img=imgFromBase64(string)
            start = time.time()
            img=processImage(img)
            delta = start - time.time()

            print(delta)

            stream.parameters.buffer.add_timestamp(datetime.now()) \
                .add_value("image", imgToBase64(img)) \
                .add_value("delta", delta) \
                .write()

        print("Done processing parameters")

    buffer.on_read += on_parameter_data_handler

input_topic.on_stream_received += read_stream
input_topic.start_reading()

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

event = threading.Event()
def signal_handler(sig, frame):
    print('Exiting...')
    event.set()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
event.wait()
