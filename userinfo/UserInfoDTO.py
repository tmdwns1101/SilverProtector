class UserInfoDTO:
    def __init__(self, userID, userName, userPhone, userAddress, nurseID):
        self.userID = userID
        self.userName = userName
        self.userPhone = userPhone
        self.userAddress = userAddress
        self.userMiss = False
        self.userFallDown = False
        self.nurseID = nurseID

    def setUserID(self, userID):
        self.userID = userID
    def getUserID(self):
        return self.userID

    def setUserName(self, userName):
        self.userName = userName
    def getUserName(self):
        return self.userName

    def setUserPhone(self, userPhone):
        self.userPhone = userPhone
    def getUserPhone(self):
        return self.userPhone

    def setUserAddress(self, userAddress):
        self.userAddress = userAddress
    def getuserAddress(self):
        return self.userAddress

    def setUserMiss(self, UserMiss):
        self.UserMiss = UserMiss
    def getUserMiss(self):
        return self.UserMiss

    def setUserFallDown(self, userFallDown):
        self.userFallDown = userFallDown
    def getUserFallDown(self):
        return self.userFallDown

    def setNurseID(self, nurseID):
        self.nurseID = nurseID
    def getUserAddress(self):
        return self.nurseID