import os
from flask import render_template, request, redirect, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from project import app, db
from project.functions import allowed_file, grammar_check_api
from project.models import Events


@app.route('/reports', methods=['GET', 'POST'])
def reports():
    events = Events.query.order_by(Events.meeting_id.desc()).all()
    if current_user.is_authenticated:
        if current_user.type == "coordinator":
            return render_template('coordinator/reports.html', events=events)
        elif current_user.type == "admin":
            return render_template('admin/reports.html', events=events)
        elif current_user.type == "student":
            return render_template('student/reports.html', events=events)
    else:
        return render_template('reports.html', events=events)


@app.route('/write_report/<id>', methods=['GET', 'POST'])
@login_required
def write_report(id):
    event = Events.query.filter_by(meeting_id=id).first()
    if request.method == "POST":
        report = request.form['report']
        event.report = str(report)
        print(report)
        db.session.commit()
        # ----------------------------------------IMAGE UPLOAD HANDLING-------------------------------------------------------
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        # If the user does not select a file, the browser submits an
        # empty file without a filename.

        if file.filename == '':
            return f"""<script>alert("No Image file selected");window.location='{request.url}';</script>"""

        if file and allowed_file(file.filename):
            file.filename = id + "." + file.filename.split('.')[1]
            filename = secure_filename(file.filename)
            event.image = filename
            db.session.commit()
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return f"""<script>alert("Report submitted successfully");window.location='{request.url}';</script>"""

        # -------------------------------------END OF IMAGE UPLOAD HANDLING -------------------------------
    if event:
        if current_user.type == "coordinator" and event.author.split(',')[1] == current_user.username:
            return render_template('coordinator/write_report.html', event=event)
        elif current_user.type == "student" and event.author.split(',')[1] == current_user.username:
            return render_template('student/write_report.html', event=event)
        else:
            return """<script>alert("You are not authorized to access this page");window.location = '/dashboard';</script>"""
    else:
        return """<script>alert("Invalid meeting id");window.location='/dashboard';</script>"""


@app.route('/view_report/<id>', methods=['GET', 'POST'])
def view_report(id):
    event = Events.query.filter_by(meeting_id=id).first()
    if event:
        if current_user.is_authenticated:
            if current_user.type == "coordinator":
                return render_template('coordinator/view.html', event=event)
            if current_user.type == "admin":
                return render_template('admin/view.html', event=event)
            elif current_user.type == "student":
                return render_template('student/view.html', event=event)
        else:
            return render_template('view.html', event=event)
    else:
        return """<script>alert("Invalid meeting id");window.location='/dashboard';</script>"""


@app.route('/grammar_check/<text>', methods=['GET'])
def grammar_check(text):

    return grammar_check_api(text)




