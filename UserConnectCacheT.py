#!/usr/bin/env python# -*- coding: utf-8 -*-import threadingimport Queueimport structimport QueueObjsimport erroflogfrom QueueManger import QueueManger# // TCP 数据包头 16 bit# // 网关与客户的交互# typedef struct tag_msghead_t {#     unsigned short     len;    // 数据体长度 H#     unsigned short  cmd;    // 协议号 H#     unsigned short     eno;    // 错误码 H#     unsigned char     enc;    // 加密 B#     unsigned char     com;    // 压缩 B#     unsigned int     tea;    // 会话 I#     unsigned int     idx;    // 包索引 I# }T_MSGHEAD_T, *LP_MSGHEAD_T;class T_MSGHEAD_T():    def __init__(self):        self.len = 0        self.cmd = 0        self.eno = 0        self.enc = 0        self.com = 0        self.tea = 0        self.idx = 0    def setLen(self,plen):        self.len = plen    def setCmd(self,pcmd):        self.cmd = pcmd    def setEno(self,peno):        self.eno = peno    def setEnc(self,penc):        self.enc = penc    def setCom(self,pcom):        self.com = pcom    def setTea(self,ptea):        self.tea = ptea    def setIdx(self,pidx):        self.idx = pidx    def setDatWithStruct(self,strdat):        #print len(strdat)        self.len,self.cmd,self.eno,self.enc,self.com,self.tea,self.idx=struct.unpack('HHHBBII',strdat)    def showDatStrTest(self):        tmpstr = "%d,%d,%d,%d,%d,%d,%d"%(self.len,self.cmd,self.eno,self.enc,self.com,self.tea,self.idx)        print tmpstr    def showHexDat(self):        print repr(self.getStructDat())    def getStructDat(self):        strtmp=struct.pack('HHHBBII',self.len,self.cmd,self.eno,self.enc,self.com,self.tea,self.idx)        return strtmpclass UserConnectCacheT(threading.Thread):    def __init__(self,t_name,threadmangert):        threading.Thread.__init__(self, name=t_name)         self.threadmangert = threadmangert        self.queuemagert = QueueManger.GetInstance()        self.mainThreadName = self.threadmangert.mainThreadName        self.queueRequest = Queue.Queue(5000)                            #接收来自客户端的连接        self.queuemagert.saveThreadMailQueueWithName(t_name, self.queueRequest)                      #注册接收邮箱        self.usersCacheQueues = {}                              #{cacheID:userCacheQueue}               #用户接收邮箱        self.accounts = {}                                      #{'account':token}                      #玩家token        self.tokens = {}                                        #{'token':cacheid}                      #token所在用户线程池        self.usersMangerRequestQueue = self.threadmangert.getUserMangerThreadQueue()    def receiveDataFromUserManger(self,userStatusObj):        #用户管理线程给客户端转发线程发来消息        userStatus = userStatusObj        if userStatus.dataType == 'login':#用户登陆，请求建立连接转发            if self.accounts.has_key(userStatus.account):                self.tokens.pop(self.accounts[userStatus.account])      #用户重新登陆，删除旧的token                self.accounts[userStatus.account] = userStatus.token                    self.tokens[userStatus.token] = userStatus.cID            else:                self.tokens[userStatus.token] = userStatus.cID                self.accounts[userStatus.account] = userStatus.token            uqueue = self.queuemagert.getThreadMailQueueWithName(userStatus.cID)            if uqueue == None:                print '错误:用户线程池与token绑定错误'            else:                self.usersCacheQueues[userStatus.cID] = uqueue        elif userStatus.dataType == 'loginout':#用户删除请法庭删除连接转发            pass    def decodeCliendData(self,clientConnectObj):        adata = clientConnectObj.data        dathandlerstr = adata[0:16]        dattmp = adata[16:]        handlertmp = T_MSGHEAD_T()        handlertmp.setDatWithStruct(dathandlerstr)        csocket = clientConnectObj.csocket        clientIP = clientConnectObj.IPaddr        if handlertmp.cmd > 11000:#游戏接口            self.sendDataToUserCacheT(dattmp, handlertmp, csocket,clientIP)        elif handlertmp.cmd < 11000:#服务器用户管理相关接口            self.sendDataToManger(dattmp, handlertmp, csocket,clientIP)    def sendDataToManger(self,datstr,handler,clientSocket,clientIP):        clientobj = QueueObjs.ClientObj(datstr,handler,clientSocket,clientIP)#dat,handler,dataType,csocket,ipAddr        queueobj = QueueObjs.QueueMangerObj(clientobj,QueueObjs.Flog_ClientObj,self.getName(),self.threadmangert.userMangerName,True)        self.usersMangerRequestQueue.put(queueobj)    def sendDataToUserCacheT(self,datstr,handler,clientSocket,clientIP):        clientobj = QueueObjs.ClientObj(datstr,handler,clientSocket,clientIP)        if self.tokens.has_key(handler.tea):            queueobj = QueueObjs.QueueMangerObj(clientobj,QueueObjs.Flog_ClientObj,self.getName(),self.tokens[handler.tea])            self.usersCacheQueues[self.tokens[handler.tea]].put(queueobj)        else:            handler.eno = erroflog.Erro_UserNoLogin            handler.len = 0            handler.enc = 0            handler.com = 0            clientSocket.send(handler.getStructDat())            print "用户token值不对%d"%(handler.tea)    def run(self):        while(True):            if not self.queueRequest.empty():                ququeobj = self.queueRequest.get_nowait()                if self.mainThreadName == ququeobj.fromTName:                   #接收到主服务器IO线程数据                    self.decodeCliendData(ququeobj.data)                elif ququeobj.fromTName == self.threadmangert.userMangerName:   #接收到用户管理器数据                    self.receiveDataFromUserManger(ququeobj.data)                                