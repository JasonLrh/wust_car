#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from socket import *
import time

udpClient = socket(AF_INET,SOCK_DGRAM)
address = (1,1)

HOST = ''
PORT = 3344
BUFSIZ = 1024
ADDRESS = (HOST, PORT)

udpServerSocket = socket(AF_INET, SOCK_DGRAM)
udpServerSocket.bind(ADDRESS)      # 绑定客户端口和地址

def transUdp(data):
    udpClient.sendto((data).encode(),address)

class Button(QPushButton):
    def keyPressEvent(self, a0):
        
        if (a0.key()==Qt.Key_W or a0.key()==Qt.Key_Up):
            transUdp("f")
            ex.statusBar().showMessage('^')
        elif (a0.key()==Qt.Key_S or a0.key()==Qt.Key_Down):
            transUdp("b")
            ex.statusBar().showMessage('v')
        elif (a0.key()==Qt.Key_A or a0.key()==Qt.Key_Left):
            transUdp("l")
            ex.statusBar().showMessage('<')
        elif (a0.key()==Qt.Key_D or a0.key()==Qt.Key_Right):
            transUdp("r")
            ex.statusBar().showMessage('>')
        else:
            print(a0.key())
        return # super().keyPressEvent(a0)
    def keyReleaseEvent(self, e):
        transUdp("s")
        ex.statusBar().showMessage('...')
        return super().keyReleaseEvent(e)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.ip=['localhost','3333']
        configFile = open("./info.conf","r+")
        if configFile is not None:
            data = configFile.readlines()
            data = data[0]
            self.ip = data.split(':')

        self.qle_address = QLineEdit(self);self.qle_address.setGeometry(20,10,100,20);self.qle_address.setText(self.ip[0])
        ql = QLabel(self);ql.setText(":");ql.move(124,10)
        self.port = QLineEdit(self);self.port.setGeometry(130,10,55,20);self.port.setText(self.ip[1])
        self.button = Button(self);self.button.setGeometry(190,5,100,30);self.button.setText("Connect");self.button.setCheckable(True);self.button.clicked[bool].connect(self.connectUdp)
        
        self.statusBar().showMessage('OK')
        self.setGeometry(300, 300, 300, 150)
        self.setFixedSize(300,300)
        self.setWindowFlags(Qt.WindowMinimizeButtonHint)
        self.setWindowTitle('udp connector')
        self.show()
    
    def connectUdp(self,pressed):
        global udpClient
        if pressed:
            global address
            address = (self.qle_address.text(),int( self.port.text() ))
            udpClient = socket(AF_INET,SOCK_DGRAM)
            self.button.grabKeyboard()
            self.setWindowTitle(self.qle_address.text()+ ":"+ self.port.text())
            self.statusBar().showMessage("connected")
            
            # status bar 显示连接状态
        else:
            self.button.releaseKeyboard()
            udpClient.close()
            self.statusBar().showMessage("dis-connected")
            self.setWindowTitle("udp connector")
            # status bar 隐藏
sec = 0
def setTime():
    global sec
    sec += 1
    print("sec"+str(sec))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    global ex
    ex = MainWindow()
    timer = QTimer()
    timer.timeout.connect(setTime)
    timer.start(1000)
    sys.exit(app.exec_())