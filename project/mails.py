from project import app, mail
from flask import url_for
from project.models import User
from flask_mail import Message
from threading import Thread
from itsdangerous import URLSafeTimedSerializer as Serializer


def forget_password_mail_async(email):
    msg = Message()
    msg.subject = 'Reset Password'
    msg.recipients = [email]
    token = User.get_token(email)
    msg.sender = "saipraveenkondapalli@gmail.com"
    msg.body = f""" This is a link to reset your password: {url_for('reset_password', token=token, _external=True)} \nThis link  is valid only for 10 minutes.
    This is a system generated email. Please do not reply to this email."""
    mail.send(msg)
    Thread(target=send_async_email, args=(app, msg)).start()


def send_password(email):
    token = User.get_token(email)
    msg = Message()
    msg.subject = 'Create Password'
    msg.recipients = [email]
    msg.sender = "saipraveenkondapalli@gmail.com"
    msg.body = f""" This is a link to create your password: {url_for('reset_password', token=token, _external=True)}\n
    This link is valid for 10 minutes. please create your password before then. \nThis is a system generated email. Please do not reply to this email."""
    mail.send(msg)
    Thread(target=send_async_email, args=(app, msg)).start()



# Accessible only for admin

def new_user_mail(email):
    msg = Message()
    msg.subject = "Approved for Press Club, Create your profile."
    msg.recipients = [email]
    msg.sender = "saipraveenkondapalli@gmail.com"
    serial = Serializer(app.config['SECRET_KEY'])
    token = serial.dumps(email, salt='new-user')
    msg.body = f""" This is a link to create your profile: {url_for('new_user', token=token, _external=True)} \n
    This link is valid for 30 minutes. please create your profile before then. \nThis is a system generated email. Please do not reply to this email."""
    Thread(target=send_async_email, args=(app, msg)).start()


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

