#!/usr/bin/env python# -*- coding: utf-8 -*-#数据类型编号Flog_MysqlAskObj = 1Flog_ClientConnectObj = 2Flog_ClientObj = 3Flog_UserObj = 4Flog_UserStatusObj = 5Flog_UserNomalObj = 6Flog_BaseData = 7flog_pkHerosData = 8flog_pkResultData = 9#所有线程中都只传送这种类型的数据，数据类型细节收dataType决定class QueueMangerObj():    def __init__(self,dat,datType,fromTName,toTName,isBack = False):        self.data = dat        #dataType分为:1.MysqlAskObj(mysql数据库请求),2.ClientConnectObj(客户端连接请求),3.ClientObj(客户端请求),4.UserObj(用户数据请求),5.UserStatusObj(用户状态数据),6.NomalObj(通用数据),7.basedata(对象间默认数据类型)        self.dataType = datType         self.fromTName = fromTName        self.toTName = toTName        self.isBack = isBack             #接收线程收到数据是否要返回#数据库请求对象class MysqlAskObj():    def __init__(self,askid,data,ptype = 4,account = '',askThreadName = '' ,countx = 0):#inset,del,update,sreach,close分别为增加数据，删除数据，修改数据，查找数据,关闭mysql连接,backfunc为查找到的数据返回        self.askid = askid                      #mysql请求编号        self.data = data                        #mysql请求拿命令        self.count = countx                     #mysql请返回数据行数        self.dataType = ptype                   #数据库请求类型,1.增加，2.删除，3.更新修改，4.查寻,-1,退出mysql数据库连接，'tsend':开启数据库连接        self.threadname = ''                    #mysql线程名        self.askThreadName = askThreadName                 #mysql请求者线程名        self.erro = 0        self.account = account#连接数据对象class ClientConnectObj():    def __init__(self,dat,ipAddr,csocket):        self.data = dat        self.IPaddr = ipAddr        self.csocket = csocket#客户端数据对象class ClientObj():    def __init__(self,dat,handler,csocket,ipAddr):        self.data = dat        self.handler = handler        self.csocket = csocket        self.ipAddr = ipAddr        #用户数据对象class UserObj():    def __init__(self,dat,dataType,account,ttoken = 0,csocket = None):        self.data = dat        self.dataType = dataType        self.account = account        self.token = ttoken        self.csocket = csocket#用户状态数据对象 class UserStatusObj():    def __init__(self,dat,dataType,account,token,cID):        self.data = dat        self.dataType = dataType        self.account = account        self.token = token        self.cID = cID        #用户状态数据对象 class PKEquipData():    def __init__(self,equipNID,equipCID,equipLevel,equipStar,equipQuality):        self.equipNID = equipNID        self.equipCID = equipCID        self.equipLevel = equipLevel        self.equipStar = equipStar        self.equipQuality = equipQuality        class PKHheroData():    def __init__(self,heroNid,heroCid,herolevel,heroStar,pSkillCID,pSkillLevel,pEquipDatas):        self.heroNID = heroNid        self.heroCID = heroCid        self.heroLevel = herolevel        self.heroStar = heroStar        self.skillCID = pSkillCID        self.skillLevel = pSkillLevel        self.equips = pEquipDatas        class PKHeroDataObj():    def __init__(self,heroDatas,dataType,account,token,beAccount,beToken,cID,isRobot = False,csocket = None):        self.data = heroDatas               #双方英雄数据{upheros:[PKHheroData,...],downheros:[PKHheroData,...]}        self.dataType = dataType            #数据类型,1.军机处对战,2.风云争霸,3.帮战        self.account = account              #战斗主动攻击方,主动攻击方在地图下方        self.beAccount = beAccount          #战斗被攻击方，被攻击方在地图上方        self.isRobot = isRobot              #被攻击方是否是机器人        self.token = token                  #主攻方token        self.betoken = beToken        self.cID = cID                      #主攻方用户线程ID        self.csocket = csocket              #主攻方客户端socket#战斗战报数据class PKWarDataObj():    def __init__(self,Account,beAccount,warType,warDataMysqlID,warData = None,isRobot = False):        self.data = warData                     #战报数据        self.warType = warType                  #战斗类型,1.军机处对战,2.风云争霸,3.帮战        self.account = Account                  #进攻方帐号        self.beAccount = beAccount              #防守方帐号        self.warDataMysqlID = warDataMysqlID    #战报数据保存的mysql网络ID        self.isRobot = isRobot                  #被攻击方是否是机器人#通用数据对象class NomalObj():    def __init__(self,dat,dataType = ''):        self.data = dat         self.dataType = dataType