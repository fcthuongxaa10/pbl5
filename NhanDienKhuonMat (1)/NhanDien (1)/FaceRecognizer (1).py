import random
import string

import pymysql
import pyrebase
import cv2
import numpy as np
from PIL import Image
import pickle
import sqlite3
import datetime
import time
import serial
import sys
import requests

# Khởi tạo bộ phát hiện khuôn mặt
faceDetect = cv2.CascadeClassifier('haarcascade_frontalface_default.xml');

# Khởi tạo bộ nhận diện khuôn mặt
# SerialPort = serial.Serial("com3", baudrate=9600, timeout=1)
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('recognizer/trainner.yml')

Dem = 0

id = 0
# set text style
fontface = cv2.FONT_HERSHEY_SIMPLEX
fontscale = 1
fontcolor = (0, 255, 0)
fontcolor1 = (0, 0, 255)


def Adruino(Check):
    SerialPort = serial.Serial("com3", baudrate=9600, timeout=1)
    try:
        # OutgoingData = input('> ')
        SerialPort.write(bytes(Check, 'utf-8'))
    except KeyboardInterrupt:
        print("Closing and exiting the program")
        SerialPort.close()
        sys.exit(0)


def Connect():
    connectionn = pymysql.connect(host='localhost',
                                  user='root',
                                  password='',
                                  db='bnl5',
                                  )
    return connectionn


# Hàm lấy thông tin người dùng qua ID
def getProfile(id):
    conn = Connect()
    cursor = conn.cursor()
    cursor.execute("select * from people")
    cursor.execute("SELECT * FROM people WHERE id_tv=" + str(id))
    profile = None
    for row in cursor:
        profile = row
    conn.close()
    return profile


def insertOrUpdate(name,Date, Time, Check, Link):
    conn = Connect()
    cursor = conn.cursor()
    cursor.execute("select * from infor_dn")
    print("ok chon info")
    cmd = "INSERT INTO infor_dn(name,day,time,ND,image) Values('"+name+"','" + T + "','" + Time + "'," + str(Check) + ",'" + Link + "')"
    print(cmd)
    cursor.execute(cmd)
    conn.commit()
    conn.close()


def random_with_N_digits():
    range_start = 10 ** (5 - 1)
    range_end = (10 ** 5) - 1
    return random.randint(range_start, range_end)


config = {
    "apiKey": "AIzaSyB7gJ-L5KI_wnKGa3d4awzMpQxdVuQOv3U",
    "authDomain": "pbl5-image.firebreaks.com",
    "databaseURL": "https://pbl5-image-default-rtdb.firebaseio.com",
    "projectId": "pbl5-image",
    "storageBucket": "pbl5-image.appspot.com",
    "serviceAccount": "ServiceAccount.json"
}

# Khởi tạo camera
cam = cv2.VideoCapture(0);

while (True):

    # Đọc ảnh từ camera
    ret, img = cam.read()

    # Lật ảnh cho đỡ bị ngược
    img = cv2.flip(img, 1)

    # Vẽ khung chữ nhật để định vị vùng người dùng đưa mặt vào
    centerH = img.shape[0] // 2;
    centerW = img.shape[1] // 2;
    sizeboxW = 300;
    sizeboxH = 400;
    cv2.rectangle(img, (centerW - sizeboxW // 2, centerH - sizeboxH // 2),
                  (centerW + sizeboxW // 2, centerH + sizeboxH // 2), (255, 255, 255), 5)

    # Chuyển ảnh về xám
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Phát hiện các khuôn mặt trong ảnh camera
    faces = faceDetect.detectMultiScale(gray, 1.3, 5);

    # Lặp qua các khuôn mặt nhận được để hiện thông tin
    for (x, y, w, h) in faces:
        # Vẽ hình chữ nhật quanh mặt
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Nhận diện khuôn mặt, trả ra 2 tham số id: mã nhân viên và dist (dộ sai khác)
        id, dist = recognizer.predict(gray[y:y + h, x:x + w])
        conn = Connect()
        cursor = conn.cursor()
        cursor.execute("select * from people")
        cursor.execute("SELECT * FROM people WHERE id_tv=" + str(id))
        for row in cursor:
            name = row[1]
            image = row[2]
        print(name)
        print(image)
        conn.commit()
        conn.close()

        profile = None
        today = datetime.datetime.now()
        T = today.strftime("%y-%m-%d")
        Time = today.strftime("%H:%M:%S")
        Check = 1
        # Nếu độ sai khác < 40 thì lấy profile
        if (dist <= 40):
            profile = getProfile(id)
            print(dist)
        # Hiển thị thông tin tên người hoặc Unknown nếu không tìm thấy
        if (profile != None):
            Check = 1
            #cv2.putText(img, "Name: " + str(profile["username"]), (x, y + h + 30), fontface, fontscale, fontcolor, 2)
            insertOrUpdate(name,T, Time, Check,image)
            Adruino(str(Check))
            time.sleep(10)
        else:
            Check = 0
            print(dist)
            ramdom = random_with_N_digits()
            Image = str(ramdom) + ".jpg"
            cv2.imwrite("Fails/" + Image, img)
            cv2.putText(img, "Name: Unknown", (x, y + h + 30), fontface, fontscale, fontcolor1, 2)
            print(ramdom)
            firebase = pyrebase.initialize_app(config)
            storage = firebase.storage()
            # Upload Image
            storage.child(Image).put("Fails/" + Image)
            # Get url of image
            link = "https://firebasestorage.googleapis.com/v0/b/pbl5-image.appspot.com/o/"
            token = '?alt=media&token=3d3816b2-156b-4fa9-a04d-c6e2ba9d81ef'
            url = link + Image + token
            insertOrUpdate("unknow",T, Time, Check, url)
            Adruino(str(Check))
            time.sleep(10)
    cv2.imshow('Face', img)
    # Nếu nhấn q thì thoát
    if cv2.waitKey(1) == ord('q'):
        break
cam.release()
cv2.destroyAllWindows()
