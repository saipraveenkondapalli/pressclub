from project import app, mail
from flask import url_for
from project.models import User
from flask_mail import Message
from flask_login import login_required
from threading import Thread


def forget_password_mail_async(email):
    with app.app_context():
        msg = Message()
        msg.subject = 'Reset Password'
        msg.recipients = [email]
        token = User.get_token(email)
        msg.sender = "saipraveenkondapalli@gmail.com"
        msg.body = f""" This is a link to reset your password: {url_for('reset_password', token=token, _external=True)} \nThis link  is valid only for 10 minutes.
This is a system generated email. Please do not reply to this email."""
        mail.send(msg)
        Thread(target=forget_password_mail_async, args=email).start()


@login_required
def send_password(email):
    with app.app_context():
        token = User.get_token(email)
        msg = Message()
        msg.subject = 'Create Password'
        msg.recipients = [email]
        msg.sender = "saipraveenkondapalli@gmail.com"
        msg.body = f""" This is a link to create your password: {url_for('reset_password',token = token ,_external=True)}\n
This link is valid for 10 minutes. please create your password before then. \nThis is a system generated email. Please do not reply to this email."""
        mail.send(msg)
        Thread(target=send_password, args=email).start()


