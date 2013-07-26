from pyudt import *
import time
import threading
import signal

is_stop = False

def signal_handler(signal, frame):
    global is_stop
    is_stop = True
    print 'You pressed Ctrl+C!\n'
    sys.exit(0)
    
def monitor_thread(client):
    global is_stop
    print "SendRate(Mb/s)\tRTT(ms)\tCWnd\tPktSndPeriod(us)\tRecvACK\tRecvNAK\n"
    perf = traceinfo()
    while not is_stop:
        time.sleep(1)
        if client.perfmon(perf) < 0:
            print "perfmon error.\n"
            break
        print perf.mbpsSendRate,"\t\t", perf.msRTT,"\t",perf.pktCongestionWindow,"\t",perf.usPktSndPeriod,"\t\t\t",perf.pktRecvACK,"\t", perf.pktRecvNAK,"\n"
        
def send_thread():
    global is_stop
    server = create_string_buffer("192.168.28.226")
    port = create_string_buffer("9000")
    
    client = pyudt_socket()
    print "connect to %s %s\n"%(server.value,port.value)
    rc = client.connect(server,port)
    if rc < 0:
        print "connect to server failed.\n"
        client.close()
        sys.exit(1)
    else:
        print "connected to server. ready to send data.\n"
    
    mon = threading.Thread(target=monitor_thread,name="mointor thread",args=[client])
    mon.dameon = True
    mon.start()
    
    size = 100000
    
    data = create_string_buffer('a'*size)
    
    for i in range(10000):
        if is_stop:
            break
        ssize = 0
        while ssize < size:
            pbuf = c_char_p()
            pbuf.value = data[ssize:size]
            ss = client.send(pbuf,size - ssize)
            if ss < 0:
                print "send error.quit \n"
                sys.exit(1)
            ssize += ss
        #print "send %d bytes to server\n"%ssize
        if ssize < size:
            break

    client.close()
        
if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    send = threading.Thread(target=send_thread,name="send thread")
    send.daemon = True
    send.start()
    
    while not is_stop:
        time.sleep(1)
    send.join()
    sys.exit(0)
