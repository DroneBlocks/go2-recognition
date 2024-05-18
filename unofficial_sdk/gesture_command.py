import asyncio
import json
import cv2 
import time
import numpy as np
import os

from mss import mss
from gesture_module import GestureRecognizer
from go2_webrtc import Go2Connection, ROBOT_CMD

def gen_command(cmd: int):
	return json.dumps({
		"type": "msg",
		"topic": "rt/api/sport/request",
		"data": {
			"header": {"identity": {"id": Go2Connection.generate_id(), "api_id": cmd}},
			"parameter": json.dumps(cmd),
		},
	})

async def gesture_recog(robot_conn, use_dog):
	if use_dog:
		await robot_conn.connect_robot()

	detector = GestureRecognizer()

	gesture_actions = {
		"Open_Palm": "StandUp",
		"Closed_Fist": "StandDown",
		"Victory": "Stretch",
		"ILoveYou": "FingerHeart",
		"Thumb_Up": "FrontJump"
	}

	last_time = time.time()
	delay = 1

	cap = cv2.VideoCapture(0)

	os.system("cd go2webrtc-rs | ./target/debug/go2webrtc-rs  --robot 192.168.12.1 | ffplay -i connection.sdp -protocol_whitelist file,udp,rtp  -flags low_delay  -probesize 32  -vf setpts=0")

	if use_dog:
		#cap = cv2.VideoCapture('go2webrtc-rs/connection.sdp', cv2.CAP_ANY)
		pass

	try:
		with mss() as sct:
			while True:
				top, left = (0, 0)
				width, height = (640, 360)
				monitor = {"top": top, "left": left, "width": width, "height": height}
				
				#_, frame = cap.read()
				
				frame = np.array(sct.grab(monitor))
				#frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

				frame, current_gesture = detector.loop_run(frame)

				current_time = time.time()

				if current_time - last_time >= delay:
					for gesture in gesture_actions.keys():
						if gesture == current_gesture["Left"] or gesture == current_gesture["Right"]:
							action = gesture_actions.get(gesture)
							print(f"Gesture detected: {gesture} -> {action}")

							if use_dog:
								robot_cmd = gen_command(ROBOT_CMD[action])
								robot_conn.data_channel.send(robot_cmd)

					last_time = current_time

				if cv2.waitKey(1) & 0xFF == ord('q'):
					break
				
				cv2.imshow('Frame', frame)

				await asyncio.sleep(0.005)
			cap.release() 
			cv2.destroyAllWindows() 
	except asyncio.CancelledError:
		pass

async def main():
	use_dog = False

	if use_dog:
		conn = Go2Connection("192.168.12.1", "<token>")
		
		await conn.connect_robot()
	else:
		conn = None

	try:
		await gesture_recog(conn, use_dog)
	except KeyboardInterrupt:
		print("Interrupted by user, stopping...")
	finally:
		if use_dog:
			await conn.pc.close()
		else:
			pass
	
asyncio.run(main())

