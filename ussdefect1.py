# coding:utf-8

from bottle import route, run, Bottle, template, request, abort, redirect, static_file
import sqlite3 as sqlite                                                                                    
import os                                                                                                
import sys
import time
from users import login_required
from urllib import urlencode, unquote


# create table if not exists ussdefects(
#         id integer primary key,
#         component varchar(10),
#         number varchar(10),
#         title varchar(30),
#         Lineitem varchar(10),
#         open_date varchar(20),
#         close_date varchar(20),
#         poster varchar(20),
#         status varchar(10),
#         comment varchar(30)
# );    

# insert into ussdefects values(NULL,"LE","111","ff zz","3204","2012-01-01","2012-02-01","lljli","close","only for test");
# insert into ussdefects values(NULL,"LE","ME222","ttt zz","3204","2012-01-03","2012-02-01","lljli","close","only for test");
# insert into ussdefects values(NULL,"LE","ME223","ttt zz","3204","2012-01-04","2012-02-01","lljli","close","only for test");
# insert into ussdefects values(NULL,"USS","MQ","ttt zz","3204","2012-01-05","2012-02-11","lljli","close","only for test");
# insert into ussdefects values(NULL,"Shell","z1501","ttt zz","133","2012-02-01","2012-02-11","lljli","close","only for test");
# insert into ussdefects values(NULL,"Shell","z1502","ttt zz","133.1","2012-02-01","2012-02-11","lljli","close","only for test fdasfsae \n ffff");



defect_status = ["open", "verify", "close", "returned", "cancel",]

USSdefect_app = Bottle()

@USSdefect_app.route("/") 
@login_required
def index():
    return template("ussdefect/index.htm",user=request.user)

@USSdefect_app.route("/defect/") 
@login_required
def defect():
    cx = sqlite.connect('branding.db')
    cu = cx.cursor()
    cu.execute('select * from ussdefects')
    rs = cu.fetchall()
    d_total = len(rs)
    d_open = 0
    d_verify = 0
    d_close = 0
    d_returned = 0
    d_cancel = 0
    d_other = 0
    for r in rs:
        if r[8] == "open":
            d_open += 1
        elif r[8] == "verify":
            d_verify += 1
        elif r[8] == "close":
            d_close += 1
        elif r[8] == "returned":
            d_returned += 1
        elif r[8] == "cancel":
            d_cancel += 1
        else:
            d_other += 1
    return template("ussdefect/defect.htm",user=request.user, defects=rs, d_total=d_total, d_open=d_open, d_verify=d_verify, d_close=d_close,
                    d_returned=d_returned, d_cancel=d_cancel, d_other=d_other)

@USSdefect_app.route("/defect/new/") 
@login_required
def defect_new():
    return template("ussdefect/defect_new.htm", user=request.user)


if __name__=="__main__":
    pass

