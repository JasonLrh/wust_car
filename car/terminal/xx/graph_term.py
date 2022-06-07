from PyQt5 import QtCore
import cv2 as cv
import numpy as np
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from socket import *
import time
from threading import Thread

class Server:
    def __init__(self, callback, port=3333):
        self.host, self.port = "127.0.0.1", port
        self.thread_stop_sign = False
        self.callback = callback

    def server_handle(self, callback):
        """
        UDP处理函数，收到UDP报文时会调callback函数
        :param callback:回调函数
        :return:
        """
        serv = socket(AF_INET, SOCK_DGRAM)
        serv.bind((self.host, self.port))
        while True:
            message, client_address = serv.recvfrom(2048)
            message = message.decode()
            callback(message)

    def start(self):
        """
        守护线程启动
        :return:线程成功启动，返回True，反之返回false
        """
        self.thread = Thread(target=self.server_handle, args=(self.callback,))
        self.thread.setDaemon(True)
        self.thread.start()

    def stop(self):
        """
        守护线程启动
        :return:线程关闭
        """
        self.thread_stop_sign = True
        serv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        serv.sendto(b"stop", (self.host, self.port))

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        size = (240,320)
        self.img = cv.imread("/Users/jason/Desktop/0.jpg")
        # cv.merge([np.zeros(size,np.uint8),np.zeros(size,np.uint8),np.zeros(size,np.uint8)])
        self.initUI()
    
    def initUI(self):
        # np.ndarray.tobytes
        qim = QImage(self.img.tobytes() ,width=self.img.shape[1],height=self.img.shape[0],format=QImage.Format_BGR888)
        imglabel = QLabel()
        imglabel.setScaledContents(True)
        
        imglabel.resize(QtCore.QSize(self.img.shape[1],self.img.shape[0]))
        imglabel.setPixmap(QPixmap.fromImage(qim))
        
        self.statusBar().showMessage('OK')
        self.setGeometry(300, 500, 500, 500)
        self.setFixedSize(300,300)
        self.setWindowFlags(Qt.WindowMinimizeButtonHint)
        self.setWindowTitle('udp connector')
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    global ex
    ex = MainWindow()
    sys.exit(app.exec_())