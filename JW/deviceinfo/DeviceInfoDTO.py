class DeviceInfoDTO:
    def __init__(self, deviceID, userID):
        self.deviceID = deviceID
        self.userID = userID


    def setDeviceID(self, deviceID):
        self.deviceID = deviceID
    def getDeviceID(self):
        return self.deviceID

    def setUserID(self, userID):
        self.userID = userID
    def getUserID(self):
        return self.userID