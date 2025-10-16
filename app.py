from flask import Flask,request,url_for,render_template,redirect,session,flash
import mysql.connector
import csv
import pdfkit

app=Flask(__name__)
app.secret_key="my_secret_key"

db_config={
    'host':'localhost',
    'user': 'root',
    'password' : 'suryadb575**',
    'database':'eventdb'
}

def get_db_connection():
    conn=mysql.connector.connect(**db_config)
    return conn

@app.route('/',methods=['GET','POST'])
def login():
    if request.method=="POST":
        adminname=request.form['adminname']
        adminpassword=request.form['adminpassword']
        conn=get_db_connection()
        cursor=conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM admins WHERE adminname=%s AND adminpassword=%s',(adminname,adminpassword))
        adn=cursor.fetchone()
        session['adminid']=adn['aid']
        if adn:
            return redirect('/homedashboard')
            conn.close()
            cursor.close()
        else:
            return redirect('/')
    return render_template('login.html')

@app.route('/homedashboard')
def homedashboard():
    return render_template('/homedashboard.html')

@app.route('/event',methods=['POST','GET'])
def event():
    conn=get_db_connection()
    cursor=conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM events")
    eventdata=cursor.fetchall()
    conn.close()
    cursor.close()
    return render_template('event.html',eventdata=eventdata)


@app.route('/addEventForm' ,methods=['POST','GET'])
def addEventForm():
    if request.method=='POST':
        title=request.form['title']
        description=request.form['description']
        date=request.form['date']
        location=request.form['location']
        capacity=request.form['capacity']
        price=request.form['price']
        conn=get_db_connection()
        cursor=conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM events WHERE title=%s',(title,))
        data=cursor.fetchone()
        if not data:
            cursor.execute("INSERT INTO events (title,description,date,location,capacity,price) VALUES (%s,%s,%s,%s,%s,%s)",(title,description,date,location,capacity,price))
            eid = cursor.lastrowid
            cursor.execute("INSERT INTO tickets (eid,eventname,price,available) VALUES (%s,%s,%s,%s)",(eid,title,price,capacity))
            conn.commit()
            flash("Event Registered Successfully",'success')
            conn.close()
            cursor.close()
            return redirect('/event')
        else:
            flash("This Event is Already Registered , Please Register a new Event")
            return render_template('addEventForm.html')

    return render_template('addEventForm.html')

@app.route('/editEventForm/<int:eid>',methods=['GET','POST'])
def editEventForm(eid):
    conn=get_db_connection()
    cursor=conn.cursor(dictionary=True)
    if request.method=='POST':
        title=request.form['title']
        description=request.form['description']
        date=request.form['date']
        location=request.form['location']
        capacity=request.form['capacity']
        price=request.form['price']
        cursor.execute('UPDATE events SET title=%s , description=%s , date=%s , location=%s , capacity=%s , price=%s WHERE eid=%s',(title,description,date,location,capacity,price,eid))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Event updated successfully", "success")
        return redirect('/event')
    cursor.execute("SELECT * FROM events WHERE eid=%s", (eid,))
    eventt = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('editEventForm.html',eventt=eventt)

@app.route('/deleteEvent/<int:eid>',methods=['GET','POST'])
def deleteEvent(eid):
    conn=get_db_connection()
    cursor=conn.cursor(dictionary=True)
    cursor.execute('DELETE FROM events WHERE eid=%s',(eid,))
    conn.commit()
    if cursor.rowcount>0:
        flash('Event Deleted Successfully!','success')
    else:
        flash("Sorry! Event Can't be deleted",'error')

    cursor.close()
    conn.close()
    return redirect('/event')

@app.route('/attendee',methods=['GET'])
def attendee():
    conn=get_db_connection()
    cursor=conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM events')
    eventdata=cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('attendee.html',eventdata=eventdata)


@app.route('/manageAttendee/<int:eid>',methods=['GET'])
def manageAttendee(eid):
    conn=get_db_connection()
    cursor=conn.cursor(dictionary=True)
    cursor.execute(f"CREATE TABLE IF NOT EXISTS `attendees{eid}` (eid INT,aid INT AUTO_INCREMENT PRIMARY KEY, name CHAR(50), email VARCHAR(50), mobileNo VARCHAR(15), status CHAR(50),FOREIGN KEY(eid) REFERENCES events(eid) ON DELETE CASCADE)")

    cursor.execute(f'SELECT * FROM attendees{eid}')
    attendeedata=cursor.fetchall()
    cursor.execute("SELECT * FROM events WHERE eid=%s",(eid,))
    eventdata=cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('manageAttendee.html',attendeedata=attendeedata,eventdata=eventdata)

@app.route('/addAttendeeForm/<int:eid>',methods=['GET','POST'])
def addAttendeeForm(eid):
    conn=get_db_connection()
    cursor=conn.cursor(dictionary=True)
    if request.method=='POST':
        name=request.form['name']
        mobileNo=request.form['mobileNo']
        email=request.form['email']
        status=request.form['status']
        cursor.execute(f"SELECT * FROM attendees{eid} WHERE email=%s",(email,))
        userdata=cursor.fetchone()
        if not userdata:
            cursor.execute(f"INSERT INTO attendees{eid} (eid,name,mobileNo,email,status) VALUES (%s,%s,%s,%s,%s)",(eid,name,mobileNo,email,status))
            cursor.execute("UPDATE tickets SET sold=sold+1,available=available-1,revenue=sold*price WHERE eid=%s",(eid,))
            conn.commit()
            flash("Attendee Added Sucessfully!",'success')
            cursor.close()
            conn.close()
            return redirect(f'/manageAttendee/{eid}')
        else:
            flash('Attendee Already Added','error')
            return render_template('addAttendeeForm.html')
    cursor.execute("SELECT * FROM events WHERE eid=%s",(eid,))
    edata=cursor.fetchone()
    conn.close()
    cursor.close()
    return render_template('addAttendeeForm.html',edata=edata)

@app.route('/editAttendeeForm/<int:aid>/<int:eid>', methods=['GET','POST'])
def editAttendeeForm(aid,eid):
    conn=get_db_connection()
    cursor=conn.cursor(dictionary=True)
    if request.method=="POST":
        name=request.form['name']
        email=request.form['email']
        mobileNo=request.form['mobileNo']
        status=request.form['status']
        cursor.execute(f"UPDATE attendees{eid} SET name=%s,email=%s,mobileNo=%s,status=%s WHERE aid=%s",(name,email,mobileNo,status,aid))
        conn.commit()
        flash("Attendee Details Updated Successfully!",'success')
        cursor.close()
        conn.close()
        return redirect(f'/manageAttendee/{eid}')
    cursor.execute(f'SELECT * FROM attendees{eid} WHERE aid=%s',(aid,))
    userdata=cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('editAttendeeForm.html',userdata=userdata)

@app.route('/deleteAttendee/<int:aid>/<int:eid>',methods=['GET','POST'])
def deleteAttendee(aid,eid):
    conn=get_db_connection()
    cursor=conn.cursor(dictionary=True)
    cursor.execute(f"DELETE FROM attendees{eid} WHERE aid=%s",(aid,))
    cursor.execute("UPDATE tickets SET sold=sold-1,available=available+1,revenue=sold*price WHERE eid=%s",(eid,))
    conn.commit()
    if cursor.rowcount>0:
        flash('Attendee Deleted Successfully!','success')
        return redirect(f'/manageAttendee/{eid}')
    else:
        flash("Attendee Can't be Deleted",'error')
        return render_template('manageAttendee.html')
    cursor.close()
    conn.close()


@app.route('/importcsv',methods=['GET','POST'])
def importcsv():
    if request.method=="POST":
        file=request.files['csvfile']
        if not file.filename.endswith('.csv'):
            flash('Please Upload a Valid CSV File')
            return render_template('importcsv.html')
        else:
            stream=file.stream.read().decode('UTF8').splitlines()
            reader=csv.DictReader(stream)
            conn=get_db_connection()
            cursor=conn.cursor(dictionary=True)
           
            for row in reader:  #i-->row
                cursor.execute('SELECT * FROM events WHERE title=%s',(row['title'],))
                data=cursor.fetchone()
                if data:
                    flash("Event Already Registered ! Please Register New Event",'error')
                    return render_template('importcsv.html')
                else:
                    cursor.execute("INSERT INTO events (title,description,date,location,capacity) VALUES (%s,%s,%s,%s,%s)",(row['title'],row['description'],row['date'],row['location'],row['capacity']))

            conn.commit()
            cursor.close()
            conn.close()
            flash('CSV File Imported and Event Added Successfully!','success')
            return redirect('/event')
    return render_template('importcsv.html')


@app.route('/ticket')
def ticket():
    conn=get_db_connection()
    cursor=conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM events")
    eventdata=cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('ticket.html',eventdata=eventdata)


@app.route('/trackTicket/<int:eid>',methods=['GET'])
def trackTicket(eid):
    conn=get_db_connection()
    cursor=conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM tickets WHERE eid=%s',(eid,))
    ticketdata=cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('trackTicket.html',ticketdata=ticketdata)

@app.route('/generatereport', methods=['GET'])
def viewreport():
    conn=get_db_connection()
    cursor=conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM tickets')
    ticketdata=cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('generatereport.html',ticketdata=ticketdata)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')



if __name__=='__main__':
    app.run(debug=False)

