from socket import *
import json
import time
import serial
import binascii
import pygame
import time

# ser = serial.Serial("/dev/ttyTHS1", 9600)

addr = ("192.168.1.101", 3334)
cli = socket(AF_INET, SOCK_DGRAM)

def chazhi(in_num,in_max=1.0000,d_num=0.0001,out_max=255.0):
    in_num = float(in_num)
    in_max = float(in_max)
    d_num = float(d_num)
    out_max = float(out_max)
    retn = (in_max/d_num)
    # print(retn) 
    retn = (out_max/retn)
    # print(retn)
    retn = retn *in_num
    # print(retn)
    retn = int(retn)
    # print(retn)
    return retn

def _up_(num):
    # print ("_up_  : "+str(num))
    return
def _down_(num):
    # print ("_down_  : "+str(num))
    return
def _left_(num):
    # print ("_left_  : "+str(num))
    return
def _right_(num):
    # print ("_right_  : "+str(num))
    return


pygame.init()
pygame.joystick.init()
clock = pygame.time.Clock()
joystick_count = pygame.joystick.get_count()
# print(joystick_count)
joystick = pygame.joystick.Joystick(0)
joystick.init()
name = joystick.get_name()
# print(name)
t = time.time()
x = 0
y = 0
axoffset = joystick.get_axis(2)
ayoffset = joystick.get_axis(1)
while True:
    if time.time() - t > 0.030:
        def p(s):
            if s < 0:
                return -int(52*(-s/6)**(0.5))
            else:
                return int(52*(s/6)**(0.5))
        Y = p(y*350)
        def c(s):
            T = abs(s)**(1.5)
            if s<0 and T > 0:
                T = -T
            return T
        X = int(150 * c(x))
        if Y < 0:
            X = -X
        dic = {"y":(Y - X),"x":(Y + X)}
        msg = json.dumps(dic)
        print(msg)
        cli.sendto(msg.encode('utf-8'), addr)
        t = time.time()
    for event_ in pygame.event.get():
            #Quit Event
            if event_.type == pygame.QUIT:
                done=True
            elif event_.type == pygame.JOYBUTTONDOWN or event_.type == pygame.JOYBUTTONUP:
                buttons = joystick.get_numbuttons()
                for i in range(buttons):
                    button = joystick.get_button(i)
                    # print("button "+ str(i) + " : " + str(button))
                    if i == 0 and button == 1:
                        # print(1)
                        pass
                    elif i == 0 and button == 0:
                        # print(2)
                        pass
                    elif i == 1 and button == 1:
                        # print(3)
                        pass
                    elif i == 1 and button == 0:
                        # print(4)
                        pass
                    elif i == 3 and button == 1:
                        # print(5)
                        pass
                    elif i == 3 and button == 0:
                        # print(6)
                        pass
                    elif i == 4 and button == 1:
                        # print(7)
                        pass
                    elif i == 4 and button == 0:
                        # print(8)
                        pass

                    elif i == 10 and button == 1:
                        # print(9)
                        pass
                    elif i == 10 and button == 0:
                        # print(10)
                        pass


                    elif i == 11 and button == 1:
                        # print(11)
                        pass
                    elif i == 11 and button == 0:
                        # print(12)
                        pass


                    elif i == 6 and button == 1:
                        # print(13)
                        pass
                    elif i == 6 and button == 0:
                        # print(14)
                        pass


                    elif i == 7 and button == 1:
                        # print(15)
                        pass
                    elif i == 7 and button == 0:
                        # print(16)
                        pass

                pass
            elif event_.type == pygame.JOYAXISMOTION :
                axes = joystick.get_numaxes()
                for i in range(axes):
                    axis = joystick.get_axis(i)
                    # if i == 4 and axis != -1:
                    #     BHLonClick(axis)
                    # pass
                    # if i == 5 and axis != -1:
                    #     BHRonClick(axis)
                    # pass
                    if i == 1 and axis < 0:
                        _up_(chazhi(axis))
                    elif i == 1 and axis > 0:
                        _down_(chazhi(axis))




                    elif i == 0 and axis < 0:
                        _left_(chazhi(axis))
                    elif i == 0 and axis > 0:
                        _right_(chazhi(axis))


                    elif i == 0 and axis == 0:
                        pass


                    # print ("axis "+str(i) + ": "+str(axis))
                    
                    if i == 2:
                        x = (axoffset-axis)
                    elif i == 1:
                        y = (ayoffset-axis)
                    pass
            # elif event_.type == pygame.JOYHATMOTION:
            #     hats = joystick.get_numhats()
            #     for i in range(hats):
            #         hat = joystick.get_hat(i)
            #         if(hat == (0,0)):
            #             stop()
            #         elif(hat == (0,1)):
            #             forward(128)
            #             pass
            #         elif hat == (0,-1):
            #             backoff(128)
            #             pass
            #         elif hat == (-1,0):
            #             groundleftrun(100)
            #             pass
            #         elif hat == (1,0):
            #             groundrightrun(100)
            #             pass
            #         pass

            #         print("hat "+str(i)+ ": "+str(hat))
            #         print(hat)
            #         pass
            #     pass
            # pass
# while True:
#     dic = {"y":8,"x":2}
#     msg = json.dumps(dic)
#     cli.sendto(msg.encode('utf-8'), addr)
#     time.sleep(0.1)