#!/usr/bin/env python# -*- coding: utf-8 -*-import threadingimport Queueimport Cmds_pb2import erroflogimport timeimport randomimport QueueObjsfrom QueueManger import QueueMangerimport askMysqlTypeRANDOMKEY = 0COUNT = 1RANDOMKEY = random.randrange(0,0x0ffffffff) #使用随机数可以使用每次服务器重启后生成的token不同class UserMangerT(threading.Thread):    def __init__(self,t_name,threadmangert):        threading.Thread.__init__(self, name=t_name)         self.threadmangert = threadmangert        self.queuemangert = QueueManger.GetInstance()        self.queueReauest = Queue.Queue(5000)        self.queuemangert.saveThreadMailQueueWithName(t_name, self.queueReauest)        self.cacheQueueRequest = self.queuemangert.getThreadMailQueueWithName(self.threadmangert.connectThreadName)        self.connectCacheName = self.threadmangert.connectThreadName        #登陆token保存socket        self.tokenClient = {}                #UserCache        self.mysqlUnUsedQueues = {}        #mysql        self.mysqlIndex = 100                               #mysql请求编号,从100号开始，100号以下的留给用户管理器器自已用,1:获取服务器列表        #获取mysql线程请求列队        mysqlqueue,mysqlThreadName = self.threadmangert.getCanUseMysqlThreadForOther(self.getName()) #mysql数据请求，需要时再请求，不用时马上释放连接,所以这里不作请求#mysql请求线程名                                     if mysqlqueue == None or mysqlThreadName == None:            print '错误:mysql线程请求错误,UserMangerT未请求到可用Mysql连接线程(UserMangerT)'        self.mysqlUnUsedQueues[mysqlThreadName] = mysqlqueue       #已请求到的未使用的mysql连接        self.mysqlUsedQueues = {}                                   #正在使用的mysql连接        self.mysqlRequests = {}                                     #mysql请求编号        print 'usermanger run'        #Users        self.UserCacheQueues = {}               #{account,queue}保存用户线程邮箱        self.CidCacheQueues = {}                #{cid:queue}缓存名保存的列队        self.userTokens = {}                    #{token:account},通过玩家token保存玩家帐号        self.userLoginAccounts = {}             #{account:[token,usercahceID]},通过帐号保存token和缓存名        #初始化时，初始化好服务器列表        self.serverlist = []        self._getServerList()        self.usercacheIndex = 1                 #用户线程池从1开始    def getToken(self):        t = int(time.time())        global RANDOMKEY        global COUNT        global RANDOMKEY        tmp = t        if RANDOMKEY == t:            COUNT += 1            tmp =t*100000 + COUNT        elif RANDOMKEY == 0 or RANDOMKEY != t:            COUNT = 0            RANDOMKEY = t            tmp = t*100000        tmp = tmp ^ RANDOMKEY        tmp = int(str(tmp)[-9:])        return tmp    def _getServerList(self):        dat = "SELECT * FROM server.servertab_server;"                                   mysqlaskobj = QueueObjs.MysqlAskObj(1,dat,4)        if len(self.mysqlUnUsedQueues) > 0:            mysqlname,mysqlqueue = self.mysqlUnUsedQueues.popitem()            self.mysqlUsedQueues[mysqlname] = mysqlqueue            self.mysqlRequests[1] = mysqlname                       #1.号获取服务器列表mysql请求编号,请的结果将会一直保存在用户管理列表中            queueobj = QueueObjs.QueueMangerObj(mysqlaskobj,QueueObjs.Flog_MysqlAskObj,self.getName(),mysqlname,True)            mysqlqueue.put(queueobj)            #mysqlqueue.put(copy.deepcopy(queueobj))        else:            mysqlname,mysqlqueue = self.threadmangert.getCanUseMysqlThreadForOther(self.getName())            if self.mysqlqueue == None or self.mysqlThreadName == None:                print '错误:mysql线程请求错误,UserMangerT未请求到可用Mysql连接线程(UserMangerT)'            else:                self.mysqlUsedQueues[mysqlname] = mysqlqueue                self.mysqlRequests[1] = mysqlname                queueobj = QueueObjs.QueueMangerObj(mysqlaskobj,QueueObjs.Flog_MysqlAskObj,self.getName(),mysqlname,True)                #mysqlqueue.put(copy.deepcopy(queueobj))                mysqlqueue.put(queueobj)    def _receiveServerListFromMysql(self,mysqlaskobj):        if mysqlaskobj.erro == 0:            serverlist = mysqlaskobj.data            for serv in serverlist:                self.serverlist.append({'id':serv[0],'type':serv[1],'ip':serv[2],'nip':serv[3],'port':serv[4],'name':str(serv[5].encode('utf8')),'time':serv[6],'status':serv[7]})            print serverlist        else:            print "get server list erro:%s"%(mysqlaskobj.erro)    def _getMysqlIndex(self):        tmp = self.mysqlIndex        self.mysqlIndex += 1        if self.mysqlIndex >= 0x0fffffff:            self.mysqlIndex = 100        return tmp    def receiveDataFromMysqlConnectT(self,msqlaskobj):        if msqlaskobj.askid == 1:            self._receiveServerListFromMysql(msqlaskobj)        elif self.mysqlRequests[msqlaskobj.askid] == 0:            self.mysqlRequests.pop(msqlaskobj.askid)        else:            self.receiveDataFromMysql(self.mysqlRequests[msqlaskobj.askid], msqlaskobj)    def receiveDataFromMysql(self,clientobj,mangersqlobj):        if clientobj == 0:            return        if clientobj.handler.cmd == 10001:            self.completeCmd10001(clientobj, mangersqlobj)        elif clientobj.handler.cmd == 10002:            self.completeCmd10002(clientobj, mangersqlobj)        elif clientobj.handler.cmd == 10003:            self.completeCmd10003(clientobj, mangersqlobj)        elif clientobj.handler.cmd == 10004:            self.completeCmd10004(clientobj, mangersqlobj)        elif clientobj.handler.cmd == 10005:            self.completeCmd10005(clientobj, mangersqlobj)        elif clientobj.handler.cmd == 10006:            self.completeCmd10006(clientobj, mangersqlobj)        elif clientobj.handler.cmd == 10007:            self.completeCmd10007(clientobj, mangersqlobj)        elif clientobj.handler.cmd == 10008:            self.completeCmd10008(clientobj, mangersqlobj)        elif clientobj.handler.cmd == 10009:            self.completeCmd10009(clientobj, mangersqlobj)    def completeCmd10001(self,clientobj,mangersqlobj):        if mangersqlobj.erro != 0:            clientobj.handler.len = 0            clientobj.handler.eno = mangersqlobj.erro            clientobj.handler.enc = 0            clientobj.handler.com = 0            if mangersqlobj.erro == 1062:                print '数据库主键重复，帐号已存在'            elif mangersqlobj.erro == 1366:                print '数据库写入字段数据类型不匹配'            try:                  clientobj.csocket.send(clientobj.handler.getStructDat())            except EOFError:                  print '10001注册成功返回客户端数据错误,错误情况:'                 print EOFError              except:                  print '10001注册成功返回客户端数据错误'        else:            #玩家注册成功，创建用户            registeracc = Cmds_pb2.RequestRegisterAccount()            registeracc.ParseFromString(clientobj.data)            self.createUserThread(registeracc.userAccount,clientobj)    #用户登陆,在游戏服务器中创建角色    def createUserThread(self,useraccount,clientobj):        #用户使用帐户名，密码，平台号登陆        queuerequest,cid = self.threadmangert.getCanUseUserCacheThreadTForUserMangerTWithUser(useraccount)        if cid == None or queuerequest == None:            print '服务器已满,用户线程池已满'            handlertmp = clientobj.handler            handlertmp.eno = erroflog.Erro_ServerNoSpace            handlertmp.len = 0            handlertmp.com = 0            handlertmp.enc = 0            try:                  clientobj.csocket.send(handlertmp.getStructDat())            except EOFError:                  print '10001用户创建错误时返回客户端数据错误,错误情况:'                 print EOFError              except:                  print '10001用户创建错误时返回客户端数据错误'        else:            #UserCache            ttoken = self.getToken()            clientobj.handler.tea = ttoken            self.UserCacheQueues[useraccount] = queuerequest                    #玩家所在缓存列队保存列队            self.CidCacheQueues[cid] = queuerequest            self.userTokens[ttoken] = useraccount                               #token保存帐号            self.userLoginAccounts[useraccount] = [ttoken,cid]      #帐号保存token和缓存名            self.tokenClient[ttoken] = clientobj            userobj = QueueObjs.UserObj(clientobj,'clientobj',useraccount) #dat,dataType,handler,account,csocket            queueobj = QueueObjs.QueueMangerObj(userobj,QueueObjs.Flog_UserObj,self.getName(),cid)            #queuerequest.put(copy.deepcopy(queueobj))            queuerequest.put(queueobj)    def completeCmd10002(self,clientobj,mangersqlobj):        askData = mangersqlobj.data        useraccount = askData[0][0]        pwsql = askData[0][3]        pdata = Cmds_pb2.RequestLoginByAccount()        pdata.ParseFromString(clientobj.data)        if useraccount == pdata.userAccount and pwsql == pdata.password:            queuerequest,cid = self.threadmangert.getCanUseUserCacheThreadTForUserMangerTWithUser(useraccount)            if queuerequest != None and cid != None:                ttoken = self.getToken()                clientobj.handler.tea = ttoken                self.UserCacheQueues[useraccount] = queuerequest                    #玩家所在缓存列队保存列队                if self.userLoginAccounts.has_key(useraccount): #玩家已登陆过                    self.userTokens.pop(self.userLoginAccounts[useraccount][0])                self.CidCacheQueues[cid] = queuerequest                self.userTokens[ttoken] = useraccount                               #token保存帐号                self.userLoginAccounts[useraccount] = [ttoken,cid]      #帐号保存token和缓存名                self.tokenClient[ttoken] = clientobj                userobj = QueueObjs.UserObj(clientobj,'clientobj',useraccount) #dat,dataType,handler,account,csocket                queueobj = QueueObjs.QueueMangerObj(userobj,QueueObjs.Flog_UserObj,self.getName(),cid)                #queuerequest.put(copy.deepcopy(queueobj))                queuerequest.put(queueobj)        else:            print '错误:帐号或密码错误'            handlertmp = clientobj.handler            handlertmp.eno = erroflog.Erro_AccountOrPW            handlertmp.len = 0            handlertmp.com = 0            handlertmp.enc = 0            try:                  clientobj.csocket.send(handlertmp.getStructDat())            except EOFError:                  print '10002登陆成功返回客户端数据错误,错误情况:'                 print EOFError              except:                  print '10002登陆成功返回客户端数据错误'    def completeCmd10003(self,clientobj,mangersqlobj):        askData = mangersqlobj.data        pass    def completeCmd10004(self,clientobj,mangersqlobj):        askData = mangersqlobj.data        pass    def completeCmd10005(self,clientobj,mangersqlobj):        askData = mangersqlobj.data        pass    def completeCmd10006(self,clientobj,mangersqlobj):        askData = mangersqlobj.data        pass    def completeCmd10007(self,clientobj,mangersqlobj):        askData = mangersqlobj.data        pass    def completeCmd10008(self,clientobj,mangersqlobj):        askData = mangersqlobj.data        pass    def completeCmd10009(self,clientobj,mangersqlobj):        askData = mangersqlobj.data        pass    def receiveDataFromConnectCache(self,clientobj):        if clientobj.handler.cmd == 10001:            self.cmd10001(clientobj)        elif clientobj.handler.cmd == 10002:            self.cmd10002(clientobj)        elif clientobj.handler.cmd == 10003:            self.cmd10003(clientobj)        elif clientobj.handler.cmd == 10004:            self.cmd10004(clientobj)        elif clientobj.handler.cmd == 10005:            self.cmd10005(clientobj)        elif clientobj.handler.cmd == 10006:            self.cmd10006(clientobj)        elif clientobj.handler.cmd == 10007:            self.cmd10007(clientobj)        elif clientobj.handler.cmd == 10008:            self.cmd10008(clientobj)        elif clientobj.handler.cmd == 10009:            self.cmd10009(clientobj)    def cmd10001(self,clientobj):# 10001    玩家注册账号        #数据->帐号,密码，向注册服务器请求注册        tid = self._getMysqlIndex()        dat10001 = Cmds_pb2.RequestRegisterAccount()        dat10001.ParseFromString(clientobj.data)        dat = "INSERT INTO `server`.`servertab_rigester` (`useraccount`, `phone`, `rigestertype`, `pw`, `devicecode`, `ip`, `date`, `email`, `phoneType`, `sysversion`) VALUES ("        dat += "'" + str(dat10001.userAccount) + "','" + str(dat10001.phone) + "','" + str('2') + "','" + str(dat10001.password) + "','"+ str(dat10001.machingNumber) +"','"+ str(clientobj.ipAddr) +"','" + str(int(time.time())) + "','email@email.com','"+dat10001.userType+"','1.0');"        self.mysqlRequests[tid] = clientobj        print dat10001        #在用户数据库中增加帐号信息        mysqlaskobj = QueueObjs.MysqlAskObj(tid,dat,1,0)        if len(self.mysqlUnUsedQueues) > 0:            mysqlname,mysqlqueue = self.mysqlUnUsedQueues.popitem()            self.mysqlUsedQueues[mysqlname] = mysqlqueue            queueobj = QueueObjs.QueueMangerObj(mysqlaskobj,QueueObjs.Flog_MysqlAskObj,self.getName(),mysqlname)            #mysqlqueue.put(copy.deepcopy(queueobj))            mysqlqueue.put(queueobj)        else:            mysqlqueue,mysqlname = self.threadmangert.getCanUseMysqlThreadForOther(self.getName()) #mysql数据请求，需要时再请求，不用时马上释放连接,所以这里不作请求#mysql请求线程名                                 if mysqlqueue == None or mysqlname == None:                print '错误:未请求到mysql连接线程'                csocket = clientobj.csocket                handlertmp = clientobj.handler                handlertmp.eno = erroflog.Erro_NoMysqlConnect                handlertmp.enc = 0                handlertmp.com = 0                handlertmp.len = 0                try:                      csocket.send(handlertmp.getStructDat())                except EOFError:                      print '10001注册成功返回客户端数据错误,错误情况:'                     print EOFError                  except:                      print '10001注册成功返回客户端数据错误'                return             self.mysqlUsedQueues[mysqlname] = mysqlqueue            queueobj = QueueObjs.QueueMangerObj(mysqlaskobj,QueueObjs.Flog_MysqlAskObj,self.getName(),mysqlname)            #mysqlqueue.put(copy.deepcopy(queueobj))            mysqlqueue.put(queueobj)    def cmd10002(self,clientobj):# 10002    账号密码登陆        #数据->帐号,密码，向注册服务器请求注册        tid = self._getMysqlIndex()        dat10002 = Cmds_pb2.RequestLoginByAccount()        dat10002.ParseFromString(clientobj.data)        #数据库中查找用户是否存在        dat = "SELECT * FROM `server`.`servertab_rigester` where useraccount = '%s';"%(str(dat10002.userAccount))        #print dat        self.mysqlRequests[tid] = clientobj        #在用户数据库中增加帐号信息        mysqlaskobj = QueueObjs.MysqlAskObj(tid,dat,1)        if len(self.mysqlUnUsedQueues) > 0:            mysqlname,mysqlqueue = self.mysqlUnUsedQueues.popitem()            self.mysqlUsedQueues[mysqlname] = mysqlqueue            queueobj = QueueObjs.QueueMangerObj(mysqlaskobj,QueueObjs.Flog_MysqlAskObj,self.getName(),mysqlname)            #mysqlqueue.put(copy.deepcopy(queueobj))            mysqlqueue.put(queueobj)        else:            mysqlqueue,mysqlname = self.threadmangert.getCanUseMysqlThreadForOther(self.getName()) #mysql数据请求，需要时再请求，不用时马上释放连接,所以这里不作请求#mysql请求线程名                                 if mysqlqueue == None or mysqlname == None:                print '错误:未请求到mysql连接线程'                csocket = clientobj.csocket                handlertmp = clientobj.handler                handlertmp.eno = erroflog.Erro_NoMysqlConnect                handlertmp.enc = 0                handlertmp.com = 0                handlertmp.len = 0                try:                      csocket.send(handlertmp.getStructDat())                except EOFError:                      print '10002登陆不成功返回客户端数据错误,错误情况:'                     print EOFError                  except:                      print '10002登陆不成功返回客户端数据错误'                return             self.mysqlUsedQueues[mysqlname] = mysqlqueue            queueobj = QueueObjs.QueueMangerObj(mysqlaskobj,QueueObjs.Flog_MysqlAskObj,self.getName(),mysqlname)            #mysqlqueue.put(copy.deepcopy(queueobj))            mysqlqueue.put(queueobj)    def cmd10003(self,clientobj):# 10003    使用设备码登录(直接登录)        pass    def cmd10004(self,clientobj):# 10004    修改密码        pass    def cmd10005(self,clientobj):# 10005    获取游戏服务器列表        pass    def cmd10006(self,clientobj):# 10006    访问游戏服务器接口        pass    def cmd10007(self,clientobj):# 10007    转发到登陆服务器登陆        pass    def cmd10008(self,clientobj):# 10008    获取客户端数据配置表md5效验码        pass    def cmd10009(self,clientobj):# 10009    服务器心跳包，返回当前服务器时间        pass    def receiveDataFromUserCacheT(self,userstautsobj):#1创建帐号成功,        userstauts = userstautsobj        if userstauts.dataType == 'login':#用户登陆成功            self.sendDataToConneceCache(userstauts.token, userstauts.account,userstauts.cID)            if self.tokenClient.has_key(userstauts.token):                clientox = self.tokenClient.pop(userstauts.token)                handlertmp = clientox.handler                clientproto =  Cmds_pb2.ResponseRegisterAccount()                clientproto.registerAccount.isBinded = False                clientproto.registerAccount.lastLoginServerID = 1                clientproto.registerAccount.loginToken = userstauts.token                for ser in self.serverlist:                        serverinfo = clientproto.registerAccount.servers.add()                        serverinfo.pID = int(ser['id'])                        serverinfo.pType = int(ser['type'])                        serverinfo.pStatus = int(ser['status'])                        serverinfo.pPort = int(ser['port'])                        serverinfo.pName = str(ser['name'])                        serverinfo.pIP = str(ser['ip'])                print clientproto                sdat = clientproto.SerializePartialToString()                handlertmp.len = len(sdat)                handlertmp.enc = 0                handlertmp.eno = 0                handlertmp.com = 0                handlertmp.tea = userstauts.token                sdat = handlertmp.getStructDat() + sdat                try:                      clientox.csocket.send(sdat)                   except EOFError:                      print '10001返回服务器列表到客户端错误,客户端可能已断开,错误情况:'                     print EOFError                  except:                      print '10001返回服务器列表到客户端错误,客户端可能已断开'            #通知connectCache建立用户连接转发        elif userstauts.dataType == 'email':#用户要发送邮件给其他用户            #userstatuseobj = QueueObjs.UserStatusObj('','email',fromName,toAccount,emailNid)#dat,dataType,account,token,cID):            useraccount = userstauts.token#toAccount            fromName = userstauts.account            emailNid = userstauts.cID            emailType = userstauts.data            #queuerequest,cid = self.threadmangert.getUserWorkUserCacheTQueueWithAccount(useraccount)            if self.UserCacheQueues.has_key(useraccount) and self.userLoginAccounts.has_key(useraccount):                queuerequest = self.UserCacheQueues[useraccount]                cidname = self.userLoginAccounts[useraccount][1]                userobj = QueueObjs.UserObj(emailNid,'email',useraccount,fromName,emailType) #dat,dataType,account,ttoken = 0,csocket = None):                queueobj = QueueObjs.QueueMangerObj(userobj,QueueObjs.Flog_UserObj,self.getName(),cidname)                #queuerequest.put(copy.deepcopy(queueobj))                queuerequest.put(queueobj)            else:#接入邮件的用户不在线,在用户帐号数据库中保存用户有新邮件标志                tid = self._getMysqlIndex()                cmdstr = "UPDATE `game`.`nettab_account` SET "                cmdstr += "`isNewEmail`='%d' "%(1)                cmdstr += "WHERE `account`='%s';\n"%(str(useraccount))                #数据库中查找用户是否存在                dat = cmdstr                self.mysqlRequests[tid] = 0                #在用户数据库中增加帐号信息                mysqlaskobj = QueueObjs.MysqlAskObj(tid,dat,1)                if len(self.mysqlUnUsedQueues) > 0:                    mysqlname,mysqlqueue = self.mysqlUnUsedQueues.popitem()                    self.mysqlUsedQueues[mysqlname] = mysqlqueue                    queueobj = QueueObjs.QueueMangerObj(mysqlaskobj,QueueObjs.Flog_MysqlAskObj,self.getName(),mysqlname)                    #mysqlqueue.put(copy.deepcopy(queueobj))                    mysqlqueue.put(queueobj)                else:                    mysqlqueue,mysqlname = self.threadmangert.getCanUseMysqlThreadForOther(self.getName()) #mysql数据请求，需要时再请求，不用时马上释放连接,所以这里不作请求#mysql请求线程名                                         if mysqlqueue == None or mysqlname == None:                        print '错误:未请求到mysql连接线程'                        return                     self.mysqlUsedQueues[mysqlname] = mysqlqueue                    queueobj = QueueObjs.QueueMangerObj(mysqlaskobj,QueueObjs.Flog_MysqlAskObj,self.getName(),mysqlname)                    #mysqlqueue.put(copy.deepcopy(queueobj))                    mysqlqueue.put(queueobj)        elif userstauts.dataType == 'loginout':#用户token到期            self.userCacheID[userstauts.account] = None    def sendDataToConneceCache(self,usertoken,useraccount,cID):        userstatusobj = QueueObjs.UserStatusObj('login','login',useraccount,usertoken,cID)#(self,dat,dataType,account,token,cID):        queueobj = QueueObjs.QueueMangerObj(userstatusobj,QueueObjs.Flog_UserStatusObj,self.getName(),self.connectCacheName)        self.cacheQueueRequest.put(queueobj)        #self.cacheQueueRequest.put(copy.deepcopy(queueobj))    def run(self):        while(True):            if not self.queueReauest.empty():                queueobj = self.queueReauest.get_nowait()                if queueobj.fromTName == self.connectCacheName:                    self.receiveDataFromConnectCache(queueobj.data)                elif self.CidCacheQueues.has_key(queueobj.fromTName):                    self.receiveDataFromUserCacheT(queueobj.data)                elif self.mysqlUsedQueues.has_key(queueobj.fromTName):                    mysqlname = queueobj.fromTName                    mysqlqueu = self.mysqlUsedQueues.pop(mysqlname)                    if len(self.mysqlUnUsedQueues) > 1:                        self.threadmangert.releasMysqlControlForThreadName(self.getName(),mysqlname)                    else:                        self.mysqlUnUsedQueues[mysqlname] = mysqlqueu                    self.receiveDataFromMysqlConnectT(queueobj.data)