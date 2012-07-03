#!/usr/bin/python
# coding:utf-8
# 21:53:53 create orderdinner_mode.py
#  ywllyht@yahoo.com.cn  

import os
import sys
import re
import time

p_block_type = re.compile("\[START_(\w+)\]")
_localDir=os.path.dirname(__file__)
_curpath=os.path.normpath(os.path.join(os.getcwd(),_localDir))
fn = os.path.join(_curpath,"orderdinner.txt")
fn_bak = os.path.join(_curpath,"orderdinner_bak.txt")




def lock_write(f):
    
    def _function(dinner,*arg,**karg):
        f2 = open(fn_bak,"w+")

        dinner.readData()

        r = f(dinner,*arg,**karg)
        
        f2.write(dinner.__str__())
        f2.flush()

        f1 = open(fn,"w+")
        f1.write(dinner.__str__())
        f1.close()

        f2.close()

        return r

    return _function 






class Dinner(object):
    def __init__(self):
        self.menus = []
        self.accounts = None
        self.history = None

    def readData(self):
        self.menus = []
        self.accounts = None
        self.history = None

        for block,block_type in self.yieldData():
            #print block,block_type
            if block_type == "MENU":
                m = Menu()
                r = m.readData(block)
                if r == True:
                    self.menus.append(m)
                else:
                    print "Menu.readData() error! "
                    return False
            elif block_type == "ACCOUNT":
                m = Accounts()
                r = m.readData(block)
                if r == True:
                    self.accounts = m
                else:
                    print "Acount.readData() error! "
                    return False
            elif block_type == "HISTORY":
                m = History()
                r = m.readData(block)
                if r == True:
                    self.history = m
                else:
                    print "History.readData() error! "
                    return False

        if self.accounts == None:
            self.accounts = Accounts()

        if self.history == None:
            self.history = History()

        return True

    def yieldData(self):
        f1 = open(fn)
        lines = f1.readlines()
        block = []
        block_type = ""
        for line in lines:
            line = line.strip()
            if len(line) <= 1:
                continue
            if line[0] == "#":
                continue
            if line.startswith("[START_"):
                m = p_block_type.match(line)
                if m:
                    block_type = m.groups()[0]
                else:
                    yield [line],"ERROR"
            block.append(line)
            if line.startswith("[END_"):
                yield block,block_type
                block = []
        yield [],"EOF"
        f1.close()


    def __str__(self):
        s = []
        for m in self.menus:
            s.append(str(m)+"\n\n")
        s.append(str(self.accounts)+"\n\n")
        s.append(str(self.history)+"\n\n")
        return "".join(s)


        

    def menu_active(self,menuid):
        f2 = open(fn_bak,"w+")
        self.readData()

        result = False
        for menu in self.menus:
            if menu.id == menuid:
                menu.active = time.strftime("%Y%m%d",time.localtime())
                menu.historyitems = []
                result = True
                break

        f2.write(self.__str__())
        f2.flush()

        f1 = open(fn,"w+")
        f1.write(self.__str__())
        f1.close()

        f2.close()

        return result

    @lock_write
    def menu_add(self,menu):
        self.menus.append(menu)

    @lock_write
    def menu_delete(self,menuid):
        result = False
        for menu in self.menus:
            if menu.id == menuid:
                self.menus.remove(menu)
                break
        return result
        

    @lock_write
    def menu_confirm(self,menuid):
        result = False
        for menu in self.menus:
            if menu.id == menuid:
                menu.confirm = time.strftime("%Y%m%d",time.localtime())


                for item in menu.historyitems:
                    self.accounts.confirm(item)                # reduce user's money in account
                    self.history.historyitems.append(item)   # move historyitem from Menu section to History section
                menu.historyitems = []

                result = True
                break

        return result

    @lock_write
    def menu_book(self,menuid,historyitem):
        result = False
        for menu in self.menus:
            if menu.id == menuid:

                menu.historyitems.append(historyitem)

                result = True
                break

        return result

    @lock_write
    def accounts_add(self,historyitem):
        self.accounts.confirm(historyitem)                # reduce user's money in account
        self.history.historyitems.append(historyitem)   # move historyitem from Menu section to History section
 
        return True
        
        
    

    
            
class Menu(object):
    def __init__(self):
        self.id = ""
        self.title = ""
        self.active = ""
        self.confirm = ""
        self.menuitems = []
        self.historyitems = []

    def readData(self,block):
        block_len = len(block)
        if block[0] != "[START_MENU]":
            print "  [START_MENU] missing"
            return False
        if block[block_len-1] != "[END_MENU]":
            print "  [END_MENU] missing"
            return False

        line = block[1]
        slice1 = line.split(" ",1)
        self.id = slice1[0]
        self.title = slice1[1]

        line = block[2]
        slice1 = line.split("=",1)
        self.active = slice1[1]
        
        line = block[3]
        slice1 = line.split("=",1)
        self.confirm = slice1[1]

        for line in block[4:-1]:
            if line[0] == "P":
                slice1 = line[1:].split(" ",1)
                item = MenuItem()
                item.money = float(slice1[0])
                item.description = slice1[1]
                self.menuitems.append(item)
            elif line[0] == "T":
                slice1 = line.split(" ",5)
                item = HistoryItem()
                item.id = slice1[0]
                item.operator = slice1[1]
                item.user = slice1[2]
                item.date = slice1[3]
                item.money = float(slice1[4])
                item.description = slice1[5]
                self.historyitems.append(item)
            else:
                print "  illegal data - ",line
                return False
        return True

    def __str__(self):
        s = []
        s.append("[START_MENU]")

        s.append(self.id + " " + self.title)
        s.append("active=" + self.active)
        s.append("confirm=" + self.confirm)
        
        for item in self.menuitems:
            s.append(str(item))
            
        for item in self.historyitems:
            s.append(str(item))
        s.append("[END_MENU]")
        return "\n".join(s)

class MenuItem(object):
    def __init__(self):
        self.money = 0
        self.description = ""

    def __str__(self):
        return "P" + str(self.money) + " " + self.description

class HistoryItem(object):

    def __init__(self,hid="",operator="",user="",date="",money=0.0,description=""):
        self.id = hid
        self.operator = operator
        self.user = user
        self.date = date
        self.money = money
        self.description = description

    def __str__(self):
        return self.id+" "+self.operator+" "+self.user+" "+self.date+" " \
            + str(self.money) + " " + self.description
             



class Accounts(object):

    def __init__(self):
        self.accounts = []

    def readData(self,block): 
        block_len = len(block)
        if block[0] != "[START_ACCOUNT]":
            print "  [START_ACCOUNT] missing"
            return False
        if block[block_len-1] != "[END_ACCOUNT]":
            print "  [END_ACCOUNT] missing"
            return False
        
        for line in block[1:-1]:
            slice1 = line.split(" ",1)
            if len(slice1) == 2:
                username = slice1[0]
                money = float(slice1[1])
                self.accounts.append([username,money])
            else:
                print "  illegal data - ",line
                return False
        return True
       
    def confirm(self,historyitem):
        ''' take care, the input money is minus number'''
        user = historyitem.user
        money = historyitem.money

        findflag = False
        for account in self.accounts:
            if account[0] == user:
                account[1] = account[1] + money
                findflag = True
                break

        if findflag == False:
            self.accounts.append([user,money])
                
        
    def __str__(self):
        s = []
        s.append("[START_ACCOUNT]")
        for a in self.accounts:
            s.append(a[0]+" "+str(a[1]))
        s.append("[END_ACCOUNT]")
        return "\n".join(s)

class History(object):
    
    def __init__(self):
        self.historyitems = []


    def readData(self,block):
        block_len = len(block)
        if block[0] != "[START_HISTORY]":
            print "  [START_HISTORY] missing"
            return False
        if block[block_len-1] != "[END_HISTORY]":
            print "  [END_HISTORY] missing"
            return False

        for line in block[1:-1]:
            if line[0] == "T":
                slice1 = line.split(" ",5)
                item = HistoryItem()
                item.id = slice1[0]
                item.operator = slice1[1]
                item.user = slice1[2]
                item.date = slice1[3]
                item.money = float(slice1[4])
                item.description = slice1[5]
                self.historyitems.append(item)
            else:
                print "  illegal data - ",line
                return False
        return True

    def __str__(self):
        s = []
        s.append("[START_HISTORY]")
            
        for item in self.historyitems:
            s.append(str(item))

        s.append("[END_HISTORY]")
        return "\n".join(s)

    


if __name__ == '__main__':
    d = Dinner()
    if d.readData():
        print d
    else:
        print "d.readData() error"
        sys.exit(1)

        
    menuid= "M2121211113"
    d.menu_active(menuid)
    
    newid = "T"+str(int(time.time()))
    h = HistoryItem(newid,"yujia","yujia", time.strftime("%Y%m%d",time.localtime()), -10.0, "铁板烧")
    d.menu_book(menuid,h)
    

    d.menu_confirm(menuid)


    newid =  "T"+str(int(time.time()))
    h = HistoryItem(newid,"yujia","yujia", time.strftime("%Y%m%d",time.localtime()), 100.0, "充值")
    d.accounts_add(h)

