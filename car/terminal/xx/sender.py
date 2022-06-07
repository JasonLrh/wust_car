from os import sendfile
from sys import byteorder
import cv2 as cv

from socket import *
import time
from threading import Thread

class Client:
    def __init__(self, port=3333):
        self.serv = socket(AF_INET, SOCK_DGRAM)
        self.host, self.port = "127.0.0.1", port

    def send_img(self, img):
        """
        发送通知
        :param msg:通知内容
        :return:
        """
        for x in range(img.shape[0]):
            a = [x]
            for y in range(img.shape[1]):
                for c in range(img.shape[2]):
                    a.append(int(img[x,y,c]))
            self.serv.sendto(bytes(a), (self.host, self.port))
            print(len(a))


cap = cv.VideoCapture("/Users/jason/Movies/phone/cam/VID_20201203_215555.mp4")

ret,img = cap.read()
client = Client()
while img is not None:
    ret,img = cap.read()
    img = cv.resize(img,(320,240))
    client.send_img(img=img)
