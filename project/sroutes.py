
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from project import app, db
from project.models import User
from datetime import datetime
from project.mails import send_password


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

            except IntegrityError:
                flash('Profile not updated!', 'danger')
        return render_template('student/profile.html')
    else:
        return "You are not authorized to view this page"
