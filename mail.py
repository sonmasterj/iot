import sys
import os
from PyQt5.QtWidgets import QApplication, QDialog,QMessageBox
from PyQt5 import uic
from PyQt5.QtCore import Qt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
USER_MAIL="iot.demo.sp2022@gmail.com"
PASS_MAIL="iotdemo1234@"
def convertTime(time):
    t = datetime.fromtimestamp(time)
    return t.strftime('%d/%m/%Y %H:%M:%S:%f')[:-5]
class Mail(QDialog):
    def __init__(self,parent,dt,name):
        # super().__init__(*args, **kwargs)
        super().__init__(parent)
        # self.userID = userID
        # super().__init__()
        self.dt = dt
        self.name = name
        self.setAttribute(Qt.WA_DeleteOnClose)
        #load ui file
        uic.loadUi('mail.ui', self)

        # #set fix size window
        self.setFixedSize(559,196)

        #diable window title
        # self.setWindowFlags(Qt.FramelessWindowHint)

        #set event for buttons
        self.btn_exit.clicked.connect(self.goClose)
        self.btn_send.clicked.connect(self.sendMail)

    def closeEvent(self, QCloseEvent):
        self.parent().dialog_show = False
    def goClose(self):
        # self.parent().show()
        self.close()

    def sendMail(self):
        print('send email!')
        mail = self.txt_email.text()
        subject = self.txt_subject.text()
        if mail.find('@')==-1:
            return QMessageBox.warning(self, 'Thông báo', 'Vui lòng nhập email nhận!', QMessageBox.Ok)
        try:
            self.btn_send.setEnabled(False)
            self.btn_exit.setEnabled(False)
            self.txt_email.setEnabled(False)
            self.txt_subject.setEnabled(False)
            sensor_type=''
            sub ='Dữ liệu cảm biến '
            header='Time,'
            if self.name ==0:
                sensor_type ='temp'
                sub = sub +'nhiệt độ'
                header = header+'Temperature value(℃)\n'
            elif self.name==1:
                sensor_type ='humid'
                sub = sub +'độ ẩm'
                header = header+'Humidity value(%)\n'
            elif self.name ==2:
                sensor_type ='press'
                sub = sub +'áp suất'
                header=header+'Pressure value(hPa)\n'
            elif self.name ==3:
                sensor_type ='air_oxy'
                sub = sub +'nồng độ oxy trong không khí'
                header=header+'Air oxygen value(%vol)\n'
            elif self.name ==4:
                sensor_type ='co2'
                sub = sub +'CO2'
                header=header+'CO2 value(ppm)\n'
            elif self.name==5:
                sensor_type ='sound'
                sub = sub +'cường độ âm thanh'
                header=header+'Sound value(dBA)\n'
            elif self.name ==6:
                sensor_type ='pH'
                sub = sub +'PH'
                header=header+'Ph value(pH)\n'
            elif self.name ==7:
                sensor_type ='water_oxy'
                sub = sub +'nồng độ oxy trong nước'
                header=header+'Water oxygen value(mg/L)\n'
            elif self.name ==8:
                sensor_type ='ec'
                sub = sub +'độ dẫn điện'
                header=header+'Electrical conductivity value(ms/cm)\n'
            dt_lines=header
            for item in self.dt:
                dt_lines= dt_lines+convertTime(item.time)+','+str(getattr(item,sensor_type))+'\n'


            msg = MIMEMultipart()
    
            # storing the senders email address  
            msg['From'] = USER_MAIL
            
            # storing the receivers email address 
            msg['To'] = mail
            
            # storing the subject 
            msg['Subject'] = sub+'-'+subject
            
            filename = "data.csv"
            
            # instance of MIMEBase and named as p
            p = MIMEBase('application', 'octet-stream')
            
            # To change the payload into encoded form
            p.set_payload(dt_lines)
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
            s.sendmail(USER_MAIL, mail, text)
            # terminating the session
            s.quit()
            QMessageBox.information(self, 'Thông báo', 'Gửi mail thành công!', QMessageBox.Ok)
            self.close()
        except Exception as ex:
            print(ex)
            self.btn_send.setEnabled(True)
            self.btn_exit.setEnabled(True)
            self.txt_email.setEnabled(True)
            self.txt_subject.setEnabled(True)
            QMessageBox.warning(self, 'Thông báo', 'Gửi mail thất bại!', QMessageBox.Ok)

# test app
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     # window = Home("s")
#     # window.show()
#     win = Mail([],'1')
#     win.exec()