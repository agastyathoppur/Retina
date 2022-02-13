# import the necessary packages
from scipy.spatial import distance
from imutils.video import FileVideoStream
from imutils.video import VideoStream
from imutils import face_utils
import pymongo
import numpy as np
import argparse
import imutils
import time
from datetime import datetime
from datetime import date
import dlib
import cv2
import math
import sys
import logging
import os
import screen_brightness_control as sbc


resttime = 10

cur_dir = os.getcwd()
print(cur_dir)


dirpath = os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(dirpath, 'testlog.log')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

filehandler = logging.FileHandler(filename)
filehandler.setLevel(logging.INFO)
filehandler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(filehandler)


def log_resttime(resttime):
    with open('testlog.log', 'w'):
        pass
    logger.info(resttime)


now = datetime.now()
start = now.strftime("%H:%M:%S")


class Blink:
    def __init__(self, startTime, duration):
        self.startTime = startTime
        self.duration = duration


STARTING_TIME = datetime.now()
TOTAL_RUNNING_TIME = 180
CURRENT_RUNNING_TIME = TOTAL_RUNNING_TIME
STATE = "RUNNING"
TOTAL_BLINKS = 0
EYE_AR_THRESH = 0.28
EYE_AR_CONSEC_FRAMES = 2
COUNTER = 0
ASPECT_RATIO_VECTOR = []


def getPauseDuration(pause):
    global CURRENT_RUNNING_TIME
    duration = getDuration(pause, datetime.now())
    if (duration > 60):
        return True
    CURRENT_RUNNING_TIME += duration
    print("paused for ", duration)
    return False


def getDuration(date1, date2):
    timeDelta = date2 - date1
    totalSeconds = timeDelta.total_seconds()
    return totalSeconds


def eyeAspectRatio(eye):
    # Representation of Human eye
    '''
        p2    p3
    p1            p4 
        p6    p5
    '''
    # Each eye is represented by an array of above 6 points (p1 -> p6) in clockwise direction
    # Eye Aspect Ratio = (||p2 - p6|| + ||p3 - p5|| )/ 2 * ||p4 - p1||

    # Euclidean distances between vertical eye landmarks
    d1 = distance.euclidean(eye[1], eye[5])
    d2 = distance.euclidean(eye[2], eye[4])

    # Euclidean distance between horizontal eye landmarks
    d3 = distance.euclidean(eye[0], eye[3])

    eye_aspect_ratio = (d1 + d2) / (2.0 * d3)
    return eye_aspect_ratio


# initialize dlib's face detector (HOG-based) and then create the facial landmark predictor

# path=str(sys.argv[1])
# print(path)
print("INFO: loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(
    "Desktop/Retina/shape_predictor_68_face_landmarks.dat")

# get indexes of the facial landmarks for the left and right eye
(leftEyeStart, leftEyeEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rightEyeStart, rightEyeEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

# start the video stream thread
log_resttime(resttime)
print("INFO: starting video stream thread...")
vs = VideoStream(0).start()
fileStream = False
time.sleep(1.0)

while True:
    if (getDuration(STARTING_TIME, datetime.now()) >= CURRENT_RUNNING_TIME):
        break
    # Read the frame, resize it and convert to grayscale
    frame = vs.read()
    frame = imutils.resize(frame, width=450)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # detect faces in the grayscale frame
    faces = detector(gray, 0)

    if (len(faces) != 1):
        if (STATE != "PAUSED"):
            STATE = "PAUSED"
            print("WARNING: face count is not equal to 1. pausing frames... ")
            PAUSE_START_TIME = datetime.now()
    else:
        if (STATE == "PAUSED" and getPauseDuration(PAUSE_START_TIME)):
            break
        STATE = "RUNNING"
        face = faces[0]
        shape = predictor(gray, face)
        shape = face_utils.shape_to_np(shape)

        # extracting the left and right eye from the facial landmarks
        leftEye = shape[leftEyeStart: leftEyeEnd]
        rightEye = shape[rightEyeStart: rightEyeEnd]

        # calculating aspect ratios for both eyes
        leftEAR = eyeAspectRatio(leftEye)
        rightEAR = eyeAspectRatio(rightEye)

        # average the eye aspect ratio together for both eyes
        ear = (leftEAR + rightEAR) / 2.0

        ASPECT_RATIO_VECTOR.append(ear)

        if (len(ASPECT_RATIO_VECTOR) >= 60):
            ASPECT_RATIO_VECTOR.pop(0)

        EYE_AR_THRESH = sum(ASPECT_RATIO_VECTOR) / len(ASPECT_RATIO_VECTOR) - 0.06

        if ear < EYE_AR_THRESH:
            COUNTER += 1
        else:
            if COUNTER >= EYE_AR_CONSEC_FRAMES:
                TOTAL_BLINKS += 1
            COUNTER = 0

        cv2.putText(frame, "Blinks: {}".format(TOTAL_BLINKS),
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, "EAR: {:.2f}".format(
            ear), (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # show the frame
    #cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

BLINK_RATE = TOTAL_BLINKS*60/TOTAL_RUNNING_TIME
MIN_RATE = 2
MAX_RATE = 35
NORMAL_RATE_MIN = 12
NORMAL_RATE_MAX = 15
DRYNESS = 1 - (BLINK_RATE - MIN_RATE)/(MAX_RATE - MIN_RATE)

if BLINK_RATE <= NORMAL_RATE_MIN - 5:
	curr_brightness=sbc.get_brightness()
	new_brightness=int(curr_brightness*4/5)
	sbc.set_brightness(new_brightness)
	os.system('notify-send --urgency=LOW "Please Blink! (Brightness reduced by 20%)" -i ~/Desktop/Retina/eye_icon.ico')
    
client = pymongo.MongoClient()
mydb = client["BlinksDatabase"]
mycol = mydb["Blinkstats"]
mydict = {"Time": start, "Date": str(
    date.today()), "BlinkRate": round(BLINK_RATE), "DrynessLevel": round(DRYNESS,2)}
mycol.insert_one(mydict)
cv2.destroyAllWindows()
vs.stop()
