from ctypes import *
import sys
import os
import inspect

AF_INET = 2
SOCK_STREAM = 1

def get_libpath():
    caller_file = inspect.stack()[1][1]         # caller's filename
    return os.path.join(os.path.abspath(os.path.dirname(caller_file)),"udtc.dll")
class sockaddr(Structure):
    _fields_ = [("sa_family",c_uint16),
               ("sa_data",c_char*14)]
class traceinfo(Structure):
    _fields_ = [("msTimeStamp",c_longlong),
                ("pktSentTotal",c_longlong),
                ("pktRecvTotal",c_longlong),
                ("pktSndLossTotal",c_int),
                ("pktRcvLossTotal",c_int),
                ("pktRetransTotal",c_int),
                ("pktSentACKTotal",c_int),
                ("pktRecvACKTotal",c_int),
                ("pktSentNAKTotal",c_int),
                ("pktRecvNAKTotal",c_int),
                ("usSndDurationTotal",c_longlong),
                ("pktSent",c_longlong),
                ("pktRecv",c_longlong),
                ("pktSndLoss",c_int),
                ("pktRcvLoss",c_int),
                ("pktRetrans",c_int),
                ("pktSentACK",c_int),
                ("pktRecvACK",c_int),
                ("pktSentNAK",c_int),
                ("pktRecvNAK",c_int),
                ("mbpsSendRate",c_double),
                ("mbpsRecvRate",c_double),
                ("usSndDuration",c_longlong),
                ("usPktSndPeriod",c_double),
                ("pktFlowWindow",c_int),
                ("pktCongestionWindow",c_int),
                ("pktFlightSize",c_int),
                ("msRTT",c_double),
                ("mbpsBandwidth",c_double),
                ("byteAvailSndBuf",c_int),
                ("byteAvailRcvBuf",c_int)]
    
class pyudt_socket:
    def __init__(self,af=AF_INET,type=SOCK_STREAM,flags=0,udtsock=-1):
        self.libpath = get_libpath()
        self.udtlib = CDLL(self.libpath)
        if udtsock <0:
            self.sock = self.udtlib.udt_socket(c_int(af),c_int(type),c_int(flags))
            if self.sock < 0:
                print "create udt socket failed\n"
                sys.exit(1)
        else:
            self.sock = udtsock
        #startup udt
        self.udtlib.udt_startup()
    def __del__(self):
        if self.udtlib != None:
            self.udtlib.udt_close(c_int(self.sock))
    
    def bind(self,host,port):
        
        return self.udtlib.udt_py_bind(c_int(self.sock),host,port)
        
    def bind2(self,udpsock):
        return self.udtlib.udt_bind2(c_int(self.sock),c_int(udpsock))
    
    def connect(self,host,port):
        #phost = c_char_p()
        #phost.value = host
        #pport = c_char_p()
        #pport.value = port
        #print "connect host=%s, port=%s\n"%(phost.value,port)
        return self.udtlib.udt_py_connect(c_int(self.sock),host,port)
    
    def listen(self, i):
        return self.udtlib.udt_listen(c_int(self.sock),c_int(i))
    def accept(self,addr,len):
                
        return self.udtlib.udt_accept(c_int(self.sock),addr,len)
        
    def getnameinfo(self,addr,addrlen,host,hostlen,serv,servlen):
        
        return self.udtlib.udt_getnameinfo(addr,addrlen,host,c_int(hostlen),serv,c_int(servlen))
        
    def recv(self,buf,len):
                
        return self.udtlib.udt_recv(c_int(self.sock),buf,len,0)
        
    def send(self,buf,len):
        
        return self.udtlib.udt_send(c_int(self.sock),buf,c_int(len),0)
        
    def recvmsg(self,buf,len):
        
        return self.udtlib.udt_recvmsg(c_int(self.sock),buf,len)
        
    def sendmsg(self,buf,len,ttl,inorder):
        
        return self.udtlib.udt_sendmsg(c_int(self.sock),buf,c_int(len),c_int(ttl),c_int(inorder))
        
    def set_rendezvous(self,flag):
        
        return self.udtlib.udt_set_rendezvous(c_int(self.sock),c_bool(flag))
        
    def close(self):
        self.udtlib.udt_close(c_int(self.sock))
        self.udtlib = None
    def perfmon(self,traceinfo):
        return self.udtlib.udt_perfmon(c_int(self.sock),byref(traceinfo),0)

