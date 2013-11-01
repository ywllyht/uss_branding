#!/usr/bin/python
# coding:utf-8
# 21:31:55 create orderdinner.py
#  ywllyht@yahoo.com.cn  

from bottle import route, run, Bottle, template, request, abort, redirect, response, hook
from orderdinner_mode import Dinner, Menu, Accounts, History, HistoryItem
from users import login_required
import os
import time
import re

dinner_app = Bottle()


@dinner_app.route("/")
@login_required
def dinner_index():
    return template('dinner/index.htm',user=request.user)

@dinner_app.route("/menu/")
@login_required
def dinner_menu():
    d = Dinner()
    d.readData()
    today = time.strftime("%Y%m%d",time.localtime())
    return template('dinner/menu.htm', dinner=d, today=today, user=request.user)


@dinner_app.route("/menu/add/",method='POST')
@login_required
def dinner_menu_add():
    menudata = request.forms.get('menudata')
    #print menudata
    m = Menu()
    r = m.create(menudata)
    if r != "":
        return template("mydirect.htm",title="menu create fail", msg=r, next_url="/dinner/menu/", user=request.user)
    else:
        d = Dinner()
        r = d.menu_add(m, request.user.username)
        if r != "":
            return template("mydirect.htm",title="menu create fail", msg=r, next_url="/dinner/menu/", user=request.user)
        else:
            redirect("/dinner/menu/")


@dinner_app.route("/menu/delete/<menuid>")
@login_required
def dinner_menu_delete(menuid):
    d=Dinner()
    r=d.menu_delete(menuid, request.user.username)
    if r != "":
            return template("mydirect.htm",title="menu delete fail", msg=r, next_url="/dinner/menu/", user=request.user)
    else:
            redirect("/dinner/menu/")
   

@dinner_app.route("/menu/active/<menuid>")
@login_required
def dinner_menu_active(menuid):

    d=Dinner()
    r=d.menu_active(menuid, request.user.username)
    if r != "":
            return template("mydirect.htm",title="menu active fail", msg=r, next_url="/dinner/menu/", user=request.user)
    else:
            redirect("/dinner/menu/")

@dinner_app.route("/menu/deactive/<menuid>")
@login_required
def dinner_menu_deactive(menuid):

    d=Dinner()
    r=d.menu_deactive(menuid, request.user.username)
    if r != "":
            return template("mydirect.htm",title="menu active fail", msg=r, next_url="/dinner/menu/", user=request.user)
    else:
            redirect("/dinner/menu/")   


@dinner_app.route("/menu/confirm/<menuid>")
@login_required
def dinner_menu_confirm(menuid):
    d = Dinner()
    r = d.menu_confirm(menuid,request.user.username)
    if r != "":
        return template("mydirect.htm",title="reservation delete fail", msg=r, next_url="/dinner/menu/book_list/", user=request.user)
    else:
        redirect("/dinner/menu/book_list/")   

@dinner_app.route("/menu/book_list/")
@login_required
def dinner_menu_book_list():
    d = Dinner()
    d.readData()

    today = time.strftime("%Y%m%d",time.localtime())
    # calculate consume report for user
    balance = 0
    for account in d.accounts.accounts:
        if request.user.username == account[0]:
            balance = account[1]
            break
    hs = []
    for h in d.history.historyitems:
        if h.user == request.user.username:
            msg = "  %s for %s, %d元, %s, %s" %(h.operator,h.user,h.money,h.date,h.description)
            hs.append(msg);
    hs.reverse()
    if len(hs) >= 20:
        hs = hs[:20]
    hs.insert(0,"You recent consume records are as below:")
    hs.insert(1,"----------------------------------------")
    consume_report = "\n".join(hs)
    #print "balance=",balance

    # calculate book report
    for menu in d.menus:
        if menu.active == today:
            reportdetail = []
            totalmoney = 0
            for historyitem in menu.historyitems:
                msg = "%s, %10.2f元, %s" %(historyitem.user , 0-historyitem.money, historyitem.description)
                reportdetail.append(msg)
                totalmoney -= historyitem.money
            reporttext = "\n".join(reportdetail)+"\n------------------------------------------------\ntotal: "+str(totalmoney) +"元"+", "+str(len(reportdetail))+"份"
            menu.reporttext = reporttext

    return template('dinner/book_list.htm', dinner=d, today=today, user=request.user, balance=balance,consume_report=consume_report)

@dinner_app.route("/menu/book_list/",method='POST')
@login_required
def dinner_menu_book():
    d = Dinner()
    menuid= request.forms.get('menuid')
    itemid= request.forms.get('book_select')
    username= request.forms.get('users')
    #print "itemid,username,menuid",itemid,username,menuid
    if itemid == "0":
        itemprice=request.forms.get('item_price')
        itemdescription=request.forms.get('item_description')
        #print "itemprice,itemdescription",itemprice,itemdescription
        regex=ur"^[1-9]\d*|^[1-9]\d*\.\d*|^0\.\d*[1-9]\d*$" 
  
        if itemdescription == "":
            return template("mydirect.htm",title="reservation delete fail", msg="you didn't input the dish!", next_url="/dinner/menu/book_list/", user=request.user) 
        elif re.search(regex, itemprice):  
            r=d.menu_book_input(menuid,itemprice,itemdescription, request.user.userid, request.user.username,username)
            if r != "":
                return template("mydirect.htm",title="reservation delete fail", msg=r, next_url="/dinner/menu/book_list/", user=request.user) 
            else: 
                redirect("/dinner/menu/book_list/")   
        else:
            return template("mydirect.htm",title="reservation delete fail", msg="your money is not correct!", next_url="/dinner/menu/book_list/", user=request.user)  
    else:          
        r = d.menu_book(menuid, itemid, request.user.userid, request.user.username,username)
        if r != "":
            return template("mydirect.htm",title="reservation delete fail", msg=r, next_url="/dinner/menu/book_list/", user=request.user)
        else:
            redirect("/dinner/menu/book_list/")    
              

@dinner_app.route("/menu/book_delete/<menuid>/<historyitemid>")
@login_required
def dinner_menu_book_delete(menuid,historyitemid):
    d = Dinner()
    r = d.menu_book_delete(menuid,historyitemid,request.user.username)
    if r != "":
        return template("mydirect.htm",title="reservation delete fail", msg=r, next_url="/dinner/menu/book_list/", user=request.user)
    else:
        redirect("/dinner/menu/book_list/")


@dinner_app.route("/accounts/charge/")
@login_required
def dinner_accounts_manager():

    d = Dinner()
    d.readData()
    return template('dinner/account.htm', dinner=d, user=request.user)

@dinner_app.route("/accounts/add/",method="POST")
@login_required
def dinner_accounts_add():
   d = Dinner()
   username= request.forms.get('orderuser')
   money = request.forms.get('money')
   try:
       money = float(money)
   except ValueError,e:
       return template("mydirect.htm",title="Recharge Fail", msg="input money is illegal", next_url="/dinner/accounts/charge/", user=request.user)
   description = request.forms.get('description')

   newid =  "T"+str(int(time.time()))+request.user.userid
   h= HistoryItem(newid,request.user.username,username, time.strftime("%Y%m%d",time.localtime()),money,description)
     
   r= d.accounts_add(h,request.user.username)
   if r != "":
        return template("mydirect.htm",title="Recharge Fail", msg=r, next_url="/dinner/accounts/charge/", user=request.user)
   else:
        redirect("/dinner/accounts/charge/")
        
@dinner_app.route("/accounts/review/")
@login_required
def dinner_accounts_list():    
    d = Dinner()
    d.readData()
    return template('dinner/account_list.htm', dinner=d, user=request.user)


@dinner_app.route("/accounts/users/")
@login_required
def dinner_accounts_users():

    d = Dinner()
    d.readData()
    return template('dinner/users.htm', dinner=d, user=request.user)

@dinner_app.route("/accounts/adduser/",method="POST")
@login_required
def dinner_accounts_add():

   newusername = request.forms.get('newusername')
   newusername = newusername.strip()
   if not newusername:
       return template("mydirect.htm",title="Recharge Fail", msg="input username is illegal", next_url="/dinner/accounts/users/", user=request.user)

   d = Dinner()     
   r= d.users_add(newusername,request.user.username)
   if r != "":
        return template("mydirect.htm",title="Recharge Fail", msg=r, next_url="/dinner/accounts/users/", user=request.user)
   else:
        redirect("/dinner/accounts/users/")
        
@dinner_app.route("/accounts/deleteuser/<deleteusername>")
@login_required
def dinner_accounts_delete(deleteusername):
   deleteusrname = deleteusername.strip()
   if not deleteusername:
       return template("mydirect.htm",title="Recharge Fail", msg="input username is illegal", next_url="/dinner/accounts/users/", user=request.user)

   d = Dinner()
   r= d.users_delete(deleteusername,request.user.username)
   if r != "":
        return template("mydirect.htm",title="Recharge Fail", msg=r, next_url="/dinner/accounts/users/", user=request.user)
   else:
        redirect("/dinner/accounts/users/")
        


if __name__ == '__main__':
    run(dinner_app,host="0.0.0.0",reloader=True)
