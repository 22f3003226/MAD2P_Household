from datetime import datetime
from applications.worker import celery
from celery.schedules import crontab
from jinja2 import Template
import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.mime.multipart import MIMEMultipart
from applications.models import User, HouseholdServiceRequest, HouseholdServices
import csv, os

def send_mail(email, subject, email_content, attachment=None):
    smtp_server_host = "localhost"
    smtp_port = 1025
    sender_email = "admin@A2Z.com"
    sender_password = ""

    # Create the email msg
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = email
    msg["Subject"] = subject
    #Attach html content to email
    msg.attach(MIMEText(email_content, "html")) 

    if attachment: # Exporting data to csv if attachment is provided
        #filename = "/home/shiba/mad-2p/backend/data_export.csv"
        attach = open(attachment, "rb")
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attach.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename= {os.path.basename(attachment)}")
        msg.attach(part)
    
    # Set-up Email server
    server = smtplib.SMTP(host=smtp_server_host, port=smtp_port)
    server.login(sender_email, sender_password)
    server.send_message(msg)
    server.quit()
    print("Email sent successfully.")

def get_html_report(username, data):
    with open("/home/shiba/mad-2p/frontend/report.html") as file:
        template = Template(file.read())
        html_report = template.render(username=username, request_details=data)
    return html_report



@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    sender.add_periodic_task(10.0, monthly_report.s(), name='10 sec test')
    # If you've 2 tasks which are doing the same thing, jst at different times, you need to keep the 'name' param unique.

    # Calls test_task() every 30 seconds
    sender.add_periodic_task(20.0, daily_reminder.s(), name='daily reminder 10sec')

    # sender.add_periodic_task(
    #     crontab(hour=18, minute=30),
    #     daily_reminder.s(),
    #     name = "daily reminder at 6:30pm"
    # )

    # sender.add_periodic_task(
    #     crontab(day_of_month='1', month_of_year='*'),
    #     monthly_report.s(),
    #     name = "monthly report on 1st of every month"
    # )

#@celery.task
#def test(arg):
    #print(arg)

@celery.task
def daily_reminder():
    proff = User.query.filter_by(role='service_proffessional').all()   
    current_date = datetime.now().date()  # Convert to date object
    
    for p in proff:
        if p.last_seen and (current_date - p.last_seen).days > 7:
            msg = f"<h1>Hello {p.user_name},\n\nThis is a daily reminder to visit A2Z.\n\nThanks,\nA2Z Team</h1>"
            send_mail(email=f'"{p.user_name}"@gmail.com', email_content=msg, subject="Daily reminder") 
        # else:
        #     send_mail(email=f'"{p.user_name}"@gmail.com', email_content="Daily", subject="Daily reminder")
    print("Daily reminder sent successfully.")

@celery.task
def monthly_report():
    customers = User.query.filter_by(role='customer').all() 
    for customer in customers:
        req = HouseholdServiceRequest.query.filter_by(customer_id=customer.id).all()
        req_details = []
        for r in req:
            temp = []
            proff = User.query.filter_by(id=r.service_proffessional_id).first()
            temp.append(r.id)
            temp.append(proff.user_name)
            temp.append(r.request_description)
            temp.append(r.request_status)
            temp.append(r.date_created)
            temp.append(r.date_closed)
            temp.append(r.rating_by_customer)
            temp.append(r.review_by_customer)
            req_details.append(temp)
        html_report = get_html_report(customer.user_name, req_details)
        send_mail(email=f'{User.query.filter_by(id=customer.id).first().user_name}@gmail.com', 
                  email_content=html_report, subject="Monthly report")
        print(html_report)
    print("Monthly report sent successfully.")

@celery.task
#def data_export(request_details):
def data_export():
    with open("/home/shiba/mad-2p/backend/data_export.csv", "w") as csvfile:
        writer = csv.writer(csvfile)
        closed_requests = HouseholdServiceRequest.query.filter_by(request_status='closed').all()
        writer.writerow(["Request ID", "Service Name", "Request Description", "Proffessional Name", "Customer Name", "Date Created", "Date Closed", "Rating by Customer", "Review by Customer"])
        for request in closed_requests:
            writer.writerow([request.id, HouseholdServices.query.filter_by(id=request.service_id).first().service_name, 
                             request.request_description, 
                             User.query.filter_by(id=request.service_proffessional_id).first().user_name,
                             User.query.filter_by(id=request.customer_id).first().user_name,
                             request.date_created, request.date_closed, request.rating_by_customer, request.review_by_customer])
    send_mail(email="admin@A2Z.com", email_content="Please find the exported Data.", subject="Closed requests data export", attachment="/home/shiba/mad-2p/backend/data_export.csv")        
    return "Data exported successfully."