from PID import PID
import matplotlib.pyplot as plt

pid = PID(0.2,0.1,0)
x  = []
y = []
for i in range(1000):
    x.append(i)

t = 0
for i in x:
    pid.update(t - 100)
    t += pid.output / 10
    y.append(pid.output)

plt.plot(x,y)
plt.show()