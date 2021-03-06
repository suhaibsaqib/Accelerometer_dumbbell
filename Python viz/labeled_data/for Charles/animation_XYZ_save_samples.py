from __future__ import division
import serial
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pickle
from os import path
import csv

exerciseType="standing_calf"
filename=path.join("labeled_data",exerciseType)
samples=[]
def data_gen():
    global samples
    t = data_gen.t
    cnt = 0
    while cnt < 500: # limit the time to 25 secs
        cnt+=1
        t += 0.05
        try:
            x,y,z=get_data_from_serial()
        except:
            x,y,z =0,0,0
        # print y
        if y!= None: 
            data =t,x,y,z 
            samples.append(data)
            yield data
    #save to file for later analysis.
    pickle.dump(samples,open(filename+".p","wb"))
    toCSV(filename+".p")
    print "done"
    # else: yield data_gen()

def toCSV(picklefile):
    global exerciseType
    now =time.asctime()[4:-5]

    with open("labeled_data/"+now+"_"+exerciseType+".csv","wb") as csvFile:
        data=pickle.load(open(picklefile))
        writer=csv.writer(csvFile)
        writer.writerow(["t (sec)","x","y","z"]) #header
        for i in data:
            writer.writerow(list(i))

data_gen.t = 0

fig, ax = plt.subplots()
lineX, = ax.plot([], [],"r-", lw=2)
lineY, = ax.plot([], [],"g-", lw=2)
lineZ, = ax.plot([], [],"b-", lw=2)

ax.set_ylim(-1.1, 1.1)
ax.set_xlim(0, 10)
ax.grid()
ax.set_xlabel('time (s)')
ax.set_ylabel('acceleration (g)')
tdata, xdata, ydata, zdata = [], [],[],[]
def run(data):
    # update the data
    t,x,y,z = data
    tdata.append(t)
    ydata.append(y)
    xdata.append(x)
    zdata.append(z)
    xmin, xmax = ax.get_xlim()

    if t >= xmax-1: #once the line get's halfway...
        #move the window by 1/20th of a second forward
        xmin+=5
        xmax+=5 
        ax.set_xlim(xmin, xmax)
        ax.figure.canvas.draw()
    lineX.set_data(tdata, xdata)
    lineY.set_data(tdata, ydata)
    lineZ.set_data(tdata, zdata)
    return lineX,lineY,lineZ

ser = serial.Serial('/dev/tty.usbmodem1421', 9600)
def get_data_from_serial():
    s=ser.readline()
    print s
    s=s.split(",")
    if len(s)!=3:
        return None
    for i in range(len(s)):
        try:s[i]=float(s[i].strip())
        except: return None
    # print s
    x, y, z = s[0],s[1],s[2]
    return x,y,z

ani = animation.FuncAnimation(fig, run, data_gen, blit=False, interval=10,
    repeat=False)
plt.show()
ser.close()
