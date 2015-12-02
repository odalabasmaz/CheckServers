# MailService.py
#
# Handles the connection to mail server and recievers
#
# @author   Orhun Dalabasmaz
# @since    Dec, 2015

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config.MailConfig import *

SMTP_SSL_PORT = 465


def connect_to_mail_server():
    if server_port == SMTP_SSL_PORT:
        mail_server = smtplib.SMTP_SSL(server_address, server_port)
    else:
        mail_server = smtplib.SMTP(server_address, server_port)
    mail_server.set_debuglevel(mail_server_debug_enabled)
    mail_server.starttls()
    mail_server.login(sender_username, sender_password)
    return mail_server


def add_signature_to_mail(mail_content):
    return mail_content.replace("</body></html>",
                                "</br>" + mail_signature + "</body></html>")


def send_mail(mail_subject, mail_content):
    print 'Sending mail...'
    mail_content = add_signature_to_mail(mail_content)
    mail_server = connect_to_mail_server()

    # Create the message
    msg = MIMEMultipart()
    msg['From'] = sender_address
    msg['To'] = ", ".join(receiver_addresses)
    msg['CC'] = ", ".join(receiver_addresses_cc)
    msg['BCC'] = ", ".join(receiver_addresses_bcc)
    msg['Subject'] = mail_subject
    msg.attach(MIMEText(mail_content, 'html'))

    try:
        mail_server.sendmail(sender_address, receiver_addresses, msg.as_string())
        print "Mail sent successfully."
        print msg.as_string()
    except EOFError:
        print "Error occurred when sending mail."
    mail_server.quit()


def send_success_mail(content):
    send_mail(usual_mail_subject, content)


def send_failure_mail(content):
    send_mail(failure_mail_subject, content)
