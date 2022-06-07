from socket import *
import numpy as np
import cv2 as cv
from Server import Server
import json

# sock of cli
cli = socket(AF_INET, SOCK_DGRAM)
def sendxx(msg):
    addr = ("192.168.1.101", 3334)
    if addr != None:
        # print(addr)
        cli.sendto(msg, addr)
    if msg != " ".encode('utf-8'):
        print(msg)

# proc input jpg array
img = None

ref_signal = 0
def callback(msg):
    global img,ref_signal
    image = np.asarray_chkfinite(bytearray(msg), dtype="uint8")
    img = cv.imdecode(image, cv.IMREAD_COLOR)
    ref_signal = 1

# creat input net stream
ser = Server(callback,3333)
ser.start()

# img process and order output

windowName = "WUSTCarImageService"
def proc_im(im:np.ndarray) -> np.ndarray:
    return im

cv.namedWindow(windowName, cv.WINDOW_AUTOSIZE)

# fore = cv.VideoWriter_fourcc(*'XVID')
# out = cv.VideoWriter('output.mkv', fore , 30, (160, 120))

while True:
    if img is not None and ref_signal == 1:
        # img = proc_im(img) # im progress here
        cv.imshow(windowName ,img)
        ref_signal = 0
        # out.write(img)
    key = cv.waitKey(1)    # key and delay
    if key == ord('q'):
        cv.destroyAllWindows()
        # out.release()
        break
    elif key > 0:
        sendxx(str(key).encode('utf-8'))
    else:
        sendxx(" ".encode('utf-8'))