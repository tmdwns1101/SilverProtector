def deviceIDRead():
    f = open("../DeviceID.txt", 'r')
    deviceID = f.readline()
    print(deviceID)
    f.close()
    return deviceID

