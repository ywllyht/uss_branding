# coding:utf-8
# created time is 12:04:52 2012-03-11
# filename: initials.py
# ywllyht@yahoo.com.cn

import sqlite3
def db1():
    con = sqlite3.connect('branding.db') # Warning: This file is created in the current directory
    con.execute("CREATE TABLE todo (id INTEGER PRIMARY KEY, task char(100) NOT NULL, status bool NOT NULL)")
    con.execute("INSERT INTO todo (task,status) VALUES ('Read A-byte-of-python to get a good introduction into Python',0)")
    con.execute("INSERT INTO todo (task,status) VALUES ('Visit the Python website',1)")
    con.execute("INSERT INTO todo (task,status) VALUES ('Test various editors for and check the syntax highlighting',1)")
    con.execute("INSERT INTO todo (task,status) VALUES ('Choose your favorite WSGI-Framework',0)")
    con.commit()


if __name__ == '__main__':
    db1()

