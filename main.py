# FLASK AND BOOTSTRAP
import sqlite3

from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from datetime import datetime, timedelta
import requests
from operator import itemgetter

# FLASK FORM THAT VALIDATES
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, FloatField, DateField, DateTimeField, PasswordField
from wtforms.validators import DataRequired, EqualTo

# FLASK SQLALCHEMY FOR DATABASE
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

app = Flask(__name__)
app.config['SECRET_KEY'] = '89SEKurz93Ji5PtcA1hOtFnB3g46YyU2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
engine = create_engine('sqlite:///appointments-database.db', connect_args={'check_same_thread': False})
Session = sessionmaker(bind=engine, autoflush=False)
session = scoped_session(Session)
Base = declarative_base()
Base.query = session.query_property()
Bootstrap(app)
year = datetime.now().year
print(datetime.now())



# CALENDLY API
# calendly_access_token = "eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL2F1dGguY2FsZW5kbHkuY29tIiwiaWF0IjoxNjU0MTgzNDUzLCJqdGkiOiIyMWFhMjU0Mi1lNzA4LTQ0NmUtOTI0ZC00NjIwOTE5NWM4NTYiLCJ1c2VyX3V1aWQiOiJiNGNiYzFmNS1iMWRlLTQ3NGEtOTJjNS1iNjc5MWIwOGZmODgifQ._2iACddAbjpu9dxpKNCYxTZlflumldCYA87RXTgjpbo"

#Getting Organizational URI
# header = {
#     "authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL2F1dGguY2FsZW5kbHkuY29tIiwiaWF0IjoxNjU0MTgzNDUzLCJqdGkiOiIyMWFhMjU0Mi1lNzA4LTQ0NmUtOTI0ZC00NjIwOTE5NWM4NTYiLCJ1c2VyX3V1aWQiOiJiNGNiYzFmNS1iMWRlLTQ3NGEtOTJjNS1iNjc5MWIwOGZmODgifQ._2iACddAbjpu9dxpKNCYxTZlflumldCYA87RXTgjpbo"
# }
# response = requests.get("https://api.calendly.com/users/me", headers=header).json()
# print(response)
organization_uri = "https://api.calendly.com/organizations/39a4ab6b-9e91-404b-9129-fb745652a6da"

# Creating Webhook on https://developer.calendly.com/api-docs/c1ddc06ce1f1b-create-webhook-subscription

# params = {
#     "url": "your url/webhook",
#     "events": [
#         "invitee.created",
#         "invitee.canceled"
#     ],
#     "organization": "organization_uri",
#     "scope": "organization"
# }


calendly_header = {
    "Content-Type": "application/json",
    "authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL2F1dGguY2FsZW5kbHkuY29tIiwiaWF0IjoxNjU0MTgzNDUzLCJqdGkiOiIyMWFhMjU0Mi1lNzA4LTQ0NmUtOTI0ZC00NjIwOTE5NWM4NTYiLCJ1c2VyX3V1aWQiOiJiNGNiYzFmNS1iMWRlLTQ3NGEtOTJjNS1iNjc5MWIwOGZmODgifQ._2iACddAbjpu9dxpKNCYxTZlflumldCYA87RXTgjpbo"
}

# BULK SMS API

bsms_url = 'https://www.bulksmsnigeria.com/api/v1/sms/create'
bsms_token = "20NIW0yQ0ssYaqKQQlSEI2gSkr3xOHHBsNPzys9Lv25elywxwG4StbNKlR5Y"
bridget_no = "23481434664"

bsms_headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json'
}


# ADMIN LOGIN FORM
class LoginForm(FlaskForm):
    key = PasswordField("Enter Secret Key", validators=[DataRequired()])
    login = SubmitField("Login")

# DATABASE TABLES


class PhoneAppointments(Base):
    __tablename__ = 'phone_appointments'

    id = Column(Integer, primary_key=True)
    date_added = Column(String(250))
    appointment_type = Column(String(250))
    appointment_date = Column(String(250))
    appointment_time = Column(String(250))
    client_name = Column(String(250))
    client_email = Column(String(250))
    client_phone = Column(String(250))
    message = Column(String(250))


class InPersonMeeting(Base):
    __tablename__ = 'in_person_appointments'

    id = Column(Integer, primary_key=True)
    date_added = Column(String(250))
    appointment_type = Column(String(250))
    appointment_date = Column(String(250))
    appointment_time = Column(String(250))
    client_name = Column(String(250))
    client_email = Column(String(250))
    client_phone = Column(Integer)
    message = Column(String(250))


Base.metadata.create_all(engine)


# WEB PAGES

@app.route('/')
def homepage():
    return render_template("index.html", year=year)


@app.route('/book-appointment')
def book_appointment():
    return render_template("book_appointment.html")


@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        booker_response = request.json
        # BOOKERS DETAILS
        email = booker_response["payload"]["email"]
        name = booker_response["payload"]["name"]
        message = booker_response["payload"]["questions_and_answers"][0]["answer"]
        text_reminder_to = booker_response["payload"]["questions_and_answers"][1]["answer"].replace(' ', '')

        # BOOKING DETAILS
        event_uri = booker_response["payload"]["event"]
        event_response = requests.get(f"{event_uri}", headers=calendly_header).json()
        event_name = event_response["resource"]["name"]
        event_start_time = event_response["resource"]["start_time"]

        # IC MEANS INCORRECT BECAUSE CALENDLY INCORRECTLY DEDUCTED 1HOUR TO THE TIME. REMEMBER TO KEEP CHECKING IF THEY'VE FIXED THIS
        ic_event_date = (event_start_time.split('T'))[0]
        ic_event_time = (event_start_time.split('T'))[1].split('.')[0]
        event_date_and_time = datetime.strptime(ic_event_date + ' ' + ic_event_time, '%Y-%m-%d %H:%M:%S') + timedelta(
            minutes=60)
        str_event_date_and_time = str(event_date_and_time.strftime('%Y-%m-%d %H:%M:%S'))
        event_date = str_event_date_and_time.split(' ')[0]
        event_time = str_event_date_and_time.split(' ')[1]


        # NOTIFY BRIDGET OF THE NEW BOOKING
        newb_params = {
            'api_token': bsms_token,
            'to': '2348143466411',
            'from': 'New Booking',
            'body': f'New {event_name} with {name} at {event_time} on {event_date}. Visit www.lekkiajahikoyi.com/admin for more details. ',
        }
        requests.post(bsms_url, headers=bsms_headers, params=newb_params).json()

        if event_name == "Phone Call Appointment":

            rem_date_and_time = datetime.strptime(event_date + ' ' + event_time, '%Y-%m-%d %H:%M:%S') - timedelta(
                minutes=30)
            rem_date_and_time.strftime('%Y-%m-%d %H:%M:%S')

            #SEND REMINDER TO BRIDGET
            # brem_params = {
            #     'user': 'jubril',
            #     'password': 'jubrilBSMS',
            #     'mobile': '08143466411',
            #     'senderid': 'Appointment',
            #     'message': f'Reminder: {event_name} with {name}, {text_reminder_to} at {event_time}.',
            #     'schedule': '2022:06:02:18:35:00'
            # }
            # brem_response = requests.post("https://bulksmsnigeria.ng/sendsms.php", params=brem_params).json()
            # print(brem_response)

            # SEND REMINDER TO CLIENT
            # crem_params = {
            #     'api_token': bsms_token,
            #     'to': text_reminder_to,
            #     'from': 'Bridget LAI',
            #     'body': f'Reminder: {event_name} with Lekki Ajah Ikoyi Property Investment Ltd. at {event_time}. Call: +2348050922659',
            #     'schedule': rem_date_and_time
            # }
            # crem_response = requests.post(bsms_url, headers=bsms_headers, params=crem_params).json()
            # print(crem_response)
            #
            # ADD EVENT TO DATABASE
            new_phone_appointment = PhoneAppointments(
                date_added=datetime.now().date(),
                appointment_type=event_name,
                appointment_date=event_date,
                appointment_time=event_time,
                client_name=name,
                client_email=email,
                client_phone=text_reminder_to,
                message=message
            )
            session.add(new_phone_appointment)
            session.commit()

        else:

            rem_date_and_time = event_date + " 07:00:00"

            # SEND REMINDER TO BRIDGET
            # brem_params = {
            #     'api_token': bsms_token,
            #     'to': bridget_no,
            #     'from': 'Appointment',
            #     'body': f'Reminder: {event_name} with {name}, {text_reminder_to} at {event_time} on {event_date}.',
            #     'schedule': rem_date_and_time
            # }
            # brem_response = requests.post(bsms_url, headers=bsms_headers, params=brem_params).json()
            # print(brem_response)
            #
            # # SEND REMINDER TO CLIENT
            # crem_params = {
            #     'api_token': bsms_token,
            #     'to': text_reminder_to,
            #     'from': 'Bridget LAI',
            #     'body': f'Reminder: {event_name} with Lekki Ajah Ikoyi Property Investment Ltd. at {event_time} on {event_date}. Location: Level 1, Suit 1A Dominion Plaza, Igbo Efon, Lekki-Epe Expressway, Lagos.',
            #     'schedule': rem_date_and_time
            # }
            # crem_response = requests.post(bsms_url, headers=bsms_headers, params=brem_params).json()
            # print(crem_response)

            # ADD EVENT TO DATABASE
            new_inperson_apointment = InPersonMeeting(
                date_added=datetime.now().date(),
                appointment_type=event_name,
                appointment_date=event_date,
                appointment_time=event_time,
                client_name=name,
                client_email=email,
                client_phone=text_reminder_to,
                message=message,
            )
            session.add(new_inperson_apointment)
            session.commit()

        return "Received!"


# GETTING AND SORTING ALL IN_PERSON APPOINTMENTS
def upia():
    ip_appointments = InPersonMeeting.query.all()
    sorting_ip_appointments = [{"appointment": appointment, "date_time": str(
        f"{appointment.appointment_date.replace('-', '')}{appointment.appointment_time.replace(':', '')}")} for
                               appointment in ip_appointments]
    sorted_ip_appointments = sorted(sorting_ip_appointments, key=itemgetter('date_time'), reverse=True)
    ip_appointments = [appointment["appointment"] for appointment in sorted_ip_appointments]
    upcoming_ipa = []
    for ip_appointment in ip_appointments:
        appointment_year = ip_appointment.appointment_date.split('-')[0]
        appointment_month = ip_appointment.appointment_date.split('-')[1]
        appointment_day = ip_appointment.appointment_date.split('-')[2]
        appointment_hour = ip_appointment.appointment_time.split(':')[0]
        appointment_min = ip_appointment.appointment_time.split(':')[1]

        if int(appointment_year) > datetime.now().year:
            upcoming_ipa.append(ip_appointment)
        elif int(appointment_year) == datetime.now().year and int(appointment_month) > datetime.now().month:
            upcoming_ipa.append(ip_appointment)
        elif int(appointment_year) == datetime.now().year and int(appointment_month) == datetime.now().month and int(
                appointment_day) > datetime.now().day:
            upcoming_ipa.append(ip_appointment)
        elif int(appointment_year) == datetime.now().year and int(appointment_month) == datetime.now().month and int(
                appointment_day) == datetime.now().day and int(appointment_hour) > datetime.now().hour:
            upcoming_ipa.append(ip_appointment)
        elif int(appointment_year) == datetime.now().year and int(appointment_month) == datetime.now().month and int(
                appointment_day) == datetime.now().day and int(appointment_hour) == datetime.now().hour and int(
                appointment_min) > datetime.now().minute:
            upcoming_ipa.append(ip_appointment)
    return upcoming_ipa


# GETTING AND SORTING ALL PHONE APPOINTMENTS
def upa():
    phone_appointments = PhoneAppointments.query.all()
    sorting_phone_appointments = [{"appointment": appointment, "date_time": str(
        f"{appointment.appointment_date.replace('-', '')}{appointment.appointment_time.replace(':', '')}")} for
                                  appointment in phone_appointments]
    sorted_phone_appointments = sorted(sorting_phone_appointments, key=itemgetter('date_time'), reverse=True)
    phone_appointments = [appointment["appointment"] for appointment in sorted_phone_appointments]
    upcoming_pa = []
    for phone_appointment in phone_appointments:
        appointment_year = phone_appointment.appointment_date.split('-')[0]
        appointment_month = phone_appointment.appointment_date.split('-')[1]
        appointment_day = phone_appointment.appointment_date.split('-')[2]
        appointment_hour = phone_appointment.appointment_time.split(':')[0]
        appointment_min = phone_appointment.appointment_time.split(':')[1]

        if int(appointment_year) > datetime.now().year:
            upcoming_pa.append(phone_appointment)
        elif int(appointment_year) == datetime.now().year and int(appointment_month) > datetime.now().month:
            upcoming_pa.append(phone_appointment)
        elif int(appointment_year) == datetime.now().year and int(appointment_month) == datetime.now().month and int(
                appointment_day) > datetime.now().day:
            upcoming_pa.append(phone_appointment)
        elif int(appointment_year) == datetime.now().year and int(appointment_month) == datetime.now().month and int(
                appointment_day) == datetime.now().day and int(appointment_hour) > datetime.now().hour:
            upcoming_pa.append(phone_appointment)
        elif int(appointment_year) == datetime.now().year and int(appointment_month) == datetime.now().month and int(
                appointment_day) == datetime.now().day and int(appointment_hour) == datetime.now().hour and int(
                appointment_min) > datetime.now().minute:
            upcoming_pa.append(phone_appointment)

    return upcoming_pa


# GETTING ALL APPOINTMENTS BY ADDING IPA AND PA AND SORTING THEM
def all_a():
    ip_appointments = InPersonMeeting.query.all()
    phone_appointments = PhoneAppointments.query.all()
    all_appointment = ip_appointments + phone_appointments
    sorting_all_appointments = [{"appointment": appointment, "date_time": str(f"{appointment.appointment_date.replace('-', '')}{appointment.appointment_time.replace(':', '')}")} for appointment in all_appointment]
    sorted_all_appointments = sorted(sorting_all_appointments, key=itemgetter('date_time'), reverse=True)
    all_appointment = [appointment["appointment"] for appointment in sorted_all_appointments]
    new_all_appointments = []
    for appointment in all_appointment:
        new_all_appointments.append(appointment)
    return new_all_appointments


@app.route('/admin', methods=["GET", "POST"])
def admin():
    form = LoginForm()

    if request.method == "GET":
        return render_template("admin_login.html", form=form)
    if request.method == "POST":
        if not form.validate_on_submit():
            return render_template('admin_login.html', form=form)
        if form.validate_on_submit() and form.key.data != "secret&$LAI!key":
            incorrect_password = True
            return render_template("admin_login.html", form=form, incorrect_password=incorrect_password)
        if form.validate_on_submit() and form.key.data == "secret&$LAI!key":
            upcoming_pa = upa()
            upcoming_pa_len = len(upcoming_pa)
            upcoming_ipa = upia()
            upcoming_ipa_len = len(upcoming_ipa)
            return render_template("admin_page.html", upcoming_pa_len=upcoming_pa_len, upcoming_ipa_len=upcoming_ipa_len)


@app.route('/admin/upcoming-phone-apointments')
def upcoming_phone_appointments():
    upcoming_pa = upa()
    return render_template("upcoming_phone_appointments.html", upcoming_pa=upcoming_pa)


@app.route('/admin/upcoming-inperson-apointments')
def upcoming_inperson_appointments():
    upcoming_ipa = upia()
    return render_template("upcoming_inperson_appointments.html", upcoming_ipa=upcoming_ipa)


@app.route('/admin/all-appointments')
def all_appointments():
    new_all_appointments = all_a()
    return render_template("all_appointments.html", all_appointments=new_all_appointments)


@app.route('/admin/all-invitees')
def all_invitees():
    new_all_appointments = all_a()
    return render_template("all_invitees.html", all_appointments=new_all_appointments)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
