import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
fromaddr = "drkcloud.info20@gmail.com"
toaddr = "congson1112@gmail.com"
USER_MAIL="drkcloud.info20@gmail.com"
PASS_MAIL="drkcloud$02"
start= datetime.now().timestamp()
# instance of MIMEMultipart
msg = MIMEMultipart()
  
# storing the senders email address  
msg['From'] = fromaddr
  
# storing the receivers email address 
msg['To'] = toaddr
  
# storing the subject 
msg['Subject'] = "Dữ liệu CO2 từ 11:00 đến 22:00"
  
# string to store the body of the mail
body = "Testing"
  
# attach the body with the msg instance
# msg.attach(MIMEText(body, 'plain'))
  
# open the file to be sent 
filename = "data.csv"
dt='Time,CO2 value\n1,1\n2,2\n'
# attachment = open("Path of the file", "rb")
  
# instance of MIMEBase and named as p
p = MIMEBase('application', 'octet-stream')
  
# To change the payload into encoded form
p.set_payload(dt)
  
# encode into base64
encoders.encode_base64(p)
   
p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
  
# attach the instance 'p' to instance 'msg'
msg.attach(p)
  
# creates SMTP session
s = smtplib.SMTP('smtp.gmail.com', 587)
  
# start TLS for security
s.starttls()

print('begin send mail')
# Authentication
s.login(USER_MAIL, PASS_MAIL)
  
# Converts the Multipart msg into a string
text = msg.as_string()

# sending the mail
s.sendmail(fromaddr, toaddr, text)
  
# terminating the session
s.quit()
end = datetime.now().timestamp()
print('done!',end-start)