import cv2 as cv
import numpy as np
import json
# from Server import Server
# from socket import *

R_Standard = (20,45) # EDIT: lineWidth
windowName = "WUSTCarImageService"
quick_config_file = './data.txt'

def Send_Direction(y:int,x:int):
    dic = {"y":y,"x":x}
    msg = json.dumps(dic)
    print(msg)

total_frames = 0

last_point = 0

offset_circle = 55
def sort_circle(ele):
    return abs(ele[0][0] - last_point)

frame = None
ref_signal = 0

cv.namedWindow(windowName, cv.WINDOW_AUTOSIZE)
trackName = ['h','s','v','H','S','V']

def onChange(x):
    pass

cv.createTrackbar(trackName[0],windowName,0,180,onChange)
cv.createTrackbar(trackName[1],windowName,0,255,onChange)
cv.createTrackbar(trackName[2],windowName,0,255,onChange)
cv.createTrackbar(trackName[3],windowName,0,180,onChange)
cv.createTrackbar(trackName[4],windowName,0,255,onChange)
cv.createTrackbar(trackName[5],windowName,0,255,onChange)

cap = cv.VideoCapture("output.mp4")
ret, frame = cap.read()

stateMachine = "run"
with open("path_cmd.txt", "r") as pathfile:
    while True:
        # frame = cv.resize(frame,(160,120))
        # if frame is None:
        #     continue
        if True:
            # ser.lock.acquire()
            ff = frame.copy()
            # ser.lock.release()
            # ff = cv.GaussianBlur(ff,(3,3), 9)
            img = cv.cvtColor(ff,cv.COLOR_BGR2HSV)
            h=cv.getTrackbarPos('h',windowName)
            s=cv.getTrackbarPos('s',windowName)
            v=cv.getTrackbarPos('v',windowName)
            H=cv.getTrackbarPos('H',windowName)
            S=cv.getTrackbarPos('S',windowName)
            V=cv.getTrackbarPos('V',windowName)
            img = cv.inRange(img, (h,s,v),(H,S,V)) # EDIT: environment light
            bt_im = img[55:64 , 0:159]
            cnts = cv.findContours(bt_im.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)[0]
            img = cv.cvtColor(img,cv.COLOR_GRAY2BGR)
            if len(cnts) > 0:
                cir = []
                for c in cnts:
                    cir.append(cv.minEnclosingCircle(c))
                if stateMachine == "run":
                    if len(cir) == 1:
                        ((x,y),r) = cir[0]
                        last_point = int(x)
                        cv.circle(img, (int(x),int(y) + offset_circle) , int(r), (0,255,0), 2)
                        print((int(x),int(r)), end="\t")
                        if r > R_Standard[0] and r < R_Standard[1]:
                            pass
                        elif r > R_Standard[1]:
                            stateMachine = "big"
                        else:
                            pass
                    else:
                        cir.sort(key=sort_circle)
                        num = 0
                        for c in cir: # 做最近排序
                            ((x,y),r) = c
                            if num == 0:
                                cv.circle(img, (int(x),int(y) + offset_circle) , int(r), (0,255,0), 2)
                                last_point = int(x)
                            else:
                                cv.circle(img, (int(x),int(y) + offset_circle) , int(r), (255,0,0), 2)
                            print((int(x),int(r)), end="\t")
                            num += 1
                            if r >= R_Standard[0] and r <= R_Standard[1]:
                                pass
                            elif  r > R_Standard[1] and num == 0: # may facing chose problem or big turning
                                stateMachine = "big" # ERR: 应该先做最近点判断
                            else:
                                pass
                    print()

                elif stateMachine == "big":
                    if len(cir) == 1:
                        ((x,y),r) = cir[0]
                        last_point = int(x)
                        cv.circle(img, (int(x),int(y) + offset_circle) , int(r), (0,255,255), 2)
                        print((int(x),int(r)), end="\t")
                        if r < R_Standard[1]:
                            stateMachine = "run"
                        else:
                            pass
                    else:
                        x = []
                        y = []
                        r = []
                        cont_valid_r = 0
                        for c in cir:
                            ((xx,yy),rr) = c
                            x.append(int(xx))
                            y.append(int(yy))
                            r.append(int(rr))
                            if rr >= R_Standard[0] and rr <= R_Standard[1]:
                                cont_valid_r += 1
                            else:
                                pass
                        for i in range(len(x)):
                            print((x[i], r[i]), end="\t")
                            cv.circle(img, (x[i], y[i] + offset_circle), r[i], (255,0,0), 2)
                        print("valid radio: "+ str(cont_valid_r))
                        if cont_valid_r > 1:
                            x.sort(reverse=False)
                            cho_ese_line = x
                            stateMachine = "cho"
                    print()
                elif stateMachine == "cho":
                    cho = pathfile.readline()
                    if cho != None and cho != '':
                        print(cho)
                        cho = int(cho)
                        print(cho_ese_line)
                        last_point = cho_ese_line[cho-1]
                        print("cho : %d"%cho)
                    stateMachine = "run"
            img = cv.rectangle(img, (0,55), (159,64),(0,0,255),1)
            ff =  cv.rectangle(ff , (0,55), (159,64),(0,0,255),1)
            img = cv.rectangle(img, (80,59), (last_point,61),(255,0,255),1)
            ff = cv.putText(ff,str(total_frames),(0,12), cv.FONT_HERSHEY_COMPLEX, 0.6 , color=(0,0,255))
            ff = cv.putText(ff,stateMachine,(0,24), cv.FONT_HERSHEY_COMPLEX, 0.6 , color=(0,0,255))

            tos = np.hstack([ff,img])
            cv.imshow(windowName, tos)
            key = cv.waitKey(1)

            if key > 0:
                if key == ord('q'):
                    Send_Direction(0 , 0)
                    cv.destroyAllWindows()
                    break
                elif key == ord('s'):
                    cv.imwrite("AB.jpg",frame)
                speed = 600 - abs(last_point-80)*3
                if speed < 4:
                    speed = 4
                if last_point < 80:
                    Send_Direction(speed ,600)
                elif last_point > 80:
                    Send_Direction(600 ,speed)
                else:
                    Send_Direction(600 ,600)
                ret, frame = cap.read()
                total_frames += 1



        