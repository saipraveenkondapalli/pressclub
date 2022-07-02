from project import ALLOWED_EXTENSIONS, db
from project.models import User, Attendance, Leave



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def user_attendance(username):
    present = db.session.query(Attendance).filter(Attendance.roll_no == username,
                                                  Attendance.status == '1').count()
    absent = db.session.query(Attendance).filter(Attendance.roll_no == username,
                                                 Attendance.status == '0').count()
    try:
        percentage = str((present / (present + absent)) * 100).split('.')[0] + "%"
    except ZeroDivisionError:
        percentage = "0%"
    return percentage


def user_absents(username):
    ab= db.session.query(Attendance.meeting_id).filter(Attendance.roll_no == username,
                                               Attendance.status == '0').all()
    absent = ''
    for x in ab:
        x = str(x)
        x = x.split('(')[1].split(',)')[0]
        absent += x + ','
        absent = absent[:-1]
    return absent