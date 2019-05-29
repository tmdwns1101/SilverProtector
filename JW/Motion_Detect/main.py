from JW.Motion_Detect.motion_detect import MotionDetect
from JW.util.ReadDeviecID import deviceIDRead

import cv2
cam = cv2.VideoCapture(0)
cam.set(3, 1280)  # CV_CAP_PROP_FRAME_WIDTH
cam.set(4, 720)  # CV_CAP_PROP_FRAME_HEIGHT

def main():
    deviceID = deviceIDRead()
    detect = MotionDetect(cam,deviceID)
    detect.ObjectDetector()

if __name__ == "__main__":
    main()