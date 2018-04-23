# very simple python GUI for ADDS simulation (used by add3.py)
# read status file: set slider to show que length (1st status param)
#                   print max sample amplitude    (2nd status param)
# write control file: 1st control param is level threshold for 8 bit VAD
#                     2nd control param is percentage Tx time
# Note that setting level threshold to 0 will cause add3.py to terminate

# billcowley42@gmail.com,  v0.1 april 2018


from Tkinter import *
import os, time

root = Tk()
sv   = StringVar()

thres = 10; txTime = 50; queLen = 1; maxSam = 0  # initial values 

def myloop():
    
    # controls ..
    txTime = int(stx.get())
    thres = int(sthres.get())
    writeCon(thres, txTime)

    # status
    (queLen, maxSam) = readStat()
    sque.set(queLen)
    if maxSam>0:
        sv.set(str(maxSam))
    root.after(100, myloop)    # run at 100 msec intervals 

# for simplicity: use text files for status and control 
def readStat():
    try: 
        fs = open('adds_stat.txt')
        sr1 = fs.read(); sr2 = sr1.split()
        queLen = int(sr2[0])
        maxSam = int(sr2[1])
        fs.close()
    except:
        maxSam = -1
        queLen = 0
        sv.set("read error")
    return (queLen, maxSam)

def writeCon(thres, txTime): 
        fs = open('adds_cont.txt','w')
        fs.write(str(thres)+'\n')
        fs.write(str(txTime)+'\n')        
        fs.close()
        
    
w = Label(root, text="ADDS Control v0.1")
w.pack()

#controls ... 
stx = Scale(root,  borderwidth=5, label = "Tx%",
            from_=0, to=100, orient=HORIZONTAL)
stx.pack()
stx.pack()
stx.set(txTime) 
sthres = Scale(root,  borderwidth=5, label = 'Level Thres',
               from_=0, to=100, orient=HORIZONTAL)
sthres.pack()
sthres.set(15)

# status indicators
ws = Label(root, text="ADDS Status ")
ws.pack()
sque = Scale(root, label = 'Qlen', from_=0, to=100, orient=HORIZONTAL)
sque.pack()
wm = Label(root, text="Max sample: ")
wm.pack(side=LEFT)
e1 = Entry(root, width=10, textvariable = sv)
e1.pack(side=LEFT)
sv.set("0")

myloop()
root.mainloop()
