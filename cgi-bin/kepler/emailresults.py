import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os, mimetypes

def emailresults(datafile_dir, fns, subject, message, fromaddrs, toaddrs, username, password):

    if fns:
        outer = MIMEMultipart()
    else:
        outer = MIMEText(message)
    outer['Subject'] = subject
    outer['To'] = toaddrs
    outer['From'] = fromaddrs
    outer['cc'] = fromaddrs
 
    for filename in fns:
        path = os.path.join(datafile_dir, filename)
        if not os.path.isfile(path):
            continue
        ctype, encoding = mimetypes.guess_type(path)
        if ctype is None or encoding is not None:
            ctype='application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        if maintype == 'text':
            fp = open(path)
            msg = MIMEText(fp.read(), _subtype=subtype)
            fp.close()
        else:
            fp = open(path, 'rb')
            msg = MIMEBase(maintype, subtype)
            msg.set_payload(fp.read())
            fp.close()
            encoders.encode_base64(msg)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        outer.attach(msg)

    if fns:
        message_body = MIMEText('text', "plain")
        message_body.set_payload(message)
        outer.attach(message_body)

    composed = outer.as_string()

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username, password)
    server.sendmail(fromaddrs, toaddrs, composed)
    server.quit() 
