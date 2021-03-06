# import sys
# import os
from PyQt5.QtWidgets import  QDialog,QMessageBox,QLineEdit,QLabel,QPushButton
# from PyQt5 import uic
from PyQt5.QtCore import Qt,QRect,QSize,QMetaObject,QCoreApplication
from PyQt5.QtGui import QFont
import smtplib
from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
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
        # uic.loadUi('mail.ui', self)
        if not self.objectName():
            self.setObjectName(u"Email")
        self.txt_email = QLineEdit(self)
        self.txt_email.setObjectName(u"txt_email")
        self.txt_email.setGeometry(QRect(120, 20, 421, 41))
        self.txt_email.setMinimumSize(QSize(0, 40))
        font = QFont()
        font.setFamily(u"Times New Roman")
        self.txt_email.setFont(font)
        self.label = QLabel(self)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 32, 91, 16))
        font1 = QFont()
        font1.setFamily(u"Times New Roman")
        font1.setPointSize(13)
        font1.setBold(False)
        font1.setWeight(50)
        self.label.setFont(font1)
        self.txt_subject = QLineEdit(self)
        self.txt_subject.setObjectName(u"txt_subject")
        self.txt_subject.setGeometry(QRect(120, 80, 421, 41))
        self.txt_subject.setMinimumSize(QSize(0, 40))
        self.txt_subject.setFont(font)
        self.label_2 = QLabel(self)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(20, 92, 91, 16))
        self.label_2.setFont(font1)
        self.btn_send = QPushButton(self)
        self.btn_send.setObjectName(u"btn_send")
        self.btn_send.setGeometry(QRect(440, 140, 101, 40))
        self.btn_send.setMinimumSize(QSize(0, 40))
        font2 = QFont()
        font2.setFamily(u"Times New Roman")
        font2.setBold(True)
        font2.setWeight(75)
        self.btn_send.setFont(font2)
        self.btn_exit = QPushButton(self)
        self.btn_exit.setObjectName(u"btn_exit")
        self.btn_exit.setGeometry(QRect(320, 140, 101, 40))
        self.btn_exit.setMinimumSize(QSize(0, 40))
        self.btn_exit.setFont(font2)

        # self.retranslateUi(self)
        self.setWindowTitle(QCoreApplication.translate("Email", u"Email", None))
        self.label.setText(QCoreApplication.translate("Email", u"Email nh\u1eadn", None))
        self.label_2.setText(QCoreApplication.translate("Email", u"Ch\u1ee7 \u0111\u1ec1", None))
        self.btn_send.setText(QCoreApplication.translate("Email", u"G\u1eedi", None))
        self.btn_exit.setText(QCoreApplication.translate("Email", u"Hu\u1ef7", None))

        QMetaObject.connectSlotsByName(self)

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
            return QMessageBox.warning(self, 'Th??ng b??o', 'Vui l??ng nh???p email nh???n!', QMessageBox.Ok)
        try:
            self.btn_send.setEnabled(False)
            self.btn_exit.setEnabled(False)
            self.txt_email.setEnabled(False)
            self.txt_subject.setEnabled(False)
            sensor_type=''
            sub ='D??? li???u c???m bi???n '
            header='Time,'
            if self.name ==0:
                sensor_type ='temp'
                sub = sub +'nhi???t ?????'
                header = header+'Temperature value(???)\n'
            elif self.name==1:
                sensor_type ='humid'
                sub = sub +'????? ???m'
                header = header+'Humidity value(%)\n'
            elif self.name ==2:
                sensor_type ='press'
                sub = sub +'??p su???t'
                header=header+'Pressure value(hPa)\n'
            elif self.name ==3:
                sensor_type ='air_oxy'
                sub = sub +'n???ng ????? oxy trong kh??ng kh??'
                header=header+'Air oxygen value(%vol)\n'
            elif self.name ==4:
                sensor_type ='co2'
                sub = sub +'CO2'
                header=header+'CO2 value(ppm)\n'
            elif self.name==5:
                sensor_type ='sound'
                sub = sub +'c?????ng ????? ??m thanh'
                header=header+'Sound value(dBA)\n'
            elif self.name ==6:
                sensor_type ='pH'
                sub = sub +'PH'
                header=header+'Ph value(pH)\n'
            elif self.name ==7:
                sensor_type ='water_oxy'
                sub = sub +'n???ng ????? oxy trong n?????c'
                header=header+'Water oxygen value(mg/L)\n'
            elif self.name ==8:
                sensor_type ='ec'
                sub = sub +'????? d???n ??i???n'
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
            QMessageBox.information(self, 'Th??ng b??o', 'G???i mail th??nh c??ng!', QMessageBox.Ok)
            self.close()
        except Exception as ex:
            print(ex)
            self.btn_send.setEnabled(True)
            self.btn_exit.setEnabled(True)
            self.txt_email.setEnabled(True)
            self.txt_subject.setEnabled(True)
            QMessageBox.warning(self, 'Th??ng b??o', 'G???i mail th???t b???i!', QMessageBox.Ok)

# test app
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     # window = Home("s")
#     # window.show()
#     win = Mail([],'1')
#     win.exec()