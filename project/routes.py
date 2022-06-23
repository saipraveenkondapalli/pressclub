from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user, login_user, logout_user
from project import app, db, bcrypt
from project.models import User, Events
from itsdangerous import URLSafeTimedSerializer as Serializer, SignatureExpired, BadSignature
from project.mails import forget_password_mail_async as send_mail


@app.route('/')
def index():
    admin = db.session.query(User.name).filter_by(type="admin").first()
    coordinators = db.session.query(User.name, User.department, User.batch).filter_by(type="coordinator").all()
    years = []
    for x in coordinators:
        years.append(User.year(int(x.batch)))
    coordinators = zip(coordinators, years)
    return render_template('index.html', name=admin.name, coordinators=coordinators)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            if bcrypt.check_password_hash(user.password_hash, password):
                login_user(user)
                session.permanent = True
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid password")
        else:
            flash("Invalid username")
    return render_template('login.html')


@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.is_authenticated:
        events = Events.query.filter_by().order_by(Events.meeting_id.desc()).limit(2)
        """ try:
            next = events[0]
            prev = events[1]
            author = (next.author).split(',')[1]
        except:
            author = "no" """
        if current_user.type == "admin":
            dcount = User.query.filter_by(badge="1").count()
            rcount = User.query.filter_by(badge="2").count()
            return render_template('admin/dashboard.html', next=next, dcount=dcount,
                                   rcount=rcount)
        elif current_user.type == "student":
            return render_template('student/dashboard.html',events= events )
        elif current_user.type == "coordinator":
            return render_template('coordinator/dashboard.html', events= events)
        else:
            return "<h1>You are not authorized to access this page</h1>"


@app.route('/forget_password', methods=['GET', 'POST'])
def forget_password():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        if user:
            send_mail(user.email)
            flash(f"mail sent to:\n{user.email}")
        else:
            flash("User not found")
    return render_template('forget.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        email = s.loads(token, salt='password-reset', max_age=600)
        user = User.query.filter_by(email=email).first()
        if request.method == 'POST':
            if request.form['password'] == request.form['confirm_password']:
                password_hash = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
                user.password_hash = password_hash
                db.session.commit()
                flash("Password changed")
                return redirect(url_for('login'))
            else:
                flash("Password doesn't match")
    except SignatureExpired:
        flash("Your link has expired")
        return redirect(url_for('forget_password'))
    except BadSignature:
        flash("Invalid link")
        return redirect(url_for('forget_password'))
    return render_template('reset.html', username=user.name)


@app.route("/test", methods=['GET', 'POST'])
def test():
    if request.method == "POST":
        for x in request.form.getlist('check'):
            print(x)

    return render_template('test.html')


@app.route("/change_password", methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == "POST":
        if bcrypt.check_password_hash(current_user.password_hash, request.form['current_password']):
            if request.form['new_password'] == request.form['confirm_password']:
                password_hash = bcrypt.generate_password_hash(request.form['new_password']).decode('utf-8')
                current_user.password_hash = password_hash
                db.session.commit()
                flash("Password changed")
                logout_user()
                return redirect(url_for('login'))
            else:
                flash("Password doesn't match")
        else:
            flash("Invalid current password")
    if current_user.type == "admin":
        return render_template('admin/change_password.html')
    elif current_user.type == "student":
        return render_template('student/change_password.html')
    elif current_user.type == "coordinator":
        return render_template('coordinator/change_password.html')
    else:
        return "<h1>You are not authorized to access this page</h1>"


@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_passowrd():
    """change_passowrd is a function that changes the coordinator password."""

    if request.method == 'POST':
        if bcrypt.check_password_hash(current_user.password_hash, request.form['current_password']):
            if request.form['new_password'] == request.form['confirm_password']:
                current_user.password_hash = bcrypt.generate_password_hash(request.form['new_password']).decode('utf-8')
                db.session.commit()
                flash('Password changed!', 'success')
                logout_user()
                return redirect(url_for('login'))
            else:
                flash('Password dont match!', 'danger')
        else:
            flash('Wrong current password!', 'danger')
    if current_user.type == "coordinator":
        return render_template('coordinator/change_password.html')
    elif current_user.type == "student":
        return render_template('student/change_password.html')
    elif current_user.type == "admin":
        return render_template('admin/change_password.html')
    else:
        return """<script>alert("Invalid user type");window.location='/';</script>"""
