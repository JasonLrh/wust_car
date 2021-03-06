import cv2 as cv
import numpy as np
import json
from Server import Server
from socket import *
from PID import PID
import math
from time import sleep

R_Standard = (20,50) # EDIT: lineWidth
addr = ("192.168.200.32", 3334)
windowName = "WUSTCarImageService"

cli = socket(AF_INET, SOCK_DGRAM)
def Send_Direction(y:int,x:int):
    dic = {"y":y,"x":x}
    msg = json.dumps(dic)
    if True:
        cli.sendto(msg.encode('utf-8'), addr)

total_frames = 0


# fore = cv.VideoWriter_fourcc(*'XVID')
# out = cv.VideoWriter('output.mp4', fore , 30, (160, 120))

last_point = 0
def sort_circle(ele):
    return abs(ele[0][0] - last_point)

frame = None
ref_signal = 0
pid = PID(120, 0, 0)
def callback(msg):
    global frame,ref_signal
    image = np.asarray_chkfinite(bytearray(msg), dtype="uint8")
    frame = cv.imdecode(image, cv.IMREAD_COLOR)
    # frame = cv.resize(frame,(160,120))
    frame = cv.flip(frame,0)
    frame = cv.flip(frame,1)
    # frame = cv.medianBlur(frame, 21)
    # frame = cv.erode(frame, (-1, -1))
    ref_signal = 1

ser = Server(callback,3333)
ser.start()

def USM(src_img):
    blur_img = cv.GaussianBlur(src_img, (5, 5), 30)
    usm = cv.addWeighted(src_img, 1.5, blur_img, -0.5, 0)
    return usm

cv.namedWindow(windowName, cv.WINDOW_AUTOSIZE)

# pi_output = 0.0                             # 积分输出
# pid_Kp = 2                                  # 比例系数
# pid_Ki = 0.001                                  # 积分系数

stateMachine = "run"
pid_data_file = open("pid_data.txt","w")
with open("path_cmd.txt", "r") as pathfile:
    while True:
        if frame is None:
            continue
        if ref_signal == 1:
            ser.lock.acquire()
            ff = frame.copy()
            ser.lock.release()
            # out.write(ff)
            # img = cv.cvtColor(ff,cv.COLOR_BGR2HSV)
            raw = ff.copy()
            img = ff.copy()
            img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            img = cv.medianBlur(img,35)
            img = USM(img)
            ret , img = cv.threshold(img, 102, 255, cv.THRESH_BINARY)
            np.bitwise_not(img,img)
            # img = cv.inRange(img,(0, 0, 0), (180, 255, 141)) # EDIT: environment light
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
                        cv.circle(img, (int(x),int(y) + 60) , int(r), (0,255,0), 2)
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
                                cv.circle(img, (int(x),int(y) + 60) , int(r), (0,255,0), 2)
                                last_point = int(x)
                            else:
                                cv.circle(img, (int(x),int(y) + 60) , int(r), (255,0,0), 2)
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
                        cv.circle(img, (int(x),int(y) + 60) , int(r), (0,255,255), 2)
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
                            cv.circle(img, (x[i], y[i] + 60), r[i], (255,0,0), 2)
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
            sha = (tos.shape[1]*3, tos.shape[0]*3)
            tos = cv.resize(tos,sha)
            cv.imshow(windowName, tos)
            key = cv.waitKey(20)
            if key == ord('q'):
                Send_Direction(0 , 0)
                cv.destroyAllWindows()
                pid_data_file.close()
                Send_Direction(0 , 0)
                sleep(0.020)
                Send_Direction(0 , 0)
                sleep(0.020)
                Send_Direction(0 , 0)
        
                # out.release()
                break
            else:
                if key == ord("s"):
                    cv.imwrite("out_img/"+str(total_frames)+".jpg", raw)
                    total_frames += 1

                target_val  = 0
                input_val = math.atan((last_point - 80) / 71.0)
                print('input => ', last_point, ' ---> ', input_val)
                error = target_val - input_val

                pid.update(error)
                dir = pid.output
                # pi_cur_output = pid_Ki * error
                # pi_output = pid_Kp * error + pi_cur_output

                # pi_output += pi_cur_output         # 积分累计

                # dir = - pi_output

                pid_data_file.write(str(error)+","+str(dir)+"\n")
                # pid.update(last_point-80)
                # diff = pid.output
                basic_s = 150
                # speed = abs(diff)*4
                if dir < 0:
                    Send_Direction(basic_s + dir ,basic_s)
                elif dir > 0:
                    Send_Direction(basic_s ,basic_s - dir)
                else:
                    Send_Direction(basic_s ,basic_s)

                

            # total_frames += 1

        