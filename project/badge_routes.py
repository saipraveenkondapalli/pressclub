from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required, logout_user
from sqlalchemy.exc import IntegrityError
from project import app, db, bcrypt
from project.models import User, Events, Attendance
from datetime import datetime


@app.route('/distribute_badges', methods=['GET', 'POST'])
@login_required
def distribute():
    if request.method  == "GET":
        if current_user.type == "coordinator":
            return render_template('coordinator/distribute_badges.html')
        elif current_user.type == "admin":
            return render_template('admin/distribute_badges.html')
    if request.method == 'POST':
        username = request.form['username'].lower()
        user = User.query.filter_by(username=username).first()
        print("post is working -----------------------------------------")
        try:
            user.badge = "1"  # 1 for assigned badge
            db.session.commit()
            return f"""<script>window.alert('Successfully assigned badge to {user.name} ');window.location='/distribute_badges';</script>"""
        except:
            return """<script>window.alert('Badge not assigned! ,Invalid Roll No');window.location='/distribute_badges';</script>"""

    else:
        return "You are not authorized to view this page"


@app.route('/badge_distributed_list', methods=['GET', 'POST'])
@login_required
def badge_distributed_list():
    state = "Distributed"
    students = db.session.query(User).filter(User.type != "admin", User.badge == "1").all()
    if current_user.type == "coordinator":
        return render_template('coordinator/badge_list.html', students=students, state=state)
    elif current_user.type == "admin":
        return render_template('admin/badge_list.html', students=students, state=state)
    else:
        return "You are not authorized to view this page"


@app.route('/return_badges', methods=['GET', 'POST'])
@login_required
def return_badges():
    if request.method == "GET":
        if current_user.type == "coordinator":
            return render_template('coordinator/return_badges.html')
        elif current_user.type == "admin":
            return render_template('admin/return_badges.html')

    if request.method == "POST":
        username = request.form['username'].lower()
        user = User.query.filter_by(username=username).first()
        try:
            user.badge = "2"
            db.session.commit()
            return f"""<script>window.alert('{user.name} successfully returned badge   ');window.location='/return_badges';</script>"""
        except:
            return f"""<script>window.alert('badge not returned, Invalid Roll NO');window.location='/return_badges';</script>"""

    else:
        return "You are not authorized to view this page"


@app.route('/badge_returned_list', methods=['GET', 'POST'])
@login_required
def badge_returned_list():
    state = "Returned"
    students = db.session.query(User).filter(User.type != "admin", User.badge == "2").all()
    if current_user.type == "coordinator":
        return render_template('coordinator/badge_list.html', students=students, state=state)
    elif current_user.type == "admin":
        return render_template('admin/badge_list.html', students=students, state=state)
    else:
        return "You are not authorized to view this page"