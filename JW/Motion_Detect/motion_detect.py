import cv2
import numpy as np
import time
from imutils.video import VideoStream
import argparse
import datetime
import imutils
import serial

from JW.deviceinfo.DeviceInfoDAO import *
from JW.userinfo.UserInfoDAO import *
from JW.userOuting.UserOutingDAO import *

class MotionDetect:

    ser = serial.Serial(port="COM12", baudrate=9600)

    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video", help="path to the video file")
    ap.add_argument("-a", "--min-area", type=int, default=10000, help="minimum area size")  # defualt= 500
    args = vars(ap.parse_args())

    def __init__(self, cam, deviceID):
        self.ret, self.frame = cam.read()
        # data for mySQL
        self.deviceID = deviceID
        self.deviceDAO = DeviceInfoDAO()
        self.userID = self.deviceDAO.getUserID(self.deviceID)
        self.userDAO = UserInfoDAO()

    def ObjectDetector(self):
        # if the video argument is None, then we are reading from webcam
        if self.args.get("video", None) is None:
            vs = VideoStream(src=0).start()
            time.sleep(2.0)

        # otherwise, we are reading from a video file
        else:
            vs = cv2.VideoCapture(self.args["video"])
            frame = vs.read()
            avg1 = np.float32(frame)

        # initialize the first frame in the video stream
        firstFrame = None
        print(self.userID)

        # initialize count, state and flag values
        standCount = 0
        sittingCount = 0
        curState = "No"
        self.noObjectFlag = False
        self.fallDownCheck = False
        missFlag = False
        self.outingFlag = False  # if user is not in home
        self.indoorFlag = True  # if user is in home
        self.outingCurState = False  # current user state
        self.outingPreState = False  # last user state

        # loop over the frames of the video
        while True:
            # grab the current frame and initialize the occupied/unoccupied text
            frame = vs.read()
            frame = frame if self.args.get("video", None) is None else frame[1]
            text = "Unoccupied"

            # if user is not at home, save start time and make noObjectFlag true
            if self.noObjectFlag is False:
                start = time.time()
                self.noObjectFlag = True
            # set end time to current time
            end = time.time()

            # if difference between end and start is larger than 8 hours
            # and noObjectFlag is True update mySQL UserMiss
            if end - start >= 3600*8 and self.noObjectFlag is True:
                print("Object MiSS!!!")
                if self.missFlag is False:
                    self.userDAO.UpdateUserMiss(userID=self.userID, state=1)
                    self.missFlag = True

            # if user is missing for 10 minutes and outingFlag is True
            # and indoorFlag is Ture update mySQL insertDate
            if end - start >= 10 and self.noObjectFlag is True:  # default 600
                if self.indoorFlag is True:
                    UserOutingDAO().insertDate(userID=self.userID)
                    self.userDAO.UpdateUserOut(userID=self.userID, state=1)
                    self.ser.write("off".encode())
                    self.indoorFlag = False

            # if the frame could not be grabbed, then we have reached the end
            # of the video
            if frame is None:
                break

            # resize the frame, convert it to grayscale, and blur it
            # for light smear problem, use histogram equalization
            frame = imutils.resize(frame, width=500)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            gray = cv2.equalizeHist(gray)

            # if the first frame is None, initialize it
            if firstFrame is None:
                firstFrame = gray
                continue

            # compute the absolute difference between the current frame and
            # first frame
            frameDelta = cv2.absdiff(firstFrame, gray)
            thresh = cv2.threshold(frameDelta, 60, 255, cv2.THRESH_BINARY)[1]

            # dilate the thresholded image to fill in holes, then find contours
            # on thresholded image
            thresh = cv2.dilate(thresh, None, iterations=4)
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)
            cnts = imutils.grab_contours(cnts)

            maxValue = 0
            maxIdx = 0
            # loop over the contours
            # find max area value in contours
            if cnts:
                areas = []
                for i in range(0, len(cnts)):
                    c = cnts[i]
                    ar = cv2.contourArea(c)
                    if maxValue < ar:
                        maxValue = ar
                        maxIdx = i
                areas.append(ar)
                max_area = max(areas or [0])

                # if the contour is too small, ignore it
                if max_area > self.args["min_area"]:

                    # compute the bounding box for the contour, draw it on the frame,
                    (x, y, w, h) = cv2.boundingRect(cnts[maxIdx])

                    # contours is capturing something, update text and state
                    # reset noObject, outing, indoor flag and str
                    text = "Occupied"
                    preState = curState
                    print("current state :")
                    print(preState)
                    str = "null"
                    self.noObjectFlag = False
                    self.outingFlag = False
                    self.indoorFlag = True

                    # user status : sitting / standing / Fall down / sleep
                    # accumulate stand count and if stand count is more than
                    # 100, update current state
                    # reset fallDownCheck and mySQL UserFallDown
                    if h > 1.3 * w:
                        str = "standing"
                        standCount += 1
                        sittingCount = 0
                        print("Stand Count :", standCount)
                        if standCount >= 100:
                            curState = "standing"
                        self.userDAO.UpdateUserFallDown(userID=self.userID, state=0)
                        self.fallDownCheck = False

                    # if wide is longer than height and preState is standing
                    elif w > 1.3 * h:
                        if preState != "No" and preState == "standing":
                            str = "Fall Down"

                        # measure time and if user is laying more than 5 sec
                        # update fallDownCheck and mySQl UserFalldown
                        if self.fallDownCheck is False:
                            self.fallDownCheck = True
                            fallstart = time.time()
                        if self.fallDownCheck is True:
                            fallend = time.time()
                            if fallend - fallstart >= 5:
                                print("Warning!")
                                self.fallDownCheck = False
                                self.userDAO.UpdateUserFallDown(userID=self.userID, state=1)

                        # if wide is longer than height and preState is sitting
                        # set str sleep
                        elif preState == "sitting":
                            str = "sleep"

                    # if wide and height are similar
                    # reset fallDownCheck and mySQL UserFallDown
                    elif h <= 1.3 * w and w <= 1.3 * h:
                        self.userDAO.UpdateUserFallDown(userID=self.userID, state=0)
                        self.fallDownCheck = False
                        str = "sitting"

                        # accumulate stand count and if sitting count is more than
                        # 100, update current state
                        standCount = 0
                        sittingCount += 1
                        if sittingCount >= 100:
                            curState = "sitting"
                        print("Sitting Count :", sittingCount)

                    # make frame for different color and put text str
                    if str is "standing":
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    if str is "sitting":
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    if str is "Fall Down":
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    if str is "sleep":
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 0), 2)
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
                self.ser.close()
                break

        # cleanup the camera and close any open windows
        vs.stop() if self.args.get("video", None) is None else vs.release()
        cv2.destroyAllWindows