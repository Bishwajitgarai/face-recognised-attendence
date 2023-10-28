from sqlalchemy import create_engine,text
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from utilities import SQLALCHEMY_DATABASE_URI
from flask import render_template,redirect,url_for,flash,request,send_file, make_response,Response
from flask_login import current_user,login_required,logout_user,login_user,LoginManager,UserMixin
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
camera = None
is_capturing = False
face_cascade=cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')

app = Flask(__name__)
login_manager=LoginManager()
login_manager.init_app(app)
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

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))



class User(db.Model,UserMixin):
    __tablename__='users'
    username=db.Column(db.String(100))
    password=db.Column(db.String(100))
    id=db.Column(db.Integer,autoincrement=True,primary_key=True)

class Attendence(db.Model):
    __tablename__='attendence'
    pid=db.Column(db.Integer,autoincrement=True,primary_key=True)
    entrytime=db.Column(db.DateTime)
    date=db.Column(db.DateTime)
    exittime=db.Column(db.DateTime)
    id=db.Column(db.Integer)

class Employee(db.Model):
    __tablename__='employee'
    id=db.Column(db.Integer,autoincrement=True,primary_key=True)
    fname=db.Column(db.String(100))
    lname=db.Column(db.String(100))
    image_name=db.Column(db.String(500))
    status=db.Column(db.Integer,default=1)
    role=db.Column(db.String(100))
    org_img=db.Column(db.String(200))
    

# Create the database tables

@app.route('/', methods =['GET', 'POST'])
def admin():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template("adminlogin.html")
@app.route('/adduser', methods =['GET', 'POST'])
def adduser():
    us=User.query.filter(User.username=="admin").first()
    if not us:
        payload={"username":'admin', "password":'1234'}
        new_user = User(**payload)
        db.session.add(new_user)
        db.session.commit()
        db.session.close()
    return redirect(url_for('home'))
@login_required
@app.route('/home', methods =['GET', 'POST'])
def home():
    global is_capturing
    is_capturing = False
    return render_template("home.html")
@app.route('/checklogin', methods =['GET', 'POST'])
def checklogin():
    user=request.form.get("username")
    password=request.form.get("password")
    if password:
        password=str(password)
    if user:
            user1=User.query.filter(User.username==user,User.password==password).first()
            if user1:
                login_user(user1)
                print("Logged IN>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                return redirect(url_for("home"))
    flash("Incorrect Username Or Password ,try again")
    return render_template("adminlogin.html")
@login_required
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

@login_required
@app.route('/deleteemp/<int:id>', methods =['GET', 'POST'])
def deleteemp(id):
    emp=db.session.query(Employee).get(id)
    if emp:
        emp.status=0
    # qry=text(f""" update  employee set  status=0 where id={id} """)
    # conn.execute(qry)
    # qry=text(f""" Select * from  employee  where id={id}""")
    # emp=conn.execute(qry).fetchone()
    # conn.commit()
    # conn.close()
    flash(f'User Deleted for {emp.fname} {emp.lname}')
    db.session.commit()
    db.session.close()
    return redirect(url_for("emplist"))

@login_required
@app.route('/emplist', methods =['GET', 'POST'])
def emplist():
    empllist=db.session.query(Employee).filter(Employee.status==1).all()
    # empllist=[dict(emp.__dict__) for emp in empllist]
    # # qry=text(f""" Select * from  employee  where status=1 """)
    # # empllist=conn.execute(qry).fetchall()
    # # print(empllist)
    # # conn.commit()
    # # conn.close()
    # print(empllist)
    return render_template("emplist.html",empllist=empllist)

@login_required
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('admin'))
@login_required
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
            img_filename = secure_filename(filename)
            full_img_path=os.path.join(app.config['UPLOAD_FOLDER'], img_filename)
            org_img=file.filename
            file.save(full_img_path)
            payload={"org_img":org_img,"fname":fname,"lname":lname,"image_name":img_filename,"role":role,"status":1}
            emp=Employee(**payload)
            db.session.add(emp)
            db.session.commit()
            db.session.close()
            # qry=text(f""" insert into employee (org_img,fname,lname,image_name,role,status) values ('{org_img}','{fname}','{lname}','{image}','{role}','1')  """)
            # conn.execute(qry)
            # conn.commit()
            # conn.close()
            flash(f'User Added for {fname} {lname}')
            return redirect(url_for("emplist"))
    return redirect(url_for("emplist"))
@login_required
@app.route('/editemp/<int:id>', methods =['GET', 'POST'])
def editemp(id):
    emp=Employee.query.get(id)
    # qry=text(f""" Select * from  employee  where status=1 and id='{id}' """)
    # emp=conn.execute(qry).fetchone()
    # conn.commit()
    # conn.close()
    
    if request.method == 'POST':
        file = request.files['img']
        data=dict(request.form)
        fname=data.get("fname")
        lname=data.get("lname")
        role=data.get("role")
    
        filename=str(uuid.uuid4())+"@@@@"+file.filename
        img_filename = secure_filename(filename)
        full_img_path=os.path.join(app.config['UPLOAD_FOLDER'], img_filename)
        org_img=file.filename
        file.save(full_img_path)
        payload={"id":id,"org_img":org_img,"fname":fname,"lname":lname,"image_name":img_filename,"role":role,"status":1}
        emp=Employee(**payload)
        db.session.merge(emp)
        db.session.commit()
        db.session.close()
        flash(f'User Updated for {fname} {lname}')
        return redirect(url_for("emplist"))
        
    return render_template("editemp.html",id=id,emp=emp)
# Initialize global variables

def entry_capture_attendance():
    global camera, is_capturing

    # Open the camera
    camera = cv2.VideoCapture(0)  # Change the index to match your camera device
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

    while is_capturing:
        # Read a frame from the camera
        ret, frame = camera.read()

        if ret:
            # Convert the frame to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces in the frame
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            # Draw bounding boxes around the detected faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (r(0,256),r(0,256),r(0,256)), 2)

            small_frame = cv2.resize(frame,(0,0), fx=0.25, fy =0.25)
            rgb_small_frame=cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            face_location= face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_location)
            for face_encoding in face_encodings:
                mathes = face_recognition.compare_faces(know_face_encodings, face_encoding)
                face_distance  = face_recognition.face_distance(know_face_encodings,face_encoding)
                name="name"
                if face_distance.__len__()>0:
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
                        # Add the button overlay on the frame

            # Display the frame with bounding boxes
            imgBackground[162:162 + 480, 55:55 + 640]=frame
            ret, jpeg = cv2.imencode('.jpg', imgBackground)
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


    # Release the camera resources
    camera.release()
@app.route('/entryattendence', methods =['GET', 'POST'])
def entryattendence():
    global is_capturing
    is_capturing = True
    return Response(entry_capture_attendance(), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/entry', methods =['GET', 'POST'])
def entry():
    global is_capturing
    is_capturing = False
    return render_template("atten.html")

@app.route('/end')
def end():
    global is_capturing
    global camera
    is_capturing = False
    while(camera):
        camera.release()
        camera=None
    return redirect(url_for("home"))
def exit_capture_attendance():
    global camera, is_capturing

    # Open the camera
    camera = cv2.VideoCapture(0)  # Change the index to match your camera device
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

    while is_capturing:
        # Read a frame from the camera
        ret, frame = camera.read()

        if ret:
            # Convert the frame to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces in the frame
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            # Draw bounding boxes around the detected faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (r(0,256),r(0,256),r(0,256)), 2)

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
                    cv2.putText(frame, full_name + " Out",bottomLeftCornerOffText, font,fontScale, fontColor,thikness,lineType)
                    now = datetime.now().date()
                    formatted_date = now.strftime('%Y-%m-%d') 
                    qry=text(f""" Select * from  Attendence  where  id={name} and date='{formatted_date}'  """)
                    emp=conn.execute(qry).fetchone()
                    if  emp:
                        uqry=text(f""" update  Attendence set exittime='{datetime.now()}' where id={name} and date='{formatted_date}'  """)
                        conn.execute(uqry)
                        conn.commit()
                        conn.close()


            # Display the frame with bounding boxes
            imgBackground[162:162 + 480, 55:55 + 640]=frame
            ret, jpeg = cv2.imencode('.jpg', imgBackground)
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


    # Release the camera resources
    camera.release()


@app.route('/exit', methods =['GET', 'POST'])
def exit():
    global is_capturing
    is_capturing = False
    return render_template("exit.html")

@app.route('/exitattendence', methods =['GET', 'POST'])
def exitattendence():
    global is_capturing
    is_capturing = True
    return Response(exit_capture_attendance(), mimetype='multipart/x-mixed-replace; boundary=frame')
    
if __name__ == "__main__":
    # app.run()
    if not os.path.isfile(os.path.join(os.getcwd(),"faceattendence.db")):
        with app.app_context():
            db.create_all()
    

    app.run(debug=True)
