# import sys
# import os
from PyQt5.QtWidgets import  QDialog,QMessageBox,QLineEdit,QLabel,QPushButton
# from PyQt5 import uic
from PyQt5.QtCore import Qt,QRect,QSize,QMetaObject,QCoreApplication,QThread,pyqtSignal
from PyQt5.QtGui import QFont
import smtplib
from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from ultil.spinner import QtWaitingSpinner
USER_MAIL="iot.demo.sp2022@outlook.com.vn"
PASS_MAIL="iotdemo1234@"
def convertTime(time):
    t = datetime.fromtimestamp(time)
    return t.strftime('%d/%m/%Y %H:%M:%S:%f')[:-5]
class mailThread(QThread):
    updateData = pyqtSignal(str)
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.threadActive = True
        self.content =''
        self.subject=''
        self.mail=''
    def run(self):
        while self.threadActive==True:
            try:
                msg = MIMEMultipart()
                # storing the senders email address  
                msg['From'] = USER_MAIL
                # storing the receivers email address 
                msg['To'] = self.mail
                # storing the subject 
                msg['Subject'] = self.subject
                filename = "data.csv"
                # instance of MIMEBase and named as p
                p = MIMEBase('application', 'octet-stream')
                # To change the payload into encoded form
                p.set_payload(self.content)
                # encode into base64
                encoders.encode_base64(p)
                p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
                # attach the instance 'p' to instance 'msg'
                msg.attach(p)
                # creates SMTP session
                s = smtplib.SMTP('smtp-mail.outlook.com', 587)
                # start TLS for security
                s.starttls()
                print('begin send mail')
                # Authentication
                s.login(USER_MAIL, PASS_MAIL)
                # Converts the Multipart msg into a string
                text = msg.as_string()
                # sending the mail
                s.sendmail(USER_MAIL, self.mail, text)
                # terminating the session
                s.quit()
                self.updateData.emit('done')
                break
            except Exception as ex:
                print(ex)
                self.updateData.emit('err')
                break
    def stop(self):
        self.threadActive = False
        # self.terminate()
        # self.wait()
        self.quit() 
    
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
        self.sendMail = mailThread(self)
        self.sendMail.updateData.connect(self.updateData)

        #diable window title
        # self.setWindowFlags(Qt.FramelessWindowHint)

        #set event for buttons
        self.btn_exit.clicked.connect(self.goClose)
        self.btn_send.clicked.connect(self.handleMail)
        self.loading = QtWaitingSpinner(parent=self)
    
        # self.loading.start()

    def closeEvent(self, QCloseEvent):
        self.parent().dialog_show = False
    def goClose(self):
        # self.parent().show()
        self.close()
    def updateData(self,dt):
        self.loading.stop()
        self.sendMail.stop()
        if dt=='err':
            QMessageBox.warning(self, 'Thông báo', 'Gửi mail thất bại!', QMessageBox.Ok)
        elif dt=='done':
            QMessageBox.information(self, 'Thông báo', 'Gửi mail thành công!', QMessageBox.Ok)
            self.close()

    def handleMail(self):
        print('send email!')
        mail = self.txt_email.text()
        subject = self.txt_subject.text()
        if mail.find('@')==-1:
            return QMessageBox.warning(self, 'Thông báo', 'Vui lòng nhập email nhận!', QMessageBox.Ok)
           
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
        elif self.name ==9:
            sensor_type ='force'
            sub = sub +'lực'
            header=header+'Force value(N)\n'
        dt_lines=header
        for item in self.dt:
            dt_lines= dt_lines+convertTime(item.time)+','+str(getattr(item,sensor_type))+'\n'
        
        self.sendMail.mail = mail
        self.sendMail.subject = sub+'- '+subject
        self.sendMail.content = dt_lines
        self.sendMail.start()
        self.loading.start()
        
        # self.loading.stop()
        # QMessageBox.warning(self, 'Thông báo', 'Gửi mail thất bại!', QMessageBox.Ok)

# test app
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     # window = Home("s")
#     # window.show()
#     win = Mail([],'1')
#     win.exec()