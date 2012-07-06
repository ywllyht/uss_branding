#!/usr/bin/python
# coding:utf-8
# 21:31:55 create orderdinner.py
#  ywllyht@yahoo.com.cn  

from bottle import route, run, Bottle, template, request, abort, redirect, response, hook
from orderdinner_mode import Dinner, Menu, Accounts, History, HistoryItem
from users import login_required
import os
import time

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
    return template('dinner/menu.htm', dinner=d, user=request.user)


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
    return "Rucy not completed"

@dinner_app.route("/menu/active/<menuid>")
@login_required
def dinner_menu_active(menuid):
    return "Rucy not completed" 

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
    balance = 0
    for account in d.accounts.accounts:
        if request.user.username == account[0]:
            balance = account[1]
            break
    #print "balance=",balance
    today = time.strftime("%Y%m%d",time.localtime())
    return template('dinner/book_list.htm', dinner=d, today=today, user=request.user, balance=balance)

@dinner_app.route("/menu/book_list/",method='POST')
@login_required
def dinner_menu_book():
    d = Dinner()
    menuid= request.forms.get('menuid')
    itemid= request.forms.get('book_select')
    username= request.forms.get('users')
    #print "itemid,username,menuid",itemid,username,menuid
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



if __name__ == '__main__':
    run(dinner_app,host="0.0.0.0",reloader=True)
