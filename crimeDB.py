from re import S
from flask import Flask,render_template,url_for,request,session,redirect

from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from sqlalchemy.sql.schema import ForeignKey, PrimaryKeyConstraint
from base64 import b64encode
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from collections import OrderedDict
from flask import *



app = Flask(__name__)

#postgres - database name
#admin - password
#configure your own database in postgresql
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres:admin@127.0.0.1:5432/postgres"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] ="filesystem"
Session(app)

print('success')
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()

global r

class Police(db.Model):
    p_id = db.Column(db.String,primary_key=True,nullable=False,unique=True)
    #dept_id = db.Column(db.Integer,ForeignKey('department.dept_id'),nullable=False)
    f_name = db.Column(db.String,nullable=False)
    l_name = db.Column(db.String,nullable=False)
    gender = db.Column(db.String,nullable=False)
    dob = db.Column(db.Date,nullable=False)
    doj = db.Column(db.Date,nullable=False)
    designation = db.Column(db.String,nullable=False)
    station = db.Column(db.String,nullable=False)
    age = db.Column(db.Integer)
    contact_no = db.Column(db.String,unique=True,nullable=False)
    pwd = db.Column(db.String,nullable=False)
    image = db.Column(db.LargeBinary,nullable=False)
    retired = db.Column(db.Integer)



class Criminal(db.Model):
    cr_id = db.Column(db.String,primary_key=True,nullable=False,unique=True)
    f_name = db.Column(db.String,nullable=False)
    l_name = db.Column(db.String,nullable=False)
    mother_n = db.Column(db.String,nullable=False)
    father_n = db.Column(db.String,nullable=False)
    dob = db.Column(db.Date,nullable=False)
    address = db.Column(db.String,nullable=False)
    identification = db.Column(db.String,nullable=False)
    image = db.Column(db.LargeBinary,nullable=False)


class Crime(db.Model):
    case_no = db.Column(db.String,primary_key=True,nullable=False,unique=True)
    description = db.Column(db.String,nullable=False)
    vicinity = db.Column(db.String,nullable=False)
    c_date = db.Column(db.Date,nullable=False)
    evidence = db.Column(db.String,nullable=False)
    p_id = db.Column(db.String,db.ForeignKey("police.p_id"))

class cr_criminal(db.Model):
    case_no = db.Column(db.String,db.ForeignKey("crime.case_no"),primary_key = True)
    cr_id = db.Column(db.String,db.ForeignKey("criminal.cr_id"),primary_key = True)



class Victims(db.Model):
    c_victims = db.Column(db.String,nullable = False,primary_key = True)
    case_no = db.Column(db.String,db.ForeignKey("crime.case_no"), primary_key=True)


@app.route('/')
def index():
    return render_template('index.html')

global a_username
a_username = "admin"
global a_password
a_password = "12345"


@app.route("/admin.html",methods=["GET","POST"])
def admin():
    if 'current_admin' in request.cookies:
        return redirect('/admin_in.html')
    if request.method=='GET':
        return render_template('admin.html')
    elif request.method=='POST':
        username = request.form["username"]
        password = request.form["pass"]
        t=0
    
        if username==a_username:
            t=1
            if password == a_password:
                resp = make_response(redirect('/admin_in.html'))
                resp.set_cookie('current_admin', str(username), max_age=604800)
                return resp
            else:
                return render_template("/admin.html",passMsg = "INVALID PASSWORD!")
        if t==0:
            return render_template("/admin.html",usrMsg = "INVALID USERNAME");

@app.route("/police.html",methods=["GET","POST"])
def police():
    if 'current_police' in request.cookies:
        return redirect('/police_in.html')
    if request.method=='GET':
        return render_template('police.html')
    elif request.method=='POST':
        username = request.form["pid"]
        password = request.form["pass"]
        t=0
        p = Police.query.all()
        for i in p:
            if i.p_id == username:
                t=1
                if i.pwd == password:
                    resp = make_response(redirect('/police_in.html'))
                    resp.set_cookie('current_police', str(username), max_age=604800)
                    return resp
                    
                else:
                    return render_template("/admin.html",passMsg = "INVALID PASSWORD!")
        if t==0:
            return render_template("/police.html",usrMsg = "INVALID PID");
    

'''@app.route("/add_police.html")
def add_police():
    return render_template('add_police.html')'''

@app.route("/admin_in.html",methods=['GET','POST'])
def admin_in():

    if 'current_admin' not in request.cookies:
        return redirect('/admin.html')
    if request.method == 'POST':
        if request.form['logout'] == "l":
            resp = make_response(redirect('/admin.html'))
            resp.set_cookie('current_admin','', max_age=0)
            return resp
    else:
        return render_template('admin_in.html')

global ca
ca = ""
@app.route("/police_in.html",methods = ['GET','POST'])
def police_in():
    if 'current_police' not in request.cookies:
        return redirect('/police.html')
    
    if request.method=='GET':
        return render_template('police_in.html')
    elif request.method=='POST': 

        if request.form['search_button'] == "l":
            resp = make_response(redirect('/police.html'))
            resp.set_cookie('current_police','', max_age=0)
            return resp

        if request.form['search_button'] == 'search':
            global ca
            caseNo = request.form['caseNo']
            ca = caseNo

            q = Crime.query.filter_by(case_no = caseNo).all()

            print("CASEE")
            print(q,type(q))

            if len(q)==0:
                return render_template('police_in.html',c_msg = "CASE RECORD DOESN'T EXIST!")
            return redirect(url_for('searchCase'))
        else:
            return redirect(url_for('analysis'))

@app.route("/analysis.html",methods = ['GET','POST'])
def analysis():
    if request.method=='GET':

        p = Crime.query.all()
        cityCount = {}
        for i in p:
            cityCount[i.vicinity] = cityCount.get(i.vicinity,0) + 1

        plt.clf()
        
        x = list(cityCount.keys())
        y = list(cityCount.values())

        plt.bar(range(len(cityCount)),y,tick_label = x)

        

        plt.savefig('static/images/analysis/cityCount.jpg')

        


        q = cr_criminal.query.all()
        crCount = {}
        for i in q:
            crCount[i.cr_id] = crCount.get(i.cr_id,0) + 1
        
        x = list(crCount.keys())
        y = list(crCount.values())

        plt.clf()

        plt.bar(range(len(crCount)),y,tick_label = x,color = ['red'])

        plt.savefig('static/images/analysis/crCount.jpg')

        r = Crime.query.all()
        yearCount = {}
        for i in r:
            yearCount[str(i.c_date)[:4]] = yearCount.get(str(i.c_date)[:4],0) + 1
        
        yearCount = OrderedDict(sorted(yearCount.items()))

        print(yearCount)
        
        
        x1 = list(yearCount.keys())
        y = list(yearCount.values())

        plt.clf()
        x.clear()
        for i in range(len(yearCount)):
            x.append(i)

        x = np.array(x)
        y = np.array(y)

        plt.xticks(x,x1)

        plt.plot(x,y,color='green', linestyle='dashed',marker ='o',markerfacecolor='blue',markersize=12 )

        plt.savefig('static/images/analysis/yearCount.jpg') 

        return render_template('analysis.html')
    

@app.route("/searchCase.html",methods = ['GET','POST'])
def searchCase():
    if request.method=='GET':
        global ca
        p = Crime.query.filter_by(case_no = ca).all()
        q = cr_criminal.query.filter_by(case_no = ca).all()
        r = Victims.query.filter_by(case_no = ca).all()

        lst = []
        for i in q:
            lst.append(i.cr_id)
        s = Criminal.query.filter(Criminal.cr_id.in_(lst)).all()

        image = []
        for i in s:
            i.image = b64encode(i.image).decode("utf-8")
            

        return render_template('searchCase.html',case = p[0],cr = s, cv = r)








@app.route('/add_police.html',methods=["GET","POST"])
def addPolice():
        if request.method=='GET':
            return render_template('add_police.html')
        elif request.method == 'POST':
            f_name=request.form.get('first_name')
            l_name=request.form.get('last_name')
            dob=request.form.get('birthday')
            gender=request.form.get('gender')
            designation=request.form.get('designation')
            station = request.form.get('station')
            contact_no=request.form.get('phone')
            doj=request.form.get('doj')
            age=request.form.get('age')
            p_id=request.form.get('pid')
            pwd=request.form.get('pwd')
            imageFile = request.files['image']


            q = Police.query.all()       
            if len(contact_no)!=10 :
                return render_template("add_police.html",mobile_msg = "MOBILE NUMBER SHOULD BE 10 DIGITS !")
            if(p_id[0] != 'P' or len(p_id)!=3 ):
                     return render_template("add_police.html",pid_msg = "P_ID SHOULD BE IN THE FORMAT: P**")
            for i in q:
                if(i.p_id == p_id):
                    return render_template("add_police.html",user_msg = "USER ALREADY EXISTS !")
            for i in q:
                if(i.contact_no == contact_no):
                    return render_template("add_police.html",mobile_msg = "MOBILE NUMBER ALREADY EXISTS !")
            
            p2=str(p_id)
            p3=str(f_name)
            p4=str(l_name)
            p5=str(gender)
            p6=dob
            p7=doj
            p8=str(designation)
            p9=str(station)
            p10=int(age)
            p11=str(contact_no)
            p12=str(pwd)
            
            object=Police(p_id = p2,f_name = p3,l_name = p4,gender = p5,dob = p6,doj = p7,designation = p8,station = p9,age= p10,contact_no = p11,pwd= p12,image = imageFile.read(),retired = 0)
            db.session.add(object)
            db.session.commit()
            
            return redirect(url_for('admin_in'))

@app.route('/temp.html')
def temp():
    obj = Police.query.filter_by(p_id = "P04").all()
    image = b64encode(obj[0].image).decode("utf-8")
    return render_template("temp.html", image = image)

@app.route('/del_police.html',methods=["GET","POST"])
def del_police():
    if request.method=='GET':
        return render_template('del_police.html')
    elif request.method == 'POST':

        pid=request.form.get('p_id')
        print("hello")
        print(pid)
        q = Police.query.all()
        for i in q:
            if i.p_id == pid:
                
                i.retired = 1
                db.session.commit()
                return render_template('admin_in.html')
        
        return render_template('del_police.html',usrMsg= "PID DOESN'T EXIST!")



@app.route('/upd_police.html',methods=["GET","POST"])
def upd_police():
    if request.method=='GET':
        return render_template('upd_police.html')
    elif request.method == 'POST':

        pid=request.form.get('p_id')
        print("hello")
        print(pid)
        q = Police.query.all()
        p=0
        for i in q:
            if i.p_id == pid:
                p=1
                global r
                r = Police.query.filter_by(p_id=pid).all()
                return render_template('update_in.html',R = r)
            else:
                continue
        if p==0:
            return render_template('upd_police.html',usrMsg= "PID DOESN'T EXIST!")

@app.route('/update_in.html',methods=["GET","POST"])
def update_in():

        if request.method=='GET':
            return render_template('update_in.html')
        elif request.method == 'POST':

            
            f_name=request.form.get('first_name')
            l_name=request.form.get('last_name')
            dob=request.form.get('birthday')
            gender=request.form.get('gender')
            designation=request.form.get('designation')
            station = request.form.get('station')
            contact_no=request.form.get('phone')
            doj=request.form.get('doj')
            age=request.form.get('age')
            p_id=request.form.get('pid')
            pwd=request.form.get('pwd')
            imageFile = request.files['image']

            global r


            q = Police.query.all()       
            if len(contact_no)!=10 :
                return render_template("update_in.html",mobile_msg = "MOBILE NUMBER SHOULD BE 10 DIGITS !", R =r)
            for i in q:
                if(i.contact_no == contact_no):
                    return render_template("update_in.html",mobile_msg = "MOBILE NUMBER ALREADY EXISTS !",R = r)
            
            p2=str(p_id)
            p3=str(f_name)
            p4=str(l_name)
            p5=str(gender)
            p6=dob
            p7=doj
            p8=str(designation)
            p9=str(station)
            p10=int(age)
            p11=str(contact_no)
            p12=str(pwd)

            print("OBJECT")
            q = Police.query.filter_by(p_id = r[0].p_id).all()
            q[0].f_name = p3
            q[0].l_name = p4
            q[0].gender = p5
            q[0].dob = p6
            q[0].doj = p7
            q[0].designation = p8
            q[0].station = p9
            q[0].age = p10
            q[0].contact_no = p11
            q[0].pwd = p12
            db.session.commit()
            
            return redirect(url_for('admin_in'))

@app.route('/add_criminal.html',methods=["GET","POST"])
def add_criminal():
    if request.method=='GET':
            return render_template('add_criminal.html')
    elif request.method == 'POST':
            f_name=request.form.get('first_name')
            l_name=request.form.get('last_name')
            dob=request.form.get('birthday')
            mother_n=request.form.get('mother_name')
            father_n=request.form.get('father_name')
            address = request.form.get('address')
            identification=request.form.get('identification')
            cr_id=request.form.get('crid')
            imageFile = request.files['image']


            q = Criminal.query.all()       
            if(cr_id[0] != 'C' and cr_id[1] != 'R'):
                     return render_template("add_criminal.html",pid_msg = "cr_ID SHOULD BE IN THE FORMAT: CR*")
            for i in q:
                if(i.cr_id == cr_id):
                    return render_template("add_criminal.html",user_msg = "CRIMINAL RECORD ALREADY EXISTS !")
            
            p2=str(cr_id)
            p3=str(f_name)
            p4=str(l_name)
            p5=str(mother_n)
            p6=str(father_n)
            p7=str(address)
            p8=str(identification)
            p9=dob

            
            object=Criminal(cr_id = p2,f_name = p3,l_name = p4,mother_n = p5,father_n= p6,address = p7,identification = p8,image = imageFile.read(),dob = p9)
            db.session.add(object)
            db.session.commit()
            return redirect(url_for('police_in'))

@app.route('/del_criminal.html',methods=["GET","POST"])
def del_criminal():
    if request.method=='GET':
        return render_template('del_criminal.html')
    elif request.method == 'POST':

        crid=request.form.get('cr_id')
        q = Criminal.query.all()
        p=0
        for i in q:
            if i.cr_id == crid:
                p=1
                Criminal.query.filter_by(cr_id = crid).delete()
                db.session.commit()
                return render_template('police_in.html')
            else:
                continue
        if p==0:
            return render_template('del_criminal.html',usrMsg= "CRID DOESN'T EXIST!")

global c
c = ""
global nc
nc = 0
global nv
nv = 0

global p2
p2 = ""
global p3
p3 = ""
global p4
p4 = ""
global p5
p5 = ""
global p6
p6 = ""
global p7
p7 = ""
global p8
p8 = 0
global p9
p9 = 0



@app.route('/add_crime.html',methods=["GET","POST"])
def add_crime():



    global nc
    global nv
    global c

    global p2
    global p3
    global p4
    global p5
    global p6
    global p7
    global p8
    global p9

    try:



        if request.method=='GET':
                return render_template('add_crime.html',firstPage = True)
        elif request.method == 'POST':

                if request.form['next_button'] == 'getcv':

                    case_no=request.form.get('case_no')
                    c = case_no
                    c_date=request.form.get('c_date')
                    description=request.form.get('description')
                    evidence=request.form.get('evidence')
                    p_id = request.form.get('pid')
                    vicinity=request.form.get('vicinity')
                    no_victims = request.form.get('no_victims')
                    no_criminals = request.form.get('no_criminals')
                
                    print("VICTIMSSSSSS")

                    print(no_victims,type(no_victims))

                    q = Crime.query.all() 

                    r = Police.query.filter_by(p_id = p_id).all()
                    for i in r:
                        if i.retired == 1:
                            return render_template("add_crime.html",pid_msg = "Police has retired!",firstPage = True)      
                    if(case_no[0] != 'C'):
                            return render_template("add_crime.html",pid_msg = "cr_ID SHOULD BE IN THE FORMAT: C*",firstPage = True)
                    for i in q:
                        if(i.case_no== case_no):
                            return render_template("add_crime.html",user_msg = "CASE RECORD ALREADY EXISTS !",firstPage = True)
                    
                    p2=str(case_no)
                    p3=c_date
                    p4=str(description)
                    p5=str(evidence)
                    p6=str(p_id)
                    p7=str(vicinity)
                    p8=no_victims
                    p9=no_criminals


                    nc = int(no_criminals)
                    nv = int(no_victims)

                    print("VICTIMSSSSSS")

                    print(no_victims,type(no_victims))

                
                    
                    return render_template('add_crime.html',nC = int(no_criminals), nV = int(no_victims) )
                else:
                    temp = []
                    for i in range(nc):
                        a = 'c' + str(i)
                        temp.append(request.form[a])
                    
                    for i in temp:
                        p = Criminal.query.all()
                        flag = 0 
                        for j in p:
                            
                            if i == j.cr_id:
                                flag  = 1
                        if flag==0:
                            return render_template('add_crime.html',nC = nc, nV = nv, cr_msg = "Criminal Record does not exist" )

                    object=Crime(case_no = p2,c_date = p3,description = p4,evidence = p5,p_id= p6,vicinity = p7)
                    db.session.add(object)
                    db.session.commit()

                    for i in range(nc):
                        a = 'c' + str(i)
                        temp = request.form[a]    
                        object = cr_criminal(case_no = c, cr_id = temp)
                        db.session.add(object)
                        db.session.commit()

                    for i in range(nv):
                        a = 'v' + str(i)
                        temp = request.form[a]
                        
                        object = Victims(case_no = c, c_victims = temp)
                        db.session.add(object)
                        db.session.commit()
                    return redirect(url_for('police_in'))
    except:
        return render_template('add_crime.html',msg = 'NO MORE THAN 2 CASES FOR ONE COP!',firstPage = True)

      
@app.route('/del_crime.html',methods=["GET","POST"])
def del_crime():
    if request.method=='GET':
        return render_template('del_crime.html')
    elif request.method == 'POST':

        caseNo=request.form.get('case_no')
        q = Crime.query.all()
        
        for i in q:
            print(i.case_no)
            if i.case_no == caseNo:
                
                Crime.query.filter_by(case_no = caseNo).delete()
                db.session.commit()
                return render_template('police_in.html')
        
       
        return render_template('del_crime.html',usrMsg= "CASE NO DOESN'T EXIST!")



          

    

if __name__ == "__main__": 
    app.run(debug=True)