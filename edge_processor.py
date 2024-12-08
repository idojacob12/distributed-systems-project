import asyncio
import nats
import cv2
import os
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
        cv2.imwrite("processed_frame.jpg", image)

async def run():
    if not NATS_URL:
        print("Error: NATS_URL environment variable is not set.")
        return

    try:
        # Connect to NATS server
        nc = await nats.connect(NATS_URL)
        print(f"Connected to NATS at {NATS_URL}. Subscribing to 'frames'...")

        async def message_handler(msg):
            print(f"Received frame on subject: {msg.subject}")
            await process_frame(msg.data)

        # Subscribe to "frames" with a queue group "edge_processors" to load balance messages
        await nc.subscribe("frames", "edge_processors", cb=message_handler)

        # Keep running
        await asyncio.Event().wait()
    except Exception as e:
        print(f"Failed to connect to NATS server: {e}")

if __name__ == "__main__":
    asyncio.run(run())

