import cv2
import time
import numpy as np
import threading

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.video.video_client import VideoClient
from unitree_sdk2py.go2.sport.sport_client import SportClient

from modules.gesture import GestureRecognizer

print("Starting Gesture Recognition")

ChannelFactoryInitialize(0)

video_client = VideoClient()
video_client.SetTimeout(3.0)
video_client.Init()

sport_client = SportClient()
sport_client.SetTimeout(10.0)
sport_client.Init()

detector = GestureRecognizer()

gesture_actions = {
	"Open_Palm": sport_client.StandUp,
	"Closed_Fist": sport_client.StandDown,
}

last_time = time.time()
delay = 1

code, data = video_client.GetImageSample()

def process_gesture(gesture):
	if gesture in gesture_actions:
		action = gesture_actions[gesture]
		action_thread = threading.Thread(target=action)
		action_thread.start()
		
		print(f"FOUND GESTURE {gesture}")

while code == 0:
	code, data = video_client.GetImageSample()

	image_data = np.frombuffer(bytes(data), dtype=np.uint8)
	frame = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

	frame, current_gesture, _ = detector.detect_gesture(frame)

	current_time = time.time()

	if current_time - last_time >= delay:
		process_gesture(current_gesture["Left"])
		process_gesture(current_gesture["Right"])
		
		last_time = current_time

	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
	
	cv2.imshow('Gesture Recognition', frame)

cv2.destroyAllWindows()
