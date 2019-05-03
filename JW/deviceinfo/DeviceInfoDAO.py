import pymysql
from JW.util.DataBaseConn import DBAccessMerial

class DeviceInfoDAO:
    name = "DeviceInfoDAO"

    def __init__(self):
        self

    def getUserID(self, deviceID):
        sql = "select userID from deviceInfo where deviceID = %s"
        host, user, password, db = DBAccessMerial()
        conn = pymysql.connect(host=host, user=user, password=password, db=db, charset='utf8')
        print("deviceID : ", deviceID)
        try:
            curs = conn.cursor()
            curs.execute(sql, deviceID)

            row = curs.fetchone()
            print(row)
            return row[0]


        except Exception as e:
            print(e)
        finally:
            try:
                if conn.open is True:
                    conn.close()
            except Exception as e:
                print(e)