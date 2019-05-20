import pymysql
from JW.util.DataBaseConn import DBAccessMerial
from datetime import datetime

class UserOutingDAO():
    name = "UserOutingDAO"

    def __init__(self):
        self

    def insertDate(self, userID):
        sql = "insert into userouting values(%s, %s, %s, %s, %s)"
        host, user, password, db = DBAccessMerial()
        conn = pymysql.connect(host=host, user=user, password=password, db=db, charset='utf8')
        now = datetime.now()
        year = now.year
        month = now.month
        day = now.day
        hour = now.hour
        min = now.minute
        sec = now.second

        time = str(hour) + '-' + str(min) +'-' + str(sec)

        try:
            curs = conn.cursor()
            curs.execute(sql, (userID, year, month, day, time))
            conn.commit()


        except Exception as e:
            print(e)
        finally:
            try:
                if conn.open is True:
                    # Connection 닫기
                    conn.close()
            except Exception as e:
                print(e)