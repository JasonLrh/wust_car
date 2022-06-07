from socket import *
import json
import time
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QLabel, QLayout, QWidget, QCheckBox, QApplication
from PyQt5.QtCore import *
from PyQt5 import QtCore

import sys

# addr = ("192.168.1.101", 3334)
# cli = socket(AF_INET, SOCK_DGRAM)

# while True:
#     dic = {"y":8,"x":2}
#     msg = json.dumps(dic)
#     cli.sendto(msg.encode('utf-8'), addr)
#     time.sleep(0.1)

class Example(QWidget):
     
    def __init__(self):
        super().__init__()
        self.addr = ("192.168.1.101", 3334)
        self.cli = socket(AF_INET, SOCK_DGRAM)
        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_timeout)
        self.timer.start(30)
        self.speed = (0,0)
        self.label = QLabel(self)
        self.label.setGeometry(0,140,150,20)
        
        self.label.setText("aaa")
        self.initUI()
         
         
    def initUI(self):
        self.setGeometry(300, 300, 300, 300)
        self.setWindowTitle('QCheckBox')
        self.show()
    
    def mousePressEvent(self, event: QMouseEvent):
        # print((event.x(),event.y()))
        if event.buttons() == QtCore.Qt.LeftButton:                          # 左键按下
            # print((event.x(),event.y()))
            pass
    
    def mouseMoveEvent(self,event: QMouseEvent):
        x =   ( event.x() - 150 )
        y = - ( event.y() - 150 )
        def p(s):
            if s < 0:
                return -int(36*(-s/6)**(0.5))
            else:
                return int(36*(s/6)**(0.5))
        self.speed = (p(y + x), p(y - x)) 
        # print((event.x(),event.y()))
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        self.speed = (0,0)
        # print((0, 0))
    
    def timer_timeout(self):
        dic = {"y":self.speed[0],"x":self.speed[1]}
        msg = json.dumps(dic)
        self.label.setText(msg)
        self.cli.sendto(msg.encode('utf-8'), self.addr)

         
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    
    sys.exit(app.exec_())