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
USER_MAIL="drkcloud.info20@gmail.com"
PASS_MAIL="drkcloud$02"
class Mail(QDialog):
    def __init__(self,dt,name):
        # super().__init__(*args, **kwargs)
        super().__init__()
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

    def goClose(self):
        self.close()
    def sendMail(self):
        print('send email!')
        mail = self.txt_email.text()
        subject = self.txt_subject.text()
        if '@' in mail == False:
            return QMessageBox.warning(self, 'Thông báo', 'Vui lòng nhập email nhận!', QMessageBox.Ok)
        

# test app
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     # window = Home("s")
#     # window.show()
#     win = Mail([],'1')
#     win.exec()