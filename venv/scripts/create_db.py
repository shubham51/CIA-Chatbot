import pymysql
import base64
database_name = "dtu_bot"
char_set = "utf8mb4"
cusror_type = pymysql.cursors.DictCursor

connectionInstance = pymysql.connect(
    host='localhost',
    user='root',
    password='password',
    charset=char_set,
    cursorclass=cusror_type
)
try:
    cursorInstance = connectionInstance.cursor()
    sqlStatement= "CREATE DATABASE "+ database_name
    cursorInstance.execute(sqlStatement)
except Exception as e:
    print("Exeception occured:{}".format(e))

connectionInstance = pymysql.connect(
    host='localhost',
    user='root',
    password='password',
    db='dtu_bot',
)
try:
    cursorInstance = connectionInstance.cursor()
    sqlStatement = "CREATE TABLE users (username VARCHAR(32) PRIMARY KEY, password VARCHAR(255))"
    cursorInstance.execute(sqlStatement)
except Exception as e:
    print("Exeception occured:{}".format(e))

try:
    cursorInstance = connectionInstance.cursor()
    sqlStatement = "CREATE TABLE logs (id INT AUTO_INCREMENT PRIMARY KEY, conversation VARCHAR(10000),username VARCHAR(32) NOT NULL , FOREIGN KEY(username) REFERENCES users(username))"
    cursorInstance.execute(sqlStatement)
except Exception as e:
    print("Exeception occured:{}".format(e))

username = "2k15/IT/085"
password = "2019"

with connectionInstance.cursor() as cursor:
    sql = "INSERT INTO users (`username`, `password`) VALUES (%s, %s)"
    try:
        cursor.execute(sql, (username, base64.b64encode(password)))
    except Exception as e:
        print("Exeception occured:{}".format(e))
connectionInstance.commit()

connectionInstance.close()
