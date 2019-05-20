import cv2
import threading
import numpy as np
import time
from imutils.video import VideoStream
import argparse
import datetime
import imutils
from JW.deviceinfo.DeviceInfoDAO import *
from JW.userinfo.UserInfoDAO import *
from JW.userOuting.UserOutingDAO import *

class MotionDetect:

    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video", help="path to the video file")
    ap.add_argument("-a", "--min-area", type=int, default=2000, help="minimum area size")  # defualt= 500
    args = vars(ap.parse_args())
    noObjectFlag = False
    fallDownCheck = False
    outingFlag = False

    def __init__(self, cam, deviceID):
        self.ret, self.frame = cam.read()
        self.deviceID = deviceID
        self.deviceDAO = DeviceInfoDAO()
        self.userID = self.deviceDAO.getUserID(self.deviceID)
        self.userDAO = UserInfoDAO()

    def Timer(self, limit):
        start = time.time()
        while True:
            end = time.time()
            if end - start >= limit:
                print("Warning!")
                self.fallDownCheck = False
                self.userDAO.UpdateUserFallDown(userID=self.userID, state=1)

                break

    def ObjectDetector(self):
        # if the video argument is None, then we are reading from webcam

        if self.args.get("video", None) is None:
            vs = VideoStream(src=0).start()
            time.sleep(2.0)

            # 0503 Moving Average Background Subtraction
            frame = vs.read()
            avg1 = np.float32(frame)

        # otherwise, we are reading from a video file
        else:
            vs = cv2.VideoCapture(self.args["video"])
            # 0503 Moving Average Background Subtraction
            frame = vs.read()
            avg1 = np.float32(frame)

        # initialize the first frame in the video stream
        firstFrame = None
        print(self.userID)

        ang1 = -100

        # loop over the frames of the video
        while True:
            #print(self.fallDownCheck)


            # grab the current frame and initialize the occupied/unoccupied
            # text
            frame = vs.read()
            frame = frame if self.args.get("video", None) is None else frame[1]
            text = "Unoccupied"

            # 0503 Moving Average Background Subtraction
            cv2.accumulateWeighted(frame, avg1, 0.1)
            res1 = cv2.convertScaleAbs(avg1)

            if self.noObjectFlag is False:
                start = time.time()
                self.noObjectFlag = True
            end = time.time()

            if end - start >= 10 and self.noObjectFlag is True:
                print("Object MiSS!!!")
                self.userDAO.UpdateUserMiss(userID=self.userID, state=1)

            # Change 2019/05/15 for 외출 시간 전송
            if self.outingFlag is False:
                outingStart = time.time()
                self.outingFlag = True
            outingEnd = time.time()

            if outingEnd - outingStart >= 600 and self.outingFlag is True:
                UserOutingDAO().insertDate(userID=self.userID)

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
            # thresh changed 25 -> 75 because of light dilation
            frameDelta = cv2.absdiff(firstFrame, gray)
            thresh = cv2.threshold(frameDelta, 75, 255, cv2.THRESH_BINARY)[1]

            # dilate the thresholded image to fill in holes, then find contours
            # on thresholded image
            thresh = cv2.dilate(thresh, None, iterations=2)
            #cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)
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

                #Rotated Rectangle
                rect = cv2.minAreaRect(c)
                ((x1, y1), (x2, y2), ang) = cv2.minAreaRect(c)
                box = cv2.boxPoints(rect)
                box = box.astype('int')
                cv2.drawContours(frame, [box], -1, 7)  # blue

                if self.noObjectFlag is True:
                    self.userDAO.UpdateUserMiss(userID=self.userID, state=0)

                self.noObjectFlag = False
                self.outingFlag = False # 외출상태 초기화

                text = "Occupied"

                # user status : sitting / standing / laying
                if h > 1.3 * w:
                    str = "standing"
                    ang1 = int(float(ang))
                    time.sleep(0.5)
                    self.userDAO.UpdateUserFallDown(userID=self.userID, state=0)
                    self.fallDownCheck = False
                else:
                    if w > 1.3 * h:
                        str = "laying"

                        ang2 = int(float(ang))
                        sub_ang = ang1 - ang2
                        print(self.fallDownCheck," ",ang2, ang1, sub_ang)

                        if self.fallDownCheck is False and sub_ang > 20:
                            self.fallDownCheck = True
                            fallstart = time.time()
                            print("falldown check start",sub_ang)

                        if self.fallDownCheck is True:
                            fallend = time.time()
                            if fallend - fallstart >= 5:
                                print("Warning!")
                                self.fallDownCheck = False
                                self.userDAO.UpdateUserFallDown(userID=self.userID, state=1)

                    else:
                        if w:
                            self.userDAO.UpdateUserFallDown(userID=self.userID, state=0)
                            self.fallDownCheck = False
                            str = "sitting"
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
            # 0503 Moving Average Background Subtraction
            cv2.imshow('avg1', res1)

            key = cv2.waitKey(1) & 0xFF
            # if the `q` key is pressed, break from the lop
            if key == ord("q"):
                break

        # cleanup the camera and close any open windows
        vs.stop() if self.args.get("video", None) is None else vs.release()
        cv2.destroyAllWindows