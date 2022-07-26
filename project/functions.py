import json
import requests
from project import ALLOWED_EXTENSIONS, db
from project.models import Attendance
import os

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


def grammar_check_api(text):
    url = "https://dnaber-languagetool.p.rapidapi.com/v2/check"
    payload = f"language=en-US&text={text}"
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "X-RapidAPI-Key": os.environ.get('LANG-API-KEY'),
        "X-RapidAPI-Host": "dnaber-languagetool.p.rapidapi.com"
    }

    response = requests.request("POST", url, data=payload, headers=headers)
    result = json.loads(response.text)


    f = open("result.html", "w")
    f.write("""
    <div class="container" style="margin-top: 10px;">
            <div class="table-responsive">
    """)

    for x in range(0, len(result['matches'])):
        f.write("""
                    <table class="table">
                            <thead>
                                <th>Topic</th>
                                <th>Description</th>
                            </thead>
                    """)

        f.write("""<tbody style = "color: black; font-style: italic" >""")

        try:
            f.write(f"<tr><td><strong>Sentence:</strong> </td> <td>{result['matches'][x]['sentence']}</td> \n")
        except:
            pass
        try:

            f.write(f"<tr><td><strong>Type:</strong></td> <td> {result['matches'][x]['shortMessage']} </td></tr>\n")
        except:
            pass
        try:
            f.write(
                f"<tr><td><strong>Replacement:</strong> </td> <td>{result['matches'][x]['replacements'][0]['value']}</td></tr> \n")
        except:
            pass
        try:

            f.write(f"<tr><td><strong>Message:</strong></td> <td> {result['matches'][x]['message']}</td></tr> \n")
        except:
            pass
        try:

            f.write(
                f"<tr><td><strong>Rule:</strong></td> <td>{result['matches'][x]['rule']['description']}</td></tr> \n")
        except:
            pass
        try:

            f.write(
                f"<tr><td><strong>Issue:</strong></td> <td> {result['matches'][x]['rule']['issueType']}</td></tr> \n")
        except:
            pass
        try:
            f.write(
                f"""<tr><td><strong>Learn more:</strong></td><td><a href = "{result['matches'][x]['rule']['urls'][0]['value']}" style = "color: BLUE;font-style: italic;text-decoration:  underline;">click here</a></td></tr> \n""")
        except:
            pass

        f.write("</tbody>\n")
        f.write("</table>\n")

    f.write("</div>\n")
    f.write("</div>\n")
    f.write("\n ")
    f.write("\n ")
    f.write("\n ")
    f.close()
    print("********************Done Writing to file*********************")
    f = open("result.html", "r")
    html = f.read()
    f.close()
    return html
