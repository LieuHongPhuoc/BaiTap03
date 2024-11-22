import mysql.connector

def ket_noi():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="p123",
            database="quan_ly_sach"
        )
        return conn
    except mysql.connector.Error as err:
        print("Lỗi kết nối: ", err)
        return None
