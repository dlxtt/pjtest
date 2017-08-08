#!/usr/bin/python3
# import socket
from socketserver import ThreadingTCPServer,StreamRequestHandler
import threading
import time
import json

#命令通道
class cmdSocketServer(StreamRequestHandler):
    def handle(self):
        self.m_pp = protoProcesser(self)
        self.m_pp.dataProcess()


#辅助通道
class holeSocketServer(StreamRequestHandler):
    def handle(self):
        self.m_pp = protoProcesser(self)
        self.m_pp.dataProcess()

cmd_ip_port = ('0.0.0.0', 1231)
hole_ip_port = ('0.0.0.0', 6751)

#用户信息列表
userlist = {}

#协议综合处理
class protoProcesser():
    # m_srh = ('',0)
    def __init__(self,srh):


        self.m_srh = srh
        self.m_peer = self.m_srh.request.getpeername()
        self.addr = self.m_peer[0]
        self.port = self.m_peer[1]
        print("client address: %s %d" % (self.addr,self.port))

    def dataProcess(self):
        cmdgroup = {'PACKET_TYPE_INVALID': self.doUnknow,
                    'PACKET_TYPE_NEW_USER_LOGIN': self.doNewLogin,          # 服务器收到新的客户端登录，将登录信息发送给其他客户端
                    'PACKET_TYPE_WELCOME': self.doLoginRet,                 # 客户端登录时服务器发送该欢迎信息给客户端，以告知客户端登录成功
                    'PACKET_TYPE_REQUEST_CONN_CLIENT': self.doConnClient,   # 某客户端向服务器申请，要求与另一个客户端建立直接的TCP连接，即需要进行TCP打洞
                    'PACKET_TYPE_REQUEST_MAKE_HOLE': self.doMakeHole,       # 服务器请求某客户端向另一客户端进行TCP打洞，即向另一客户端指定的外部IP和端口号进行connect尝试
                    'PACKET_TYPE_REQUEST_DISCONNECT': self.doDisconnect,    #请求服务器断开连接
                    'PACKET_TYPE_TCP_DIRECT_CONNECT': self.doDirectConn,    # 服务器要求主动端（客户端A）直接连接被动端（客户端B）的外部IP和端口号
                    'PACKET_TYPE_HOLE_LISTEN_READY': self.doListenReady,    # 被动端（客户端B）打洞和侦听均已准备就绪
                    'PACKET_TYPE_Logon': self.doLogon,
                    'PACKET_TYPE_UserList': self.doListenReady
                    }

        keepalive = True
        while keepalive:
            data = str(self.m_srh.rfile.readline(),'utf-8').strip("\r\n")
            print(data)

            try:
                keepalive = cmdgroup.get(data)()
            except:
                print("unknow command")
                keepalive = False

    def doDisconnect(self):
        return False

    def doUnknow(self):
        return False

    # PORT1
    def doNewLogin(self):
        try:
            # 记录socket和端口
            userInfo = {'cmdstream':self.m_srh,'cmdport':self.port}
            userlist[self.addr] = userInfo

            self.m_srh.wfile.write(b'PACKET_TYPE_WELCOME')
        except:
            print("do New Login Error")
        return True

    def doLoginRet(self):
        pass
    # PORT2 客户端发起主动连接请求
    def doConnClient(self):
        # 第二行为IP地址
        toaddr = str(self.m_srh.rfile.readline(), 'utf-8').strip("\r\n")

        #先记录打洞信息
        userInfo = userlist[self.addr];
        userInfo['holestream']=self.m_srh
        userInfo['holeport']=self.port
        userInfo['toaddr'] = toaddr

        #PORT1 发起打动请求
        destInfo = userlist[toaddr]
        destInfo['toaddr'] = self.addr
        destInfo['toport'] = self.port

        destInfo['cmdstream'].wfile.write(b'')
        return True

    def doMakeHole(self):
        pass

    def doDirectConn(self):
        pass

    def doListenReady(self):
        pass

    def doLogon(self):
        pass

    def doListenReady(self):
        pass

def tRun(tts):
    tts.serve_forever()

if __name__ == "__main__":
    # 两个监听服务
    cmdserver = ThreadingTCPServer(cmd_ip_port, cmdSocketServer)
    holeserver = ThreadingTCPServer(hole_ip_port, holeSocketServer)

    # 线程方式启动
    threads = []
    t1 = threading.Thread(target=tRun, args=(cmdserver,))
    threads.append(t1)
    t2 = threading.Thread(target=tRun, args=(holeserver,))
    threads.append(t2)

    for t in threads:
        t.setDaemon(True)
        t.start()

    # 挂死
    while True:
        time.sleep(5)

