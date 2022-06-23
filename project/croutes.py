""" croutes is short for coordinator routes for the webapp.
It is a collection of functions that are associated with the coordinator routes."""

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required, logout_user
from sqlalchemy.exc import IntegrityError
from project import app, db, bcrypt, ALLOWED_EXTENSIONS
from project.models import User, Events, Attendance
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from project.functions import user_attendance, user_absents


@app.route('/add_event', methods=['GET', 'POST'])
@login_required
def add_event():
    """add_event is a function that adds an event to the database."""
    if current_user.type == "coordinator":
        if request.method == 'POST':
            title = request.form['title']
            venue = request.form['venue']
            date = request.form['date']
            time = request.form['time']
            number = request.form['number']
            time = datetime.strptime(time, '%H:%M').strftime('%I:%M:%p')
            date = datetime.strptime(date, '%Y-%m-%d').strftime('%d-%m-%Y')
            try:
                event = Events(title=title, venue=venue, date=date, time=time, meeting_id=number)
                db.session.add(event)
                db.session.commit()
                flash('Event added!', 'success')
            except IntegrityError:
                flash('Event already exists., check meeting number', 'danger')

        return render_template('coordinator/add_event.html')
    else:
        return "You are not authorized to view this page"


@app.route('/coordinator/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """profile is a function that displays the coordinator profile."""

    if request.method == 'POST':
        mail = request.form['email']
        phone = request.form['phone']
        if mail:
            current_user.email = mail
        if phone:
            current_user.phone = phone
        try:
            db.session.commit()
            flash('Profile updated!', 'success')

        except IntegrityError:
            flash('Profile not updated!', 'danger')
    return render_template('coordinator/profile.html',
                           attendance = user_attendance(current_user.username), absents = user_absents(current_user.username))



@app.route('/assign_report', methods=['GET', 'POST'])
@login_required
def assign_report():
    """assign_report is a function that assigns a report to a student."""
    if request.method == "POST":
        try:
            username = request.form['username'].lower()
            meeting_id = request.form['meeting_no']
            event = Events.query.filter_by(meeting_id=meeting_id).first()
            student = User.query.filter_by(username=username).first()
            event.author = f"{student.name},{student.username}"
            db.session.commit()
            return f"""<script>window.alert('{event.title} assigned to {student.name}');window.location='/assign_report';</script>"""
        except:
            return f"""<script>window.alert('Either Roll no or meeting id is wrong');window.location='/assign_report';</script>"""

    return render_template('coordinator/assign_report.html')


@app.route('/edit_event/<id>', methods=['GET', 'POST'])
@login_required
def edit_event(id):
    if current_user.type == "coordinator":
        event = Events.query.filter_by(meeting_id=id).first()
        if request.method == "POST":
            title = request.form['title']
            venue = request.form['venue']
            time = request.form['time']
            date = request.form['date']
            if title:
                event.title = title
            if venue:
                event.venue = venue
            if time:
                time = datetime.strptime(time, '%H:%M').strftime('%I:%M:%p')
            if date:
                date = datetime.strptime(date, '%Y-%m-%d').strftime('%d-%m-%Y')
            try:
                db.session.commit()
                return f"""<script>window.alert('Event updated!');window.location='/dashboard';</script>"""
            except IntegrityError:
                return f"""<script>window.alert('Event not updated!, some error occured');window.location='/edit_event/{id}';</script>"""
        return render_template('coordinator/edit_event.html', event=event)
    else:
        return "You are not authorized to view this page"


@app.route('/coordinator/team', methods=['GET', 'POST'])
@login_required
def coordinator_team():
    if current_user.type == "coordinator":
        dcount = User.query.filter_by(badge="1").count()
        rcount = User.query.filter_by(badge="2").count()
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

            return render_template('coordinator/student_list.html',
                                   students=students,attendance = att,absent = absent, year=year1)

        return render_template('coordinator/team.html', dcount=dcount, rcount=rcount)
    else:
        return "You are not authorized to view this page"


@app.route('/attendance/<int:id>', methods=['GET', 'POST'])
@login_required
def attendance(id):
    if current_user.type == "coordinator":
        event = Events.query.filter_by(meeting_id=id).first()
        if request.method == "POST":
            users = db.session.query(User.username, User.name).filter(User.type != "admin").all()
            attendees = request.form.getlist('checkbox')
            event.attendance = str(round((len(attendees)) / len(users),2) * 100) + "%"
            db.session.commit()
            for user in users:
                if user.username in attendees:
                    user_attendance = Attendance(roll_no=user.username, meeting_id=id, status=1)
                    db.session.add(user_attendance)
                else:
                    user_attendance = Attendance(roll_no=user.username, meeting_id=id, status=0)
                    db.session.add(user_attendance)
            db.session.commit()
            return f"""<script>window.alert('Attendance updated successfully');window.location='/dashboard';</script>"""

        if request.method == "GET":
            if event.attendance:
                return f"""<script>window.alert('Attendance Taken');window.location='/dashboard';</script>"""
            students = db.session.query(User).filter(User.type != "admin", User.active == "true").all()
            return render_template('coordinator/attendance.html', id=event.meeting_id, students=students)
    else:
        return "You are not authorized to view this page"

@app.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    if current_user.type == "coordinator":
        if request.method == "POST":
            department = request.form['department']
            year = request.form['year']
            return redirect(url_for('delete_students', department=department, year=year))
        return render_template('coordinator/delete.html')


@app.route('/delete_students/<department>/<year>', methods=['GET', 'POST'])
@login_required
def delete_students( year, department):
    if current_user.type == "coordinator":
        students = student_list_fun(department= department, year=year)
        if request.method == "POST":
            check = request.form.getlist('checkbox')
            for student in students:
                if student.username in check:
                    User.query.filter_by(username=student.username).delete()
                    db.session.commit()
            return f"""<script>window.alert('Team deleted successfully');window.location='/dashboard';</script>"""

        return render_template('coordinator/delete_team.html', students=students, year=year)
    else:
        return "You are not authorized to view this page"


def student_list_fun(department, year):
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
    return students


@app.route('/delete_event/<id>', methods=['GET', 'POST'])
@login_required
def delete_event(id):
    if current_user.type == "coordinator":
        try:
            db.session.query(Events).filter(Events.meeting_id == id).delete()
            db.session.commit()
            return f"""<script>window.alert('Event {id} deleted successfully');window.location='/dashboard';</script>"""

        except:
            return f"""<script>window.alert('Invalid Meeting Id');window.location='/dashboard';</script>"""

    else:
        return "You are not authorized to view this page"