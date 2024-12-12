import asyncio
import nats
import cv2
import os
import sys
import numpy as np
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get NATS URL from environment variables
NATS_URL = os.getenv("NATS_URL")

async def process_frame(frame_data):
    # Decode the frame
    frame = np.frombuffer(frame_data, dtype=np.uint8)
    image = cv2.imdecode(frame, cv2.IMREAD_COLOR)

    if image is not None:
        # Example: Save the processed frame
        #cv2.imwrite("processed_frame.jpg", image)


        # Load YOLO model
        net = cv2.dnn.readNet("/app/yolov2-tiny.weights", "/app/yolov2-tiny.cfg")

        # Get image dimensions
        (height, width) = image.shape[:2]

        # Define the neural network input
        blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        net.setInput(blob)

        # Perform forward propagation
        output_layer_name = net.getUnconnectedOutLayersNames()
        output_layers = net.forward(output_layer_name)

        # Initialize list of detected people
        people = []

        # Loop over the output layers
        for output in output_layers:
            # Loop over the detections
            for detection in output:
                # Extract the class ID and confidence of the current detection
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                # Only keep detections with a high confidence
                if class_id == 0 and confidence > 0.5:
                    # Object detected
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    # Rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    # Add the detection to the list of people
                    people.append((x, y, w, h))

        # Draw bounding boxes around the people
        for (x, y, w, h) in people:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        if(len(people)>0):
            print("save picture")
            sys.stdout.flush()
            cv2.imwrite("processed_frame.jpg", image)
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

if __name__ == "__main__":
    asyncio.run(run())

