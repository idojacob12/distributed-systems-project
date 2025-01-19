import asyncio
import time
import nats
import cv2
import os
import sys
import numpy as np
import boto3
import json
import base64
import requests
from dotenv import load_dotenv
from io import BytesIO
from PIL import Image
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Get NATS URL from environment variables
NATS_URL = os.getenv("NATS_URL")

async def process_frame(frame_data):

    # Decode the frame
    frame = np.frombuffer(frame_data, dtype=np.uint8)
    image = cv2.imdecode(frame, cv2.IMREAD_COLOR)
    if image is not None:
        # Load YOLO model
        net = cv2.dnn.readNet("/app/yolov2-tiny.weights", "/app/yolov2-tiny.cfg")
        # Get image size
        (height, width) = image.shape[:2]
        blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        net.setInput(blob)
        output_layer_name = net.getUnconnectedOutLayersNames()
        output_layers = net.forward(output_layer_name)
        # detected people array
        people = []
        for output in output_layers:
            for detection in output:
                detection_scores = detection[5:]
                class_index = np.argmax(detection_scores)
                detection_confidence = detection_scores[class_index]
                if class_index == 0 and detection_confidence > 0.5:
                    detection_width = int(detection[2] * width)
                    detection_height = int(detection[3] * height)
                    detection_center_x = int(detection[0] * width)
                    detection_center_y = int(detection[1] * height)
                    detection_x = int(detection_center_x - detection_width / 2)
                    detection_y = int(detection_center_y - detection_height / 2)
                    people.append((detection_x, detection_y, detection_width, detection_height))

        if(len(people)>0):
            people_image_array = cut_people_image(people,image)
            is_recognized = send_to_lambda(people_image_array)
            return is_recognized
        return "False"
    return "False"

async def run():
    if not NATS_URL:
        print("Error: NATS_URL environment variable is not set.")
        return

    try:
        # Connect to NATS server
        nc = await nats.connect(NATS_URL)
        print(f"Connected to NATS at {NATS_URL}. Subscribing to 'frames'...")
        sys.stdout.flush()

        async def message_handler(msg):
            print(f"Received frame on subject: {msg.subject}")
            sys.stdout.flush()
            alarm = await process_frame(msg.data)
            if(alarm == None):
                alarm="False"
            await msg.respond(alarm.encode())

        # Subscribe to "frames" with a queue group "edge_processors" to load balance messages
        await nc.subscribe(os.getenv("FRAME_GROUP"), cb=message_handler)

        # Keep running
        await asyncio.Event().wait()
    except Exception as e:
        print(f"Failed to connect to NATS server: {e}")

def cut_people_image(people,image):
    cropped_people = []
    for (x, y, w, h) in people:
        img_height, img_width = image.shape[:2]
        # Crop the image using array slicing: image[y:y+h, x:x+w]
        if(x<0):
            x=0
        if (y<0):
            y=0
        if(x+w>img_width):
            w = img_width - x-1
        if y + h > img_height:
            h = img_height - y-1

        cropped_person = image[y:y + h, x:x + w]
        cropped_people.append(cropped_person)

    return cropped_people

def send_to_lambda(people_image_array):
    url = "https://griwo7cpqps4b64gd6qt3u6ogy0qfkpk.lambda-url.us-east-1.on.aws/"
    people_image_base64 = [image_to_base64(image) for image in people_image_array]
    payload = {
        "image_data_list": people_image_base64
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Success:", response.json())
        sys.stdout.flush()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        print(timestamp)
        sys.stdout.flush()
        count=0
        for image in people_image_array:
            image_filename = f"picture_test/processed_frame_{timestamp}_count_{count}.jpg"
            cv2.imwrite(image_filename, image)
            count = count+1
        check_list = {'status': 'unknown'}
        if check_list in response.json():
            return "True"
        return "False"
    else:
        print("Error:", response.status_code, response.text)

def image_to_base64(image_array):
    image = Image.fromarray(image_array)
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    sys.stdout.flush()
    return img_str

if __name__ == "__main__":
    asyncio.run(run())

