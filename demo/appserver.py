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
def recvdata_thread(recvsock):
    global is_stop
    client = pyudt_socket(udtsock=recvsock)
    size = 100000
    data = create_string_buffer('\000'*size)
    
    while  not is_stop:
        ssize = 0
        while ssize < size:
            pbuf = c_char_p()
            pbuf.value = data[ssize:size]
            ss = client.recv(pbuf,size-ssize)
            if ss == 0:
                print "recv failed.\n"
                break
            ssize += ss
        if ssize < size:
            break
    
    client.close()
    print "recvdata thread exit.\n"
def accept_thread():
    service= create_string_buffer("9000")
    server = pyudt_socket()
    
    rc = server.bind(create_string_buffer(""),service)
    if rc < 0:
        print "bind to %s failed.\n"%service.value
        server.close()
        sys.exit(1)
    else:
        print "bind to %s sucess.\n"%service.value
    
    rc = server.listen(10)
    if rc < 0:
        print "listen failed.\n"
        server.close()
        sys.exit(1)
    else:
        print "listen success.\n"
    
    addr = sockaddr()
    length = c_int()
    length.value=0
    while not is_stop:
        #paddr = pointer(sockaddr())
        #paddr.value = addr
        
        recv = server.accept(byref(addr),byref(length))
        if recv < 0:
            print "accept failed. quit.\n"
            server.close()
            sys.exit(1)
        else:
            host = create_string_buffer('\000'*1024)
            hostlen = 1024
            serv = create_string_buffer('\000'*1024)
            servlen = 1024
            print "add.sa_data=%s addrlen=%d"%(addr.sa_data,length.value)
            server.getnameinfo(byref(addr),length,host,hostlen,serv,servlen)
            print "accept success. host=%s, port=%s\n"%(host.value,serv.value)
        recvdata = threading.Thread(target=recvdata_thread,name="recvdata thread",args=[recv])
        recvdata.dameon = True
        recvdata.start()
    server.close()
if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    accept = threading.Thread(target=accept_thread,name="accept thread")
    accept.daemon = True
    accept.start()
    
    while not is_stop:
        time.sleep(1)
    accept.join()
    sys.exit(0)
