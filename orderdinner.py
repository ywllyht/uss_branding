#!/usr/bin/python
# coding:utf-8
# 21:31:55 create orderdinner.py
#  ywllyht@yahoo.com.cn  

from bottle import route, run, Bottle, template, request, abort, redirect, response, hook
from orderdinner_mode import Dinner, Menu, Accounts, History
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
    return "Yoga not completed"

@dinner_app.route("/menu/book_list/")
@login_required
def dinner_menu_book_list():
    d = Dinner()
    d.readData()
    today = time.strftime("%Y%m%d",time.localtime())
    return template('dinner/book_list.htm', dinner=d, today=today, user=request.user)

@dinner_app.route("/menu/book/<menuid>/<menuitemid>",method='POST')
@login_required
def dinner_menu_book(menuid,menuitemid):
    return "Yoga not completed"

@dinner_app.route("/menu/book_delete/<menuid>/<historyitemid>")
@login_required
def dinner_menu_book_delete(menuid,historyitemid):
    d = Dinner()
    r = d.menu_book_delete(menuid,historyitemid,request.user.username)
    if r != "":
        return template("mydirect.htm",title="reservation delete fail", msg=r, next_url="/dinner/menu/book_list/", user=request.user)
    else:
        redirect("/dinner/menu/book_list/")


@dinner_app.route("/accounts/manager/")
@login_required
def dinner_accounts_manager():
    return "Daisy not completed"

@dinner_app.route("/accounts/add/",method="POST")
@login_required
def dinner_accounts_add():
    return "Daisy not completed"

@dinner_app.route("/accounts/list/")
@login_required
def dinner_accounts_list():
    return "Daisy not completed"




if __name__ == '__main__':
    run(dinner_app,host="0.0.0.0",reloader=True)
