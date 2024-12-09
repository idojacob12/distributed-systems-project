import cv2
import os
import time
import sys
import asyncio
import nats
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get video directory from environment variables
VIDEO_DIRECTORY = os.getenv("VIDEO_DIRECTORY")

async def main():
    async def response_handler(msg):
        print("Received response:", msg.data.decode())


    if not VIDEO_DIRECTORY:
        print("Error: VIDEO_DIRECTORY environment variable is not set.")
        return

    # Connect to NATS server
    nats_url = os.getenv("NATS_URL")
    try:
        nc = await nats.connect(nats_url)
        print(f"Connected to NATS at {nats_url}. Publishing frames from {VIDEO_DIRECTORY}.")
        sys.stdout.flush()
    except Exception as e:
        print(f"Failed to connect to NATS server: {e}")
        return

    await nc.subscribe("alarm_1", cb=response_handler)

    try:
        # Publish frames from all videos in the video directory
        for filename in os.listdir(VIDEO_DIRECTORY):
            curr_sec = 1
            curr_movie = os.path.join(VIDEO_DIRECTORY, filename)
            curr_length_secs = get_video_length(curr_movie)

            while curr_sec < curr_length_secs - 1:
                frame = extract_frame(curr_movie, curr_sec)
                if frame is not None:
                    _, buffer = cv2.imencode('.jpg', frame)
                    await nc.publish("frames_group_1", buffer.tobytes(),reply="alarm_1")
                    print(f"Published frame from {filename} at {curr_sec:.1f}s.")
                    sys.stdout.flush()
                curr_sec += 0.5
                await asyncio.sleep(0.5)  # Simulate real-time delay

    except Exception as e:
        print(f"Error while publishing frames: {e}")
    finally:
        await nc.close()
        print("Disconnected from NATS.")

def get_video_length(video_path):
    """
    This function gets a path to a video and returns its length in seconds.
    """
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    duration = total_frames / fps
    return duration

def extract_frame(video_path, time_in_seconds):
    """
    This function gets the path to the video and a certain time in the video.
    Returns the frame at this certain time.
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_number = int(fps * time_in_seconds)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    success, frame = cap.read()
    cap.release()
    if success:
        return frame
    else:
        print(f"Error: Could not read frame at {time_in_seconds} seconds.")
        return None

if __name__ == "__main__":
    asyncio.run(main())
