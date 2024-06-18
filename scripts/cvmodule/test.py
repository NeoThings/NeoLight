
import cv2
import sys
import argparse
from face_landmarker import FaceLandmarker
from hand_gesture_recognize import HandGesture

parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    '--faceLandmarkerModel',
    help='Name of face landmarker model.',
    required=False,
    default='face_landmarker.task')
parser.add_argument(
    '--numFaces',
    help='Max number of faces that can be detected by the landmarker.',
    required=False,
    default=1)
parser.add_argument(
    '--minFaceDetectionConfidence',
    help='The minimum confidence score for face detection to be considered '
            'successful.',
    required=False,
    default=0.5)
parser.add_argument(
    '--minFacePresenceConfidence',
    help='The minimum confidence score of face presence score in the face '
            'landmark detection.',
    required=False,
    default=0.5)
parser.add_argument(
    '--minFaceTrackingConfidence',
    help='The minimum confidence score for the face tracking to be '
            'considered successful.',
    required=False,
    default=0.5)

parser.add_argument(
    '--handGestureModel',
    help='Name of gesture recognition model.',
    required=False,
    default='gesture_recognizer.task')
parser.add_argument(
    '--numHands',
    help='Max number of hands that can be detected by the recognizer.',
    required=False,
    default=1)
parser.add_argument(
    '--minHandDetectionConfidence',
    help='The minimum confidence score for hand detection to be considered '
        'successful.',
    required=False,
    default=0.5)
parser.add_argument(
    '--minHandPresenceConfidence',
    help='The minimum confidence score of hand presence score in the hand '
        'landmark detection.',
    required=False,
    default=0.5)
parser.add_argument(
    '--minHandTrackingConfidence',
    help='The minimum confidence score for the hand tracking to be '
        'considered successful.',
    required=False,
    default=0.5)

parser.add_argument(
    '--cameraId', help='Id of camera.', required=False, default=0)
parser.add_argument(
    '--frameWidth',
    help='Width of frame to capture from camera.',
    required=False,
    default=1280)
parser.add_argument(
    '--frameHeight',
    help='Height of frame to capture from camera.',
    required=False,
    default=960)
args = parser.parse_args()
parser.add_argument(
    '--frameFrequency',
    help='Frequency of frame to capture from camera.',
    required=False,
    default=10)
args = parser.parse_args()

detect_face = FaceLandmarker(args.faceLandmarkerModel, int(args.numFaces), args.minFaceDetectionConfidence,
        args.minFacePresenceConfidence, args.minFaceTrackingConfidence)

detect_hand = HandGesture(args.handGestureModel, int(args.numHands), args.minHandDetectionConfidence,
      args.minHandPresenceConfidence, args.minHandTrackingConfidence)

cap = cv2.VideoCapture(int(args.cameraId))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.frameWidth)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.frameHeight)
cap.set(cv2.CAP_PROP_FPS, args.frameFrequency)

# while cap.isOpened():
#     success, image = cap.read()
#     if not success:
#         sys.exit(
#             'ERROR: Unable to read from webcam. Please verify your webcam settings.'
#         )
#     detect_face.start_detect(image, False)
#     print(detect_face.detect_result())

while cap.isOpened():
    success, image = cap.read()
    if not success:
        sys.exit(
            'ERROR: Unable to read from webcam. Please verify your webcam settings.'
        )
    detect_hand.start_recognize(image, False)
    print(detect_hand.detect_result())