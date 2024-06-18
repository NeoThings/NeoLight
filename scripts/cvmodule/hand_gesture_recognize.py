import argparse
import sys
import time

import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


# Global variables to calculate FPS
COUNTER, FPS = 0, 0
START_TIME = time.time()

class HandGesture():
    def __init__(self, model: str, num_hands: int,
        min_hand_detection_confidence: float,
        min_hand_presence_confidence: float, min_tracking_confidence: float):

        self.result = None
        # Visualization parameters
        self.row_size = 50  # pixels
        self.left_margin = 24  # pixels
        self.text_color = (0, 0, 0)  # black
        self.font_size = 1
        self.font_thickness = 1
        self.fps_avg_frame_count = 10

        # Label box parameters
        self.label_text_color = (255, 255, 255)  # white
        self.label_font_size = 1
        self.label_thickness = 2

        self.recognition_frame = None
        self.recognition_result_list = []

        def save_result(result: vision.GestureRecognizerResult,
                        unused_output_image: mp.Image, timestamp_ms: int):
            global FPS, COUNTER, START_TIME

            # Calculate the FPS
            if COUNTER % self.fps_avg_frame_count == 0:
                FPS = self.fps_avg_frame_count / (time.time() - START_TIME)
                START_TIME = time.time()

            self.recognition_result_list.append(result)
            COUNTER += 1

        # Initialize the gesture recognizer model
        base_options = python.BaseOptions(model_asset_path=model)
        options = vision.GestureRecognizerOptions(base_options=base_options,
                                                running_mode=vision.RunningMode.LIVE_STREAM,
                                                num_hands=num_hands,
                                                min_hand_detection_confidence=min_hand_detection_confidence,
                                                min_hand_presence_confidence=min_hand_presence_confidence,
                                                min_tracking_confidence=min_tracking_confidence,
                                                result_callback=save_result)
        self.recognizer = vision.GestureRecognizer.create_from_options(options)
    
    def detect_result(self):
        return self.result
    
    def start_recognize(self, img, draw = True):
        image = cv2.flip(img, 1)

        # Convert the image from BGR to RGB as required by the TFLite model.
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)

        # Run gesture recognizer using the model.
        self.recognizer.recognize_async(mp_image, time.time_ns() // 1_000_000)

        # Show the FPS
        fps_text = 'FPS = {:.1f}'.format(FPS)
        text_location = (self.left_margin, self.row_size)
        current_frame = image
        cv2.putText(current_frame, fps_text, text_location, cv2.FONT_HERSHEY_DUPLEX,
                    self.font_size, self.text_color, self.font_thickness, cv2.LINE_AA)
        
        if self.recognition_result_list:
            if len(self.recognition_result_list[0].hand_landmarks) != 0:
                self.result = self.recognition_result_list[0].gestures[0][0].category_name
            else:
                self.result = None
        
        if not draw:
            pass
        else: 
            if self.recognition_result_list:
                # Draw landmarks and write the text for each hand.
                for hand_index, hand_landmarks in enumerate(
                    self.recognition_result_list[0].hand_landmarks):
                    # Calculate the bounding box of the hand
                    x_min = min([landmark.x for landmark in hand_landmarks])
                    y_min = min([landmark.y for landmark in hand_landmarks])
                    y_max = max([landmark.y for landmark in hand_landmarks])

                    # Convert normalized coordinates to pixel values
                    frame_height, frame_width = current_frame.shape[:2]
                    x_min_px = int(x_min * frame_width)
                    y_min_px = int(y_min * frame_height)
                    y_max_px = int(y_max * frame_height)

                    # Get gesture classification results
                    if self.recognition_result_list[0].gestures:
                        gesture = self.recognition_result_list[0].gestures[hand_index]
                        category_name = gesture[0].category_name
                        score = round(gesture[0].score, 2)
                        result_text = f'{category_name} ({score})'

                        # Compute text size
                        text_size = \
                        cv2.getTextSize(result_text, cv2.FONT_HERSHEY_DUPLEX, self.label_font_size,
                                        self.label_thickness)[0]
                        text_width, text_height = text_size

                        # Calculate text position (above the hand)
                        text_x = x_min_px
                        text_y = y_min_px - 10  # Adjust this value as needed

                        # Make sure the text is within the frame boundaries
                    if text_y < 0:
                        text_y = y_max_px + text_height

                    # Draw the text
                    cv2.putText(current_frame, result_text, (text_x, text_y),
                                cv2.FONT_HERSHEY_DUPLEX, self.label_font_size,
                                self.label_text_color, self.label_thickness, cv2.LINE_AA)

                    # Draw hand landmarks on the frame
                    hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
                    hand_landmarks_proto.landmark.extend([
                    landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y,
                                                    z=landmark.z) for landmark in
                    hand_landmarks
                    ])
                    mp_drawing.draw_landmarks(
                    current_frame,
                    hand_landmarks_proto,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())

        self.recognition_frame = current_frame
        self.recognition_result_list.clear()
           
        if self.recognition_frame is not None and draw:
            cv2.imshow('gesture_recognition', self.recognition_frame)

        # Stop the program if the ESC key is pressed.
        if cv2.waitKey(1) == 27:
            return