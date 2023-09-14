# install opencv_python,
# install numpy,
# install face_recognition,
# install python-csv,
# install DateTime
import cv2
import numpy as np
import face_recognition
from random import randrange as r
import csv
from datetime import datetime

video_capture= cv2.VideoCapture(0)
facedetect=cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')

#faces

jayanta_image =face_recognition.load_image_file("faces/jayanta.jpeg")
jayanta_encoding = face_recognition.face_encodings(jayanta_image)[0]

sourav_image =face_recognition.load_image_file("faces/sourav.jpeg")
sourav_encoding = face_recognition.face_encodings(sourav_image)[0]

bishwajit_image =face_recognition.load_image_file("faces/bishwajit.jpg")
bishwajit_encoding = face_recognition.face_encodings(bishwajit_image)[0]

elonmusk_image =face_recognition.load_image_file("faces/elonmusk.jpg")
elonmusk_encoding = face_recognition.face_encodings(elonmusk_image)[0]

know_face_encodings = [jayanta_encoding,sourav_encoding,bishwajit_encoding , elonmusk_encoding]
#face name
known_face_name= ["jayanta","sourav","bishwajit", "elonmusk"]

students =known_face_name.copy()
face_location =[]
face_encodings = []
now= datetime.now()
current_date = now.strftime("%Y-%m-%d")
#csv file name
f= open(f"{current_date}.csv","w+", newline="")
lnwriter= csv.writer(f)

imgBackground=cv2.imread("background.png")

while True:
    _, frame =video_capture.read()
#for rectangle shape
    gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces=facedetect.detectMultiScale(gray, 1.3 ,5)
    #if faces is():
        #break 
    
    for (x,y,w,h) in faces:
        cv2.rectangle(frame, (x,y), (x+w, y+h), (r(0,256),r(0,256),r(0,256)), 2)

  
    
    small_frame = cv2.resize(frame,(0,0), fx=0.25, fy =0.25)
    rgb_small_frame=cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    
    face_location= face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_location)
    for face_encoding in face_encodings:
        mathes = face_recognition.compare_faces(know_face_encodings, face_encoding)
        face_distance  = face_recognition.face_distance(know_face_encodings,face_encoding)
        best_match_index = np.argmin(face_distance)
        if(mathes[best_match_index]):
            name= known_face_name[best_match_index]

#add the text if person is present
        if name in known_face_name:
            font = cv2.FONT_HERSHEY_SIMPLEX
            bottomLeftCornerOffText =(10,100)
            fontScale = 1.5
            fontColor =(255, 0, 0)
            thikness =3
            lineType = 2
            cv2.putText(frame, name + " present",bottomLeftCornerOffText, font,fontScale, fontColor,thikness,lineType)
#stor name and date in csv
            if name in students:
                students.remove(name)
                current_time = now.strftime("%H:%M:%S")
                lnwriter.writerow([name,current_time])
#press "q" for exit
    imgBackground[162:162 + 480, 55:55 + 640] = frame
    cv2.imshow("Frame",imgBackground)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break     

video_capture.release()
cv2.destroyAllWindows()
f.close()