from sqlalchemy import create_engine,text
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from utilities import SQLALCHEMY_DATABASE_URI
from flask import render_template,redirect,url_for,flash,request,send_file, make_response
from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np
import pandas as pd
import face_recognition
from random import randrange as r
import csv
from datetime import datetime
import io
import uuid

app = Flask(__name__)

app.secret_key = 'abskjasb#$$#%$%dfn45Y$%dnv^%$&'
app.config["SQLALCHEMY_DATABASE_URI"]=SQLALCHEMY_DATABASE_URI
app.config["UPLOAD_FOLDER"]=os.path.join(os.getcwd(),"faces")
db = SQLAlchemy(app)

engin = create_engine(SQLALCHEMY_DATABASE_URI)
conn = scoped_session(sessionmaker(bind = engin))

def dwnllocal(xlFile):

    try: 
        path=os.path.join("excels/", xlFile)
        if os.path.exists(path):
            with open(path, 'rb') as f:
                content = f.read()
            response = make_response(send_file(io.BytesIO(content),
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name=xlFile))
            response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=utf-8"
            # response = make_response(send_file(path))
            # response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=utf-8"
        
            os.remove(path)
        return response

    except Exception as e: 
            print(e)
            os.remove(os.path.join("excels/", xlFile))
@app.route('/', methods =['GET', 'POST'])
def home():
    return render_template("home.html")
@app.route('/exceldownload', methods =['GET', 'POST'])
def exceldownload():
    id=request.args.get("id")
    if id:
        qry=text(f""" Select * from  Attendence  where id={id}""")
        emp=conn.execute(qry).fetchall()
        conn.commit()
        conn.close()

        data=pd.DataFrame(emp)
        if len(data)>0:
            data["entrytime"]=pd.to_datetime(data["entrytime"]).dt.strftime('%Y-%m-%d %H:%M:%S') 
            data["entrytime"]=pd.to_datetime(data["entrytime"]) 
            data["exittime"]=pd.to_datetime(data["exittime"]).dt.strftime('%Y-%m-%d %H:%M:%S') 
            data["exittime"]=pd.to_datetime(data["exittime"])
            data["date"]=pd.to_datetime(data["date"]).dt.strftime('%Y-%m-%d') 
            data["date"]=pd.to_datetime(data["date"])
        else:
            data=pd.DataFrame()
            data["id"]=[id]
            data["id"]=data["id"].astype(int)
            data["entrytime"]=None
            data["date"]=None
            data["exittime"]=None
            
        qry=text(f""" Select * from  employee  where id={id}""")
        empdata=conn.execute(qry).fetchall()
        conn.commit()
        conn.close()
        empdata=pd.DataFrame(empdata)
        empdata["id"]=empdata["id"].astype(int)
        full_data=empdata.merge(data,on="id",how="right")
        id=full_data["id"][0]
        del full_data["status"],full_data["image_name"],full_data["org_img"] #full_data["id"],
        filename=full_data["fname"][0]+" "+full_data["lname"][0]+str(id)+"_attendence.xlsx"
        full_data.to_excel("excels/"+filename,index=False)
        data=dwnllocal(filename)
        return data

    
    return redirect(url_for("emplist"))

@app.route('/admin', methods =['GET', 'POST'])
def admin():
    return render_template("adminlogin.html")
@app.route('/deleteemp/<int:id>', methods =['GET', 'POST'])
def deleteemp(id):
    qry=text(f""" update  employee set  status=0 where id={id} """)
    conn.execute(qry)
    qry=text(f""" Select * from  employee  where id={id}""")
    emp=conn.execute(qry).fetchone()
    conn.commit()
    conn.close()
    flash(f'User Deleted for {emp[1]} {emp[2]}')
    return redirect(url_for("emplist"))
@app.route('/emplist', methods =['GET', 'POST'])
def emplist():
    qry=text(f""" Select * from  employee  where status=1 """)
    empllist=conn.execute(qry).fetchall()
    conn.commit()
    conn.close()
    return render_template("emplist.html",empllist=empllist)

@app.route('/addemp', methods =['GET', 'POST'])
def addemp():
    if request.method == 'POST':
        file = request.files['img']
        data=dict(request.form)
        fname=data.get("fname")
        lname=data.get("lname")
        role=data.get("role")
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        elif file :
            filename=str(uuid.uuid4())+"@@@@"+file.filename
            filename = secure_filename(filename)
            org_img=file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image=filename
            qry=text(f""" insert into employee (org_img,fname,lname,image_name,role) values ('{org_img}','{fname}','{lname}','{image}','{role}')  """)
            conn.execute(qry)
            conn.commit()
            conn.close()
            flash(f'User Added for {fname} {lname}')
            return redirect(url_for("emplist"))
    return redirect(url_for("emplist"))

@app.route('/editemp/<int:id>', methods =['GET', 'POST'])
def editemp(id):
    qry=text(f""" Select * from  employee  where status=1 and id='{id}' """)
    emp=conn.execute(qry).fetchone()
    conn.commit()
    conn.close()
    
    if request.method == 'POST':
        file = request.files['img']
        data=dict(request.form)
        fname=data.get("fname")
        lname=data.get("lname")
        role=data.get("role")
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        elif file :
            filename=str(uuid.uuid4())+"@@@@"+file.filename
            filename = secure_filename(filename)
            org_img=file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image=filename
            # qry=text(f""" delete from  employee where id={id} """)
            # conn.execute(qry)
            qry=text(f""" update employee set org_img='{org_img}', fname='{fname}',lname='{lname}',image_name='{image}',role='{role}' where id='{id}'  """)
            conn.execute(qry)
            conn.commit()
            conn.close()
            flash(f'User Updated for {fname} {lname}')
            return redirect(url_for("emplist"))
        
    return render_template("editemp.html",id=id,emp=emp)

@app.route('/entryattendence', methods =['GET', 'POST'])
def entryattendence():
    try:
        video_capture= cv2.VideoCapture(0)
        facedetect=cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')
        qry=text(f""" Select * from  employee  where status=1 """)
        empllist=conn.execute(qry).fetchall()
        conn.commit()
        conn.close()
        know_face_encodings=[]
        known_face_name=[]
        emp_dict={}
        for emp in empllist:
            image =face_recognition.load_image_file(f"faces/{emp.image_name}")
            encoding = face_recognition.face_encodings(image)[0]
            name =emp.fname+" "+emp.lname
            id=emp.id
            know_face_encodings.append(encoding)
            known_face_name.append(id)
            emp_dict[id]=name

        face_location =[]
        face_encodings = []
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
                    full_name=emp_dict.get(name)
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    bottomLeftCornerOffText =(10,100)
                    fontScale = 1.5
                    fontColor =(255, 0, 0)
                    thikness =3
                    lineType = 2
                    cv2.putText(frame, full_name + " present",bottomLeftCornerOffText, font,fontScale, fontColor,thikness,lineType)
                    qry=text(f""" Select * from  Attendence  where  id='{name}' and date='{datetime.now().date()}' """)
                    emp=conn.execute(qry).fetchone()
                    if not emp:
                        uqry=text(f""" insert into  Attendence(id,entrytime,date) values ('{name}','{datetime.now()}','{datetime.now().date()}') """)


                        conn.execute(uqry)
                        conn.commit()
                        conn.close()

            imgBackground[162:162 + 480, 55:55 + 640] = frame
            cv2.imshow("Frame",imgBackground)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break     

        video_capture.release()
        cv2.destroyAllWindows()
        return redirect(url_for("home"))
    except:
        if video_capture.isOpened():
            video_capture.release()
        return redirect(url_for("home"))
    finally:
        if video_capture.isOpened():
            video_capture.release()
        return redirect(url_for("home"))
@app.route('/exitattendence', methods =['GET', 'POST'])
def exitattendence():
    try:
        video_capture= cv2.VideoCapture(0)
        facedetect=cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')
        qry=text(f""" Select * from  employee  where status=1 """)
        empllist=conn.execute(qry).fetchall()
        conn.commit()
        conn.close()
        know_face_encodings=[]
        known_face_name=[]
        emp_dict={}
        for emp in empllist:
            image =face_recognition.load_image_file(f"faces/{emp.image_name}")
            encoding = face_recognition.face_encodings(image)[0]
            name =emp.fname+" "+emp.lname
            id=emp.id
            know_face_encodings.append(encoding)
            known_face_name.append(id)
            emp_dict[id]=name

        face_location =[]
        face_encodings = []
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
                    full_name=emp_dict.get(name)
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    bottomLeftCornerOffText =(10,100)
                    fontScale = 1.5
                    fontColor =(255, 0, 0)
                    thikness =3
                    lineType = 2
                    cv2.putText(frame, full_name + " present",bottomLeftCornerOffText, font,fontScale, fontColor,thikness,lineType)
                    qry=text(f""" Select * from  Attendence  where  id='{name}' and date='{datetime.now().date()}'  """)
                    emp=conn.execute(qry).fetchone()
                    if  emp:
                        uqry=text(f""" update  Attendence set exittime='{datetime.now()}' where id='{id}' """)

                        conn.execute(uqry)
                        conn.commit()
                        conn.close()

            imgBackground[162:162 + 480, 55:55 + 640] = frame
            cv2.imshow("Frame",imgBackground)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break     

        video_capture.release()
        cv2.destroyAllWindows()



        return redirect(url_for("home"))
    except:
        if video_capture.isOpened():
            video_capture.release()
        return redirect(url_for("home"))
    finally:
        if video_capture.isOpened():
            video_capture.release()
        return redirect(url_for("home"))

if __name__ == "__main__":
    # app.run()
    app.run(debug=True)

