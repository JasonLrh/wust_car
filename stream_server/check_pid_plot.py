
import matplotlib.pyplot as plt
from numpy import double

with open("pid_data.txt","r") as f:
    lines = f.readlines()
    err = []
    speed = []
    for l in lines:
        data = l.split(",")
        err.append(float(data[0]))
        speed.append(float(data[1]))
        
    

    plt.plot(err,"r")
    # plt.plot(speed,"b")
    plt.show()