#!/usr/bin/python
# coding:utf-8
# 21:53:53 create orderdinner_mode.py
#  ywllyht@yahoo.com.cn  

import os
import sys
import re
import time

p_block_type = re.compile("\[START_(\w+)\]")
p_menuitem = re.compile("(?P<price>\d+.?\d{0,2})元")

_localDir=os.path.dirname(__file__)
_curpath=os.path.normpath(os.path.join(os.getcwd(),_localDir))
fn = os.path.join(_curpath,"orderdinner.txt")
fn_bak = os.path.join(_curpath,"orderdinner_bak.txt")


UTF8_BOM = "".join(map(lambda x:chr(int(x,16)), ["ef","bb","bf"]))

def lock_write(f):
    
    def _function(dinner,*arg,**karg):
        f2 = open(fn_bak,"w+")

        dinner.readData()

        r = f(dinner,*arg,**karg)

        if r == "":
            f2.write("lock!")
            f2.flush()

            f1 = open(fn,"w+")
            f1.write(dinner.__str__())
            f1.close()

        f2.close()

        return r

    return _function 






class Dinner(object):
    def __init__(self):
        self.admins = []
        self.users = []
        self.menus = []
        self.accounts = None
        self.history = None
        

    def readData(self):
        self.admins = []
        self.users = []
        self.menus = []
        self.accounts = None
        self.history = None

        for block,block_type in self.yieldData():
            #print block,block_type
            if block_type == "USER":
                r = self.readUser(block)
                if r != "":
                    return "Dinner.readUser() error! " + r

            elif block_type == "MENU":
                m = Menu()
                r = m.readData(block)
                if r == "":
                    self.menus.append(m)
                else:
                    return "Menu.readData() error! " + r

            elif block_type == "ACCOUNT":
                m = Accounts()
                r = m.readData(block)
                if r == "":
                    self.accounts = m
                else:
                    return "Acount.readData() error! " + r

            elif block_type == "HISTORY":
                m = History()
                r = m.readData(block)
                if r == "":
                    self.history = m
                else:
                    return "History.readData() error! " + r

        if self.accounts == None:
            self.accounts = Accounts()

        if self.history == None:
            self.history = History()

        if len(self.admins) == 0:
            return "Dinner.readDate() error! self.admins == 0!"

        return ""

    def readUser(self,block):
        block_len = len(block)
        if block_len != 4:
            return "  blcok_len != 4" 
        if block[0] != "[START_USER]":
            return "  [START_USER] missing"
        if block[block_len-1] != "[END_USER]":
            return "  [END_USER] missing"

        line = block[1]
        self.admins = line.split(",")

        line = block[2]
        self.users = line.split(",")

        return ""
        

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
            if line == UTF8_BOM:
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
        s.append("\n[START_USER]\n")
        s.append(",".join(self.admins)+"\n")
        s.append(",".join(self.users)+"\n")
        s.append("[END_USER]\n\n")
        for m in self.menus:
            s.append(str(m)+"\n\n")
        s.append(str(self.accounts)+"\n\n")
        s.append(str(self.history)+"\n\n")
        return "".join(s)


        

    def menu_active(self,menuid, operatorname):


        f2 = open(fn_bak,"w+")
        self.readData()

        result = ""

        if operatorname not in self.admins:
            f2.close()
            return "Dinner.menu_active() error, you are not authorized!"


        findflag = False
        for menu in self.menus:
            if menu.id == menuid:
                findflag = True
                menu.active = time.strftime("%Y%m%d",time.localtime())
                menu.confirm = "False"
                menu.historyitems = []
                break
        if findflag == False:
            result = "Dinner.menu_active() error, not find target menu " + menuid

        if result == "":
            f2.write("lock")
            f2.flush()

            f1 = open(fn,"w+")
            f1.write(self.__str__())
            f1.close()

        f2.close()

        return result

    @lock_write
    def menu_add(self,menu, operatorname):
        if operatorname not in self.admins:
            return "Dinner.menu_add() error, you are not authorized!"
        self.menus.append(menu)
        return ""

    @lock_write
    def menu_delete(self,menuid,operatorname):
        result = ""

        if operatorname not in self.admins:
            return "Dinner.menu_delete() error, you are not authorized!"

        findflag = False
        for menu in self.menus:
            if menu.id == menuid:
                findflag = True
                self.menus.remove(menu)
                break

        if findflag == False:
            result = "Dinner.menu_delete() error, not find target menu " + menuid

        return result
        

    @lock_write
    def menu_confirm(self,menuid,operatorname):
        result = ""

        if operatorname not in self.admins:
            return "Dinner.menu_confirm() error, you are not authorized!"


        findflag = False
        for menu in self.menus:
            if menu.id == menuid:
                findflag = True

                if menu.active != time.strftime("%Y%m%d",time.localtime()):
                    return "Dinner.menu_confirm() error, Target menu is not active "

                if menu.confirm != "False":
                    return "Dinner.menu_confirm() error, menu.confirm != 'False' "
                menu.confirm = time.strftime("%Y%m%d",time.localtime())


                for item in menu.historyitems:
                    self.accounts.confirm(item)                # reduce user's money in account
                    self.history.historyitems.append(item)   # move historyitem from Menu section to History section
                #menu.historyitems = []       # we remain these temp record for facilitating copy of them, then 
                                              # admin can send these records to restaurants
                break

        if findflag == False:
            result = "Dinner.menu_confirm() error, not find target menu " + menuid

        return result


    @lock_write
    def menu_book(self,menuid,itemid,operatorid,operatorname,username):
        result = ""
        findflag = False
        itemfindflag = False
        for menu in self.menus:
            if menu.id == menuid:
                findflag = True

                if menu.active != time.strftime("%Y%m%d",time.localtime()):
                    return "Dinner.menu_book() error, target menu has not actived! "

                if menu.confirm != "False":
                    return "Dinner.menu_book() error, target menu has confirmed! "

                if len(menu.historyitems) > 40:
                    return "Dinner.menu_book() error, target menu has more than 30 historyitems "

                for item in menu.menuitems:
                    if item.id == itemid:
                        itemfindflag = True
                        newid =  "T"+str(int(time.time()))+operatorid
                        h = HistoryItem(newid,operatorname,username, time.strftime("%Y%m%d",time.localtime()), str(0 - item.money), item.description)
                        menu.historyitems.append(h)
                        break
                break

        if findflag == False:
            result = "Dinner.menu_book() error, not find target menu " + menuid

        if itemfindflag == False:
            result = "Dinner.menu_book() error, not find target menuitem " + itemid

        return result

    @lock_write
    def menu_book_delete(self,menuid,itemid,operatorname):
        result = ""
        findflag = False
        itemfindflag = False
        for menu in self.menus:
            if menu.id == menuid:
                findflag = True

                if menu.active != time.strftime("%Y%m%d",time.localtime()):
                    return "Dinner.menu_book_delete() error, target menu has not actived! "

                if menu.confirm != "False":
                    return "Dinner.menu_book_delete() error, target menu has confirmed! "

                for item in menu.historyitems:
                    if item.id == itemid:
                        itemfindflag = True
                        if item.operator != operatorname and (item.operator not in self.admins):
                            return "Dinner.menu_book_delete() error, you are not authorized! "
                        menu.historyitems.remove(item)
                        break
                break

        if findflag == False:
            result = "Dinner.menu_book_delete() error, not find target menu " + menuid

        if itemfindflag == False:
            result = "Dinner.menu_book_delete() error, not find target historyitem " + itemid

        return result





    @lock_write
    def accounts_add(self,historyitem, operatorname):

        if operatorname not in self.admins:
            return "Dinner.accounrts_add() error, you are not authorized!"
      

        self.accounts.confirm(historyitem)                # reduce user's money in account
        self.history.historyitems.append(historyitem)   # move historyitem from Menu section to History section
 
        return ""
        
        
    

    
            
class Menu(object):
    def __init__(self):
        self.id = ""
        self.title = ""
        self.active = ""
        self.confirm = ""
        self.menuitems = []
        self.historyitems = []

    def create(self,menudata):
        lines = menudata.splitlines()
        lines_len = len(lines)
        if lines_len < 2:
            return "Menu.create() error! lines_len < 2"

        new_id =  "M"+str(int(time.time()*100))
        
        line = lines[0]
        line = line.strip()
        if len(line) <= 0:
            return "Menu.create() error! first line should contain shop's name"
        new_title = line
        
        new_menuitems = []

        itemnumber = 1
        for line in lines[1:]:
            line = line.strip()
            if len(line) <= 0:
                continue
            m = p_menuitem.search(line)
            if m:
                new_itemid = "P"+str(itemnumber)
                itemnumber += 1
                new_money = m.group("price")
                new_description = line.replace(new_money+"元", "")

                menuitem = MenuItem()
                menuitem.id = new_itemid
                menuitem.money = float(new_money)
                menuitem.description = new_description
                
                new_menuitems.append(menuitem)

        if len(new_menuitems) == 0:
            return "Menu.create() error! this menudata does not contain any menuitem!"

        self.id = new_id
        self.title = new_title
        self.active = "False"
        self.confirm = "False"
        self.menuitems = new_menuitems
        self.historyitems = []
                


    def readData(self,block):
        block_len = len(block)
        if block[0] != "[START_MENU]":
            return "  [START_MENU] missing"
        if block[block_len-1] != "[END_MENU]":
            return "  [END_MENU] missing"

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
                slice1 = line.split(" ",2)
                item = MenuItem()
                item.id = slice1[0]
                item.money = float(slice1[1])
                item.description = slice1[2]
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
                return "  illegal data - "+line

        return ""

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
        self.id = ""
        self.money = 0
        self.description = ""

    def __str__(self):
        return self.id + " " + str(self.money) + " " + self.description

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
            return "  [START_ACCOUNT] missing"
        if block[block_len-1] != "[END_ACCOUNT]":
            return "  [END_ACCOUNT] missing"
        
        for line in block[1:-1]:
            slice1 = line.split(" ",1)
            if len(slice1) == 2:
                username = slice1[0]
                money = float(slice1[1])
                self.accounts.append([username,money])
            else:
                return "  illegal data - "+line

        return ""
       
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
            return "  [START_HISTORY] missing"
        if block[block_len-1] != "[END_HISTORY]":
            return "  [END_HISTORY] missing"

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
                return "  illegal data - "+line

        return ""

    def __str__(self):
        s = []
        s.append("[START_HISTORY]")
            
        for item in self.historyitems:
            s.append(str(item))

        s.append("[END_HISTORY]")
        return "\n".join(s)

    


if __name__ == '__main__':
    
    # a = "T5/鱼香肉丝 12.3元 fff"
    # a = "T5/鱼香肉丝 12元 fff"
    # m = p_menuitem.search(a)
    # if m:
    #     print m.group("price")
    # else:
    #     print "match fail"
    
    menudata = '''小灯笼四川 QQ11112
T5/鱼香肉丝 12.3元 fff

12元 TT/宫保鸡丁盖饭
'''
    m = Menu()
    m.create(menudata)
    print m

    #sys.exit(1)

    d = Dinner()
    r = d.readData()
    if r == "":
        print d
    else:
        print "d.readData() error "+ r
        sys.exit(1)

    
    # r = d.menu_add(m,"yoga")
    # if r!= "":
    #     print r

    # r = d.menu_delete("M134133013419","yoga")
    # if r!= "":
    #     print r
        
    menuid= "M2121211113"
    r = d.menu_active(menuid,"yoga")
    if r != "":
        print r
    

    r = d.menu_book(menuid,"P1","11","yoga","lljli")
    if r!= "":
        print r
    
    # print d
    # itemid = raw_input("input:")
    # r = d.menu_book_delete(menuid, itemid, "yoga")
    # if r != "":
    #     print r


    r = d.menu_confirm(menuid,"yoga")
    if r != "":
        print r


    newid =  "T"+str(int(time.time()))
    h = HistoryItem(newid,"yoga","yoga", time.strftime("%Y%m%d",time.localtime()), 100.0, "充值")
    r = d.accounts_add(h,"yoga")
    if r != "":
        print r

