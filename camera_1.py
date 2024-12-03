import cv2
import os
import time
def main():
    directory = "C:\\Users\\assaf jacob\\OneDrive\\Desktop\\innsbruck semester\\ps dist systems\\final_project\\video_sets\\set_1"
    for filename in os.listdir(directory):
        curr_sec = 1
        curr_movie = os.path.join(directory, filename)
        curr_length_secs = get_video_length(curr_movie)
        while(curr_sec<curr_length_secs-1):
            frame = extract_frame(curr_movie, curr_sec)
            '''
            cv2.imshow("Extracted Frame", frame)
            cv2.waitKey(0)  # Wait until a key is pressed
            cv2.destroyAllWindows()
            '''
            curr_sec+=0.1
            time.sleep(0.1)
def get_video_length(video_path):
    """
    this function gets a path to a video and returns its length in seconds
    """
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    duration = total_frames / fps
    return duration
def extract_frame(video_path, time_in_seconds):
    """
    this function gets the path to the video and a certain time in the video.
    returns the frame in this certain time
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
main()
