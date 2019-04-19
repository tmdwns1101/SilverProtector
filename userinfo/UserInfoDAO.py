import pymysql
from util.DataBaseConn import DBAccessMerial

class UserInfoDAO:
    name = "UserInfoDAO"

    def __init__(self):
        self

    def getUserInfo(self, userID):
        sql = "select * from userInfo where userID = %s"
        host, user, password, db = DBAccessMerial()
        conn = pymysql.connect(host=host, user=user, password=password, db=db, charset='utf8')
        try:
            curs = conn.cursor()
            curs.execute(sql, userID)

            row = curs.fetchone()
            print(row)
            return row[0], row[1], row[2], row[3], row[4], row[5], row[6]     #userID, userName, userPhone, userAddress, userMiss, userFallDown, nurseID


        except Exception as e:
            print(e)
        finally:
            try:
                if conn.open is True:
                    # Connection 닫기
                    conn.close()
            except Exception as e:
                print(e)

    def getNurseID(self, userID):
        sql = "select nurseID from userInfo where userID = %s"
        host, user, password, db = DBAccessMerial()
        conn = pymysql.connect(host=host, user=user, password=password, db=db, charset='utf8')
        try:
            curs = conn.cursor()
            curs.execute(sql, userID)

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



    def getUserFallDown(self, userID):
        sql = "select userFallDown from userInfo where userID = %s"
        host, user, password, db = DBAccessMerial()
        conn = pymysql.connect(host=host, user=user, password=password, db=db, charset='utf8')
        try:
            curs = conn.cursor()
            curs.execute(sql, userID)

            row = curs.fetchone()
            print(row[0])
            return row[0]

        except Exception as e:
            print(e)
        finally:
            try:
                if conn.open is True:
                    conn.close()
            except Exception as e:
                    print(e)

    def getUserMiss(self, userID):
        sql = "select userMiss from userInfo where userID = %s"
        host, user, password, db = DBAccessMerial()
        conn = pymysql.connect(host=host, user=user, password=password, db=db, charset='utf8')
        try:
            curs = conn.cursor()
            curs.execute(sql, userID)

            row = curs.fetchone()
            print(row[0])
            return row[0]

        except Exception as e:
            print(e)
        finally:
            try:
                if conn.open is True:
                    conn.close()
            except Exception as e:
                print(e)

    def UpdateUserFallDown(self, userID, state):
        sql = "update userInfo set userFallDown = %s where userID = %s"
        host, user, password, db = DBAccessMerial()
        conn = pymysql.connect(host=host, user=user, password=password, db=db, charset='utf8')
        try:
            curs = conn.cursor()
            curs.execute(sql, (state, userID))
            conn.commit()
            #print("updateFallDown")

        except Exception as e:
            print(e)
            print("DB 오류")
        finally:
            try:
                if conn.open is True:
                    conn.close()
            except Exception as e:
                print(e)

    def UpdateUserMiss(self, userID, state):
        sql = "update userInfo set userMiss = %s where userID = %s"
        host, user, password, db = DBAccessMerial()
        conn = pymysql.connect(host=host, user=user, password=password, db=db, charset='utf8')
        #print("userID : ", userID)
        #print("state : ", state)
        try:
            curs = conn.cursor()
            curs.execute(sql, (state, userID))
            conn.commit()
            #print("updateUserMiss")

        except Exception as e:
            print(e)
            print("DB 오류")
            return -1
        finally:
            try:
                if conn.open is True:
                    conn.close()
            except Exception as e:
                    print(e)



