def SerialRead(self):
    f = open("test.txt", 'r')
    SerialNumber = f.readline()
    print(SerialNumber)
    f.close()