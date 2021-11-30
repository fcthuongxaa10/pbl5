import cv2
import sqlite3
import os
import pymysql
import pyrebase

detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
cam = cv2.VideoCapture(0)
# Đọc ảnh từ camera
ret, img = cam.read()

connectionn = pymysql.connect(host='localhost',
                              user='root',
                              password='',
                              db='bnl5',
                              charset='utf8mb4',
                              cursorclass=pymysql.cursors.DictCursor)

config = {
    "apiKey": "AIzaSyB7gJ-L5KI_wnKGa3d4awzMpQxdVuQOv3U",
    "authDomain": "pbl5-image.firebreaks.com",
    "databaseURL": "https://pbl5-image-default-rtdb.firebaseio.com",
    "projectId": "pbl5-image",
    "storageBucket": "pbl5-image.appspot.com",
    "serviceAccount": "ServiceAccount.json"
}


# Hàm cập nhật tên và ID vào CSDL
def insertOrUpdate(id, name, url):
    conn = connectionn
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM people WHERE id_tv=' + str(id))
    isRecordExist = 0
    for row in cursor:
        isRecordExist = 1

    if isRecordExist == 0:
        cmd = "INSERT INTO people(id_tv,name,image) Values(" + str(id) + ",' " + str(name) + "','" + str(url) + "')"
        print(cmd)
    else:
        cmd = "UPDATE people SET name=' " + str(name) + "', Image='" + str(url) + "'  WHERE id_tv=" + str(id)
        print(cmd)
    cursor.execute(cmd)
    conn.commit()
    conn.close()


id = input('Nhập mã nhân viên:')
name = input('Nhập tên nhân viên:')
print("Bắt đầu chụp ảnh tạo ảnh hồ sơ")
user = "User" + str(id) + ".jpg"
cv2.imwrite("User/" + user, img)
print("Bắt đầu chụp ảnh nhân viên, nhấn q để thoát!")
firebase = pyrebase.initialize_app(config)
storage = firebase.storage()
# Upload Image
storage.child(user).put("User/" + user)
# Get url of image
link = "https://firebasestorage.googleapis.com/v0/b/pbl5-image.appspot.com/o/"
token = '?alt=media&token=3d3816b2-156b-4fa9-a04d-c6e2ba9d81ef'
url = link + user + token

insertOrUpdate(id, name, url)

sampleNum = 0

while True:
    ret, img = cam.read()
    # Lật ảnh cho đỡ bị ngược
    img = cv2.flip(img, 1)
    # Kẻ khung giữa màn hình để người dùng đưa mặt vào khu vực này
    centerH = img.shape[0] // 2
    centerW = img.shape[1] // 2
    sizeboxW = 300
    sizeboxH = 400
    cv2.rectangle(img, (centerW - sizeboxW // 2, centerH - sizeboxH // 2),
                  (centerW + sizeboxW // 2, centerH + sizeboxH // 2), (255, 255, 255), 5)
    # Đưa ảnh về ảnh xám
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Nhận diện khuôn mặt
    faces = detector.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        # Vẽ hình chữ nhật quanh mặt nhận được
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        # Ghi dữ liệu khuôn mặt vào thư mục dataSet
        if not os.path.exists('dataSet'):
            os.makedirs('dataSet')

        sampleNum += 1

        cv2.imwrite("dataSet/User." + str(id) + '.' + str(sampleNum) + ".jpg", gray[y:y + h, x:x + w])

    cv2.imshow('frame', img)
    # Check xem có bấm q hoặc trên 100 ảnh sample thì thoát
    cv2.waitKey(1)
    if cv2.waitKey(200) & 0xFF == ord('q'):
        break
    elif sampleNum > 200:
        break

cam.release()
cv2.destroyAllWindows()
