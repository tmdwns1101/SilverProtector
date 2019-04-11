
from FallDownDetect.MotionDetect import MotionDetect
import cv2
cam = cv2.VideoCapture(0)
cam.set(3, 1280)  # CV_CAP_PROP_FRAME_WIDTH
cam.set(4, 720)  # CV_CAP_PROP_FRAME_HEIGHT
# cam.set(5,0) #CV_CAP_PROP_FPS
def main():
    #OpenCam()
    #time.sleep(3)
    #NullCamera()
    #MotionDetect(fallDownChecker)

    detect = MotionDetect(cam)
    detect.ObjectDetector()




if __name__ == "__main__":
    main()