from project import db, login_manager, app, bcrypt
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer
from datetime import datetime
import random
import string

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), index=True, unique=True, nullable= False)
    username = db.Column(db.String(60), index=True, unique=True, nullable=False)
    name = db.Column(db.String(60), index=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    active = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    batch = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(20), nullable=False)
    joining_date = db.Column(db.String(20), default=datetime.today().strftime('%d-%m-%Y'))
    departure_date = db.Column(db.String(20))
    badge = db.Column(db.String(20), default="0")
    absent = db.Column(db.Text())

    def __repr__(self):
        return '<User {}>'.format(self.username)

    @staticmethod
    def get_token(email):
        serial = Serializer(app.config['SECRET_KEY'])
        return serial.dumps(email, salt='password-reset')

    @staticmethod
    def generate_password():
        password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        return password_hash

    @staticmethod
    def year(year):
        current_year = datetime.today().year
        month = datetime.today().month
        if month > 8:
            batch = current_year + 4 - year + 1
        else:
            batch = current_year + 4 - year
        return str(batch)


class Events(db.Model):
    __tablename__ = 'events'
    meeting_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    title = db.Column(db.String(60), nullable=False)
    date = db.Column(db.String(20), nullable=False, unique=True)
    time = db.Column(db.String(20), nullable=False)
    venue = db.Column(db.String(60), nullable=False)
    author = db.Column(db.String(60))
    report = db.Column(db.String())
    image = db.Column(db.String(60))
    attendance = db.Column(db.Integer, default=0)


class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    meeting_id = db.Column(db.Integer, db.ForeignKey('events.meeting_id'))
    roll_no = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.Integer, nullable=False)









