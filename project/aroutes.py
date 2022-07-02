""" aroutes is short admin routes for the webapp.
It is a collection of functions that are associated with the admin routes."""

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from project import app, db
from project.models import User, Leave
from datetime import datetime
from project.mails import send_password
from project.functions import user_attendance, user_absents

@app.route('/add_member', methods=['GET', 'POST'])
@login_required
def add_member():
    """ add_member is a function that adds a new member to the database.
    It takes roll no, email, department, graduation year, phone number and adds the user to the database.
    """
    if current_user.type == "admin":
        if request.method == 'POST':
            try:
                roll_no = request.form['roll_no'].lower()
                name = request.form['name']
                email = request.form['email']
                department = request.form['department']
                year = request.form['graduation_year']
                phone = request.form['phone']
                password_hash = User.generate_password()
                user = User(username=roll_no, name=name, email=email, department=department,
                            batch=year, phone=phone, type="student",
                            joining_date=datetime.today().strftime("%d-%m-%Y"),
                            active="true", password_hash=password_hash)
                db.session.add(user)
                db.session.commit()
                send_password(email)
                flash('User successfully added!')
                send_password(email)
                flash('Email sent successfully with password link!')
            except:
                return f"""<script>alert('User with Roll No or Email Id already Exists!'); window.location= '{request.url}'</script>"""

        return render_template('admin/add_member.html')
    else:
        return "You are not authorized to view this page"


@app.route('/admin_profile', methods=['GET', 'POST'])
@login_required
def admin_profile():
    if current_user.type == "admin":
        if request.method == 'POST':
            phone = request.form['phone']
            email = request.form['email']
            try:
                if phone:
                    current_user.phone = phone
                if email:
                    current_user.email = email
                db.session.commit()
                flash('Profile updated successfully!')
            except:
                flash('Error updating profile!, change email address')
        return render_template('admin/profile.html')
    else:
        return "You are not authorized to view this page"


@app.route('/assign_coordinator', methods=['GET', 'POST'])
@login_required
def assign_coordinator():
    if current_user.type == "admin":
        if request.method == 'POST':
            try:
                roll_no = request.form['roll_no'].lower()
                user = User.query.filter_by(username=roll_no).first()
                user.type = "coordinator"
                db.session.commit()
                flash(f'{user.name} successfully assigned as coordinator!', 'success')
            except:
                flash('Error assigning coordinator!', 'danger')
        return render_template('admin/assign_coordinator.html')
    else:
        return "You are not authorized to view this page"


@app.route('/revoke_coordinator', methods=['GET', 'POST'])
@login_required
def revoke_coordinator():
    if current_user.type == "admin":
        coordinators = User.query.filter_by(type="coordinator")
        if request.method == 'POST':
            try:
                roll_no = request.form['roll_no'].lower()
                user = User.query.filter_by(username=roll_no).first()
                user.type = "student"
                db.session.commit()
                return f"""<script>alert('{user.name} successfully revoked as coordinator!'); window.location= '{request.url}'</script>"""
            except:
                return f"""<script>alert('Error revoking coordinator!'); window.location= '{request.url}'</script>"""
        return render_template('admin/revoke_coordinator.html', coordinators=coordinators )
    else:
        return "You are not authorized to view this page"

@app.route('/team', methods=['GET', 'POST'])
@login_required
def team():
    if current_user.type == "admin":
        if request.method == 'POST':

            department = request.form['department']
            year = request.form['year']
            year1 = year
            if year == "0" and department == "0":
                students = db.session.query(User).filter(User.type != "admin").all()
            elif year == "0":
                students = db.session.query(User).filter(User.type != "admin", User.department == department).all()
            elif department == "0":
                year = User.year(int(year))
                students = db.session.query(User).filter(User.type != "admin", User.batch == year).all()
            else:
                year = User.year(int(year))
                students = db.session.query(User).filter(User.type != "admin", User.batch == year,
                                                         User.department == department).all()
            att = []
            absent = []
            for x in students:
                att.append(user_attendance(x.username))
                absent.append(user_absents(x.username))

            return render_template('admin/student_list.html', students=students, attendance=att, absent=absent,
                                   year=year1)

        return render_template('admin/team.html')
    else:
        return "You are not authorized to view this page"


@app.route('/leave_applications/<id>', methods = ['GET', 'POST'])
@login_required
def leave_applications(id):
    if current_user.type == "admin":
        applications = Leave.query.filter_by(meeting_id = id, status = 0).all()
        absent = []
        percentage = []
        if applications:
            for x in applications:
                absent.append(user_absents(x.roll_no))
                percentage.append(user_attendance(x.roll_no))
        if request.method == "POST":
            status = request.form['status'].split(',')
            application = Leave.query.filter_by(roll_no =status[0], meeting_id = id, status = 0).first()
            if status[1] == '1':
                application.status = 1
            else:
                application.status = -1
            db.session.commit()
            return redirect(request.url)  # returns to the same webpage

        return render_template('admin/leave_applications.html', applications= applications, absents = absent, percentage = percentage, id= id)
    else:
        return "you are not authorised to access this page"
