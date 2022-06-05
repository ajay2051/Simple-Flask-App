import psycopg2
import psycopg2.extras
from functools import wraps
from flask import Flask, g, render_template, redirect,request, session, flash, url_for
import re
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import *  
from random import *




app = Flask(__name__)
app.secret_key = 'kajsdjakjbc125$%^453/>.c24Nj='


mail = Mail(app) 
app.config["MAIL_SERVER"]='smtp.gmail.com'  
app.config["MAIL_PORT"] = 2525      
app.config["MAIL_USERNAME"] = 'andrew2022martin@gmail.com'  
app.config['MAIL_PASSWORD'] = 'andrew@2022'  
app.config['MAIL_USE_TLS'] = False  
app.config['MAIL_USE_SSL'] = True 
otp = randint(000000,999999)



def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database='clinic',
                            user='postgres',
                            password='1234')
    return conn


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('username') is None or session.get('loggedin') is None:
            return redirect('/login')
        
        return f(*args, **kwargs)
    return decorated_function


#Email
@app.route('/email')
def email():
    return render_template('email.html') 


#Verify
@app.route('/verify', methods = ['GET',"POST"])  
def verify():
    if request.method == 'POST':
        email = request.form["email"] 
        print(email) 
        msg = Message('OTP', sender ='andrew2022martin@gmail.com', recipients = [email])  
        msg.body = str(otp)  
        mail.send(msg)  
        return render_template('verify.html')

    return render_template('verify.html')


#Validate
@app.route('/validate',methods=["POST"])   
def validate():  
    user_otp = request.form['otp']  
    if otp == int(user_otp):  
        return "<h3> Email  verification is  successful </h3>"
    else:  
        return "<h3>failure, OTP does not match</h3>"
    


#Home
@app.route('/')
@login_required
def home():
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])
    return render_template('home.html')

#Login
@app.route('/login', methods=['GET','POST'])
def login():
    if 'authenticated' in session:
        return redirect('/')
    
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username = %s ', (username,))
        accounts = cur.fetchone()
        if accounts:
            password_rs = accounts[4]
            if check_password_hash(password_rs, password):
                session['loggedin'] = True
                session['authenticated'] = True
                session['id'] = accounts[0]
                session['username'] = accounts[2]
                return redirect('/')
            else:
                flash('Incorrect Username/Password')
        else:
            flash('Incorrect Username/Password')
    return render_template('login.html')


#Register
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        fullname = request.form['fullname']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        phone_number = request.form['phone_number']
        
        _hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        accounts = cur.fetchone()
        if accounts:
            flash('Account already exists!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Username must contain only characters and numbers!')
        elif not username or not password or not email:
            flash('Please fill out the form!')
        else:
            cur.execute("INSERT INTO users (fullname, username,email, password, phone_number ) VALUES (%s,%s,%s,%s,%s)", (fullname, username,email, _hashed_password, phone_number))
            conn.commit()
            flash('You have successfully registered!')
    elif request.method == 'POST':
        flash('Please fill out the form!')
    return render_template('register.html')


#Logout
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return redirect('/login')


#Camp
@app.route('/camp')
@login_required
def camp():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM camp ORDER BY id DESC;')
    camps = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('camp.html', camps=camps)

@app.route('/addcamp', methods = ['GET','POST'])
@login_required
def addCamp():
    if request.method == 'POST':
        camp_address = request.form['camp_address']
        camp_start_date = request.form['camp_start_date']
        camp_end_date = request.form['camp_end_date']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO camp (address, start_date, end_date) VALUES(%s, %s, %s)",(camp_address,camp_start_date, camp_end_date))
        conn.commit()
        return redirect('/camp')
        
    return render_template('create_camp.html')


@app.route('/updatecamp/<int:id>', methods = ['GET','POST'])
@login_required
def updateCamp(id):
    if request.method == 'POST':
        camp_address = request.form['camp_address']
        camp_start_date = request.form['camp_start_date']
        camp_end_date = request.form['camp_end_date']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE camp SET address = %s, start_date=%s, end_date=%s WHERE id =%s ORDER BY id DESC",(camp_address,camp_start_date, camp_end_date, id))
        conn.commit()
        return redirect('/camp')
        
    return render_template('update_camp.html')


@app.route('/deletecamp/<int:id>')
@login_required
def deleteCamp(id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM camp where id = %s", (id,))
        conn.commit()
        return redirect('/camp')


#Search
@app.route('/search', methods=['GET','POST'])
def search():
    if request.method == 'POST':
        
        patients  = '%' + request.form['search_patients'] + '%'
        print(patients)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM patients WHERE name LIKE %s',(patients,))
        all_patients = cur.fetchall()
        print(all_patients)
        conn.commit()
        msg = 'No Patient AVAILABLE'
        # for all_patient in all_patients:
        #     if len(all_patient) == 0 and patients == 'all':
        #         cur.execute("SELECT name, age, weight FROM patients WHERE id=%s", (id,))
        #         all_data = cur.fetchall()
        #         conn.commit()
                
        return render_template('search.html', all_patients=all_patients,msg=msg)
    return render_template('search.html')


#Patients
@app.route('/patients')
@login_required
def patients():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM patients;')
    patients = cur.fetchall()
    per_page = 3
    page = request.args.get('page', 1, type=int)
    offset = ( page - 1 ) * per_page
    count = len(patients)
    pages = count // per_page
    limit = 3 if page == pages else per_page 
    cur.execute('SELECT * FROM patients ORDER BY id LIMIT %s OFFSET %s', (limit, offset))
    all = cur.fetchall()
    print(pages)
    if page == 1:
        prev_page = page
    else:
        prev_page = page - 1

    if page < pages:
        next_page = page + 1
    else:
        next_page = page
    
    cur.close()
    conn.close()
    return render_template('patients.html', patients=all, prev_page=prev_page, next_page=next_page)



@app.route('/addpatient', methods = ['GET','POST'])
@login_required
def addPatient():
    if request.method == 'POST':
        patient_name = request.form['patient_name']
        patient_age = request.form['patient_age']
        patient_weight = request.form['patient_weight']
        patient_bp = request.form['patient_bp']
        patient_vision = request.form['patient_vision']
        patient_symptoms = request.form['patient_symptoms']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO patients (name, age, weight, bp, vision, symptoms ) VALUES(%s, %s, %s, %s, %s, %s)",(patient_name, patient_age, patient_weight, patient_bp, patient_vision, patient_symptoms ))
        conn.commit()
        return redirect('/patients')
        
    return render_template('add_patient.html')


@app.route('/updatepatient/<int:id>', methods = ['GET','POST'])
@login_required
def updatePatient(id):
    if request.method == 'POST':
        patient_name = request.form['patient_name']
        patient_age = request.form['patient_age']
        patient_weight = request.form['patient_weight']
        patient_bp = request.form['patient_bp']
        patient_vision = request.form['patient_vision']
        patient_symptoms = request.form['patient_symptoms']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE patients SET name = %s, age=%s, weight=%s, bp=%s, vision=%s, symptoms=%s WHERE id =%s ORDER BY id DESC",(patient_name,patient_age, patient_weight,patient_bp,patient_vision,patient_symptoms, id))
        conn.commit()
        return redirect('/patients')
        
    return render_template('update_patient.html')



@app.route('/deletepatient/<int:id>')
@login_required
def deletePatient(id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM patients where id = %s", (id,))
        conn.commit()
        return redirect('/patients')



#Department
@app.route('/user_department')
@login_required
def userDepartment():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM user_department ORDER BY id DESC;')
    user_departments = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('user_department.html', user_departments=user_departments)
        
    
@app.route('/adduserdepartment', methods = ['GET','POST'])
@login_required
def addUserDepartment():
    if request.method == 'POST':
        user_department_name = request.form['user_department_name']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO user_department (title) VALUES(%s)",(user_department_name,))
        conn.commit()
        return redirect('/user_department')
        
    return render_template('add_user_department.html')



@app.route('/updateuserdepartment/<int:id>', methods = ['GET','POST'])
@login_required
def updateUserDepartment(id):
    if request.method == 'POST':
        user_department_name = request.form['user_department_name']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE user_department SET title = %s WHERE id =%s",(user_department_name, id))
        conn.commit()
        return redirect('/user_department')
        
    return render_template('update_user_department.html')


@app.route('/deleteuserdepartment/<int:id>')
@login_required
def deleteUserDepartment(id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM user_department where id = %s", (id,))
        conn.commit()
        return redirect('/user_department')





if __name__ == '__main__':
    app.run(debug=True)