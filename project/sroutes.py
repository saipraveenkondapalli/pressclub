from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from project import app, db
from project.models import Leave, Events


@app.route('/student/profile', methods=['GET', 'POST'])
@login_required
def student_profile():
    if current_user.type == 'student':
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

            except:
                flash('Profile not updated!', 'danger')
        return render_template('student/profile.html')
    else:
        return "You are not authorized to view this page"


@app.route('/leave_request/<id>', methods=['GET', 'POST'])
@login_required
def leave_request(id):
    if current_user.type == 'student' or current_user.type == 'coordinator':
        if request.method == 'POST':
            reason = request.form['reason']
            if reason:
                leave = Leave(reason=reason, roll_no=current_user.username, meeting_id=id, name = current_user.name)
                db.session.add(leave)
                db.session.commit()
                return """<script>alert("Leave request sent!");window.location.href = '/dashboard';</script>"""
            else:
                return """<script>alert("Please enter a reason!");</script>"""

        return render_template('leave_request.html', event = Events.query.filter_by(meeting_id=id).first())
    else:
        return "You are not authorized to view this page"

