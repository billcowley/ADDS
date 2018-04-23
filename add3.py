# simulations of ADDS using UDP sockets and pyaudio
# (see http://lowsnrblog.blogspot.com.au/2018/04/moving-away-from-press-to-talk.html)
#
# this version: able to act as client or server 
# USAGE:  'python add3 -s server_ipaddress_or_name'   (for server end)
# USAGE   'python add3 -c -s server_ipaddress_or_name'   (for client end)
# start client end first 
# bill  v0.1  april 2018 

# this version uses a separate GUI process (addgui) to set control
# variables and show some status indicators - start this first eg
# python addgui.py &
# to kill the add3 script: set the level threshold to 0

# this code assumes that the audio interfaces are already set eg for mic in,
# and headphones out.  Use alsamixer and pavucontrol to select suitable sound
# configurations and devices, then test and adjust input/output levels etc 

import pyaudio
import time
import socket
import sys, getopt
maxsam = 0


def main(argv):

    WIDTH = 1    # 8 bit samples
    CHANNELS = 1 # mono 
    RATE = 8000  # 8 kHz
    CHUNK = 1024 # samples per frame 
    thres = 10   # 10 sample threshold default
    tTime = 50   # % of time for Tx - use 50% default
    Tc = 3       # TDMA cycle time  (secs) 

    p = pyaudio.PyAudio()
    
    socout =[]
    socin = []
    mode = 'server'
    
    if len(sys.argv)<3:
        print 'add2 [c] -s server_ipaddress'
        sys.exit(2)
    
    try:
          opts, args = getopt.getopt(argv,"hcs:")
    except getopt.GetoptError:
          print 'add2 [c] -s server_ipaddress'
          sys.exit(2)
    for opt, arg in opts:
          if opt == '-h':
             print 'add2 [c] -s ipaddress'
             sys.exit()
          elif opt in ("-c"):
             mode='client'
          elif opt in ("-s",):
             server_id = arg
    print 'mode is ', mode
    print 'server address is ', server_id



    #audio input via callback 
    def in_callback(in_data, frame_count, time_info, status):
            global maxsam 
            max= 0
            for n in range(len(in_data)-1):
                    b0 = in_data[n]
                    c0 = abs(ord(b0) - 128)
                    if max<c0:
                        max = c0
            maxsam = max
            if maxsam>thres: 
                    socout.append(in_data)
            return (None, pyaudio.paContinue)

    # use callback for audio input  
    in_stream = p.open(format=p.get_format_from_width(WIDTH),
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer = CHUNK,
                    stream_callback=in_callback)

    # without callback for audio autput 
    out_stream = p.open(format=p.get_format_from_width(WIDTH),
                    channels=CHANNELS,
                    rate=RATE,
                    frames_per_buffer = CHUNK,
                    output=True)

    # Create a socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    #server_address = ('hereford2.local', 10000)
    server_address = (server_id,  10000)
    if mode=='server':
        print 'starting up on %s port %s' % server_address
        sock.bind(server_address)

    sock.setblocking(0)  # set non blocking 

    in_stream.start_stream()

    #  main loop .......................
    while (thres>0) and in_stream.is_active():
        try: 
          time.sleep(0.04)
          fs = open('adds_cont.txt')
          st1 = fs.read()
          st2 = st1.split()
          thres = int(st2[0])
          tTime = int(st2[1])        
          fs.close()
        except:
          print("adds_cont.txt read error ")
  
        if len(socout)>80:
                print  'long queue!' 

        rxdata=[] 
        try:
            rxdata, c_address = sock.recvfrom(CHUNK)
            # note that client address is unknown until packet rx 
        except:
            pass
        if len(rxdata)>0:  
            socin.append(rxdata)
            sys.stdout.write('R'); sys.stdout.flush()
            if len(rxdata)<CHUNK:
                print 'short data packet: ' + str(len(rxdata))
        

        if len(socin)>0:
            inblk = socin[0]
            del socin[0]
            out_stream.write(inblk) 

                
     
        # let server send in the first portion of frame; client sends in the latter part
        if mode=='server':
            TxTime = (int(time.time()*100/Tc)%100 < tTime)
        else:
            TxTime = (int(time.time()*100/Tc)%100 >(100-tTime))
            
        if TxTime and (len(socout)>0):   # send packets ?  

                outblk = socout[0]   # take the first block
                del socout[0]
                if mode=='client':
                    try:
                        sent = sock.sendto(outblk, server_address)
                        sys.stdout.write('S'); sys.stdout.flush()
                    except:
                        print 'send to server error'
                else:
                    try:
                        sent = sock.sendto(outblk, c_address)
                        sys.stdout.write('S'); sys.stdout.flush()
                    except:
                        print 'send to client error'
            
        fs = open('adds_stat.txt','w')
        queLen = len(socout)
        fs.write(str(queLen)+'\n')
        fs.write(str(maxsam)+'\n')
        fs.close()
         

    in_stream.stop_stream()
    in_stream.close()
    out_stream.stop_stream()
    out_stream.close()

    p.terminate()

if __name__ == "__main__":
   main(sys.argv[1:])
