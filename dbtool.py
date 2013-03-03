# coding:utf-8

import sqlite3 as sqlite                                                                                    
import re


def create_ussdefects():
    command = """
create table if not exists ussdefects(
        id integer primary key,
        component varchar(10),
        number varchar(10),
        title varchar(30),
        Lineitem varchar(10),
        open_date varchar(20),
        close_date varchar(20),
        poster varchar(20),
        status varchar(10),
        comment varchar(30)
);    

"""
    command1 = """
    insert into ussdefects values(NULL,"LE","111","ff zz","3204","2012-01-01","2012-02-01","lljli","close","only for test");
"""

    cx = sqlite.connect('branding.db')
    cu = cx.cursor()
    cu.execute(command)
    cu.execute(command1)
    cx.commit()
    cu.close()
    print "create end!"

def create_ussprojects():
    # if total_num = -1 -- this line item does not have a fix number, it might be regression test
    # if draw_flag = 0  -- we do not need to draw this line item's picture
    command = """
create table if not exists ussprojects(
        id integer primary key,
        name varchar(20),
        total_num integer,
        current_attempt integer,
        current_succ integer,
        draw_flag Integer,
        start_date varchar(20),
        end_date varchar(20),
        comment varchar(60)       
);    

"""
    command1 = """
    insert into ussprojects values(NULL,"Line133",683,0,0,1,"2012-01-01","2012-12-01","only for test");
"""

    cx = sqlite.connect('branding.db')
    cu = cx.cursor()
    cu.execute(command)
    cu.execute(command1)
    cx.commit()
    cu.close()
    print "create end!"

def create_ussproject():
    command = """
create table if not exists ussproject(
        id integer primary key,
        projectid integer,
        datepoint varchar(20),
        plan_attempt integer,
        plan_succ  integer,
        actual_attempt integer,
        actual_succ integer,
        comment varchar(60)       
);    

"""
    command1 = """
    insert into ussproject values(NULL,1,"2012-01-01",10,10,0,0,"only for test");
"""

    cx = sqlite.connect('branding.db')
    cu = cx.cursor()
    cu.execute(command)
    cu.execute(command1)
    cx.commit()
    cu.close()
    print "create end!"


   
if __name__=="__main__":
    #create_ussdefects()
    create_ussprojects()
    create_ussproject()
    
