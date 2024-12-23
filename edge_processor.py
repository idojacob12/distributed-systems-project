import asyncio
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
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if class_id == 0 and confidence > 0.5:
                    # Object detected
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    # Rectangle coordinates
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    # Add the detection to the list of people
                    people.append((x, y, w, h))

        # Draw rectangles over people
        #for (x, y, w, h) in people:
        #    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if(len(people)>0):
            print("save picture")
            sys.stdout.flush()
            #cv2.imwrite("processed_frame.jpg", image)
            people_image_array = cut_people(people,image)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"known_faces/processed_frame_{timestamp}.jpg"
            # Save the image with the unique filename
            cv2.imwrite(image_filename, people_image_array[0])
            is_recognized = send_to_lambda(people_image_array)
            return "True"
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
            await msg.respond(alarm.encode())


        # Subscribe to "frames" with a queue group "edge_processors" to load balance messages
        await nc.subscribe(os.getenv("FRAME_GROUP"), cb=message_handler)

        # Keep running
        await asyncio.Event().wait()
    except Exception as e:
        print(f"Failed to connect to NATS server: {e}")

def cut_people(people,image):
    cropped_people = []
    for (x, y, w, h) in people:
        # Crop the image using array slicing: image[y:y+h, x:x+w]
        cropped_person = image[y:y + h, x:x + w]
        cropped_people.append(cropped_person)

    return cropped_people

def send_to_lambda(people_image_array):
    url = "https://griwo7cpqps4b64gd6qt3u6ogy0qfkpk.lambda-url.us-east-1.on.aws/"

    people_image_base64 = [image_to_base64(image) for image in people_image_array]
    payload = {
        "image_data_list": people_image_base64
    }
    # Send a POST request to the Lambda URL
    response = requests.post(url, json=payload)

    # Check the response
    if response.status_code == 200:
        print("Success:", response.json())
    else:
        print("Error:", response.status_code, response.text)

    '''
    print("in lambda")
    sys.stdout.flush()
    # Set your AWS credentials manually (not recommended for production)
    aws_access_key_id = 'ASIAULRCZVITM5F2WEQS'
    aws_secret_access_key = 'XjMfvu6iS0UJCsOWF73ER7X4Aw3K80b4IfqzkH/E'
    region_name = 'us-east-1'  # Replace with your AWS region

    # Initialize a session using your credentials
    lambda_client = boto3.client('lambda', region_name=region_name,
                                 aws_access_key_id=aws_access_key_id,
                                 aws_secret_access_key=aws_secret_access_key)

    for person in people_image_array:
        data = {}
        data_json = json.dumps(data)
        response = lambda_client.invoke(
            FunctionName='hello_world',
            InvocationType='RequestResponse',
            Payload=data_json
        )

    return True
    '''

def image_to_base64(image_array):
    # Convert NumPy image array to PIL Image
    image = Image.fromarray(image_array)

    # Convert the image to a bytes-like object
    buffered = BytesIO()
    image.save(buffered, format="PNG")  # You can use other formats like 'JPEG' or 'PNG'

    # Encode the image in Base64
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_str

if __name__ == "__main__":
    asyncio.run(run())

