import cv2
import threading
import numpy as np
import time
from imutils.video import VideoStream
import argparse
import datetime
import imutils

class MotionDetect:
    fallDownCheck = False
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video", help="path to the video file")
    ap.add_argument("-a", "--min-area", type=int, default=1000, help="minimum area size")  # defualt= 500
    args = vars(ap.parse_args())
    noObjectFlag = False

    def __init__(self, cam):
        self.ret, self.frame = cam.read()

    def Timer(self, limit):
        start = time.time()
        while True:
            end = time.time()
            if end - start >= limit:
                print("Warning!")
                self.fallDownCheck = False
                break

    def ObjectDetector(self):
        # if the video argument is None, then we are reading from webcam

        if self.args.get("video", None) is None:
            vs = VideoStream(src=0).start()
            time.sleep(2.0)

        # otherwise, we are reading from a video file
        else:
            vs = cv2.VideoCapture(self.args["video"])

        # initialize the first frame in the video stream
        firstFrame = None

        # loop over the frames of the video
        while True:
            print(self.fallDownCheck)

            # grab the current frame and initialize the occupied/unoccupied
            # text
            frame = vs.read()
            frame = frame if self.args.get("video", None) is None else frame[1]
            text = "Unoccupied"

            if self.noObjectFlag is False:
                start = time.time()
                self.noObjectFlag = True
            end = time.time()

            if end - start >= 10 and self.noObjectFlag is True:
                print("Object MiSS!!!")
                time.sleep(1) #업데이트 되기전 접근 방지를 위해  n초(1~10) 정도 프로그램(영상)을 멈춤
                #데이터베이스 접근 후 userMiss 가 False이면 update(스레드로 동작)
                #아니면(update가 되었으면) 그냥 continue

            # if the frame could not be grabbed, then we have reached the end
            # of the video
            if frame is None:
                break

            # resize the frame, convert it to grayscale, and blur it
            frame = imutils.resize(frame, width=500)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            # if the first frame is None, initialize it
            if firstFrame is None:
                firstFrame = gray
                continue

            # compute the absolute difference between the current frame and
            # first frame
            frameDelta = cv2.absdiff(firstFrame, gray)
            thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

            # dilate the thresholded image to fill in holes, then find contours
            # on thresholded image
            thresh = cv2.dilate(thresh, None, iterations=2)
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)

            # loop over the contours
            if cnts:
                areas = []
                for c in cnts:
                    ar = cv2.contourArea(c)
                    areas.append(ar)

                max_area = max(areas or [0])
                max_area_index = areas.index(max_area)
                maxCnt = cnts[max_area_index]
                # if the contour is too small, ignore it
                if max_area < self.args["min_area"]:
                    continue

                # compute the bounding box for the contour, draw it on the frame,
                # and update the text
                (x, y, w, h) = cv2.boundingRect(c)
                #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                self.noObjectFlag = False

                text = "Occupied"
                # test1
                if h > 1.3 * w:
                    str = "standing"
                else:
                    if w > 1.3 * h:
                        str = "laying"

                        if self.fallDownCheck is False:
                            self.fallDownCheck = True
                            mythread = threading.Thread(target=self.Timer, args=(5, ))
                            mythread.daemon = True
                            mythread.start()
                    else:
                        if w:
                            str = "sitting"
                        else:
                            str = "nobody"
                if str is "standing":
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                if str is "sitting":
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                if str is "laying":
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                cv2.putText(frame, str, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            # draw the text and timestamp on the frame
            cv2.putText(frame, "Room Status: {}".format(text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
            # show the frame and record if the user presses a key
            cv2.imshow("Security Feed", frame)
            cv2.imshow("Thresh", thresh)
            cv2.imshow("Frame Delta", frameDelta)
            key = cv2.waitKey(1) & 0xFF
            # if the `q` key is pressed, break from the lop
            if key == ord("q"):
                break

        # cleanup the camera and close any open windows
        vs.stop() if self.args.get("video", None) is None else vs.release()
        cv2.destroyAllWindows
