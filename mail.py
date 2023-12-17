from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import smtplib 
from email.mime.text import MIMEText

def send_mail(to, subject, body):
    ID = "mailtest.chiba.1st@gmail.com"
    PASS = os.environ['MAIL_PASS']
    HOST = 'smtp.gmail.com'
    PORT = 587
    
    # MIME インスタンス
    msg = MIMEText(body,'html')
    
    msg['Subject'] = subject
    msg['From'] = ID
    msg['To'] = to
    
    server = SMTP(HOST,PORT)
    server.starttls()
    server.login(ID,PASS)
    server.send_message(msg)
    server.quit
    return