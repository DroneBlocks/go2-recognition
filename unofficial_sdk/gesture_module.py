import cv2
import mediapipe as mp
from mediapipe.tasks import python
import threading

class GestureRecognizer:
    def __init__(self, flip_results = True, model_path="./models/gesture_recognizer.task", num_hands=2, tracking_confidence=0.5, detection_confidence=0.5):
        self.num_hands = num_hands
        self.tracking_confidence = tracking_confidence
        self.detection_confidence = detection_confidence
        self.flip_results = flip_results

        self.hand_gestures_dict = {
            "Left": "None",
            "Right": "None"
        }

        GestureRecognizer = mp.tasks.vision.GestureRecognizer
        GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        self.lock = threading.Lock()
        options = GestureRecognizerOptions(
            base_options=python.BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.LIVE_STREAM,
            num_hands=self.num_hands,
            result_callback=self.results_callback
        )
        self.recognizer = GestureRecognizer.create_from_options(options)

        self.timestamp = 0
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=self.num_hands,
            min_detection_confidence=self.detection_confidence,
            min_tracking_confidence=self.tracking_confidence
        )

    def detect_gesture(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_bgr)
            self.recognizer.recognize_async(mp_image, self.timestamp)
            self.timestamp += 1
        else:
            with self.lock:
                self.hand_gestures_dict["Left"] = "None"
                self.hand_gestures_dict["Right"] = "None"
        
        return frame, self.hand_gestures_dict, results

    def results_callback(self, result, output_image, timestamp_ms):
        with self.lock:
            if result and any(result.gestures):
                for index, hand in enumerate(result.handedness):
                    hand_name = hand[0].category_name
                    current_hand_gesture = result.gestures[index][0].category_name
                    if self.flip_results:
                        corrected_hand_name = "Right" if hand_name == "Left" else "Left"
                    self.hand_gestures_dict[corrected_hand_name] = current_hand_gesture
