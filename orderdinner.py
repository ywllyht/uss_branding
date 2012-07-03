#!/usr/bin/python
# coding:utf-8
# 21:31:55 create orderdinner.py
#  ywllyht@yahoo.com.cn  

from bottle import route, run, Bottle, template, request, abort, redirect, response, hook
import os

dinner_app = Bottle()



@dinner_app.route("/")
def dinner_index():
    return "Rucy not comleted"

@dinner_app.route("/menu/")
def dinner_menu():
    return "Rucy not completed"

@dinner_app.route("/menu/add/",method='POST')
def dinner_menu_add():
    return "Rucy not completed"

@dinner_app.route("/menu/delete/<menuid>")
def dinner_menu_delete(menuid):
    return "Rucy not completed"

@dinner_app.route("/menu/active/<menuid>")
def dinner_menu_active(menuid):
    return "Rucy not completed"

@dinner_app.route("/menu/confirm/<menuid>")
def dinner_menu_confirm(menuid):
    return "Yoga not completed"

@dinner_app.route("/menu/book_list/")
def dinner_menu_book_list():
    return "Yoga not completed"

@dinner_app.route("/menu/book/<menuid>/<menuitemid>",method='POST')
def dinner_menu_book(menuid,menuitemid):
    return "Yoga not completed"

@dinner_app.route("/menu/book_delete/<menuid>/<historyitemid>")
def dinner_menu_book_delete(menuid,historyitemid):
    return "Yoga not completed"


@dinner_app.route("/accounts/manager/")
def dinner_accounts_manager():
    return "Daisy not completed"

@dinner_app.route("/accounts/add/",method="POST")
def dinner_accounts_add(menuid):
    return "Daisy not completed"

@dinner_app.route("/accounts/list/")
def dinner_accounts_list(menuid):
    return "Daisy not completed"




if __name__ == '__main__':
    run(dinner_app,host="0.0.0.0",reloader=True)
