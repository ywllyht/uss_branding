# coding:utf-8

from bottle import route, run, Bottle, template, request, abort, redirect, static_file
import sqlite3 as sqlite                                                                                    
import os                                                                                                
import sys
import time
import datetime
from users import login_required
from urllib import urlencode, unquote
import re
from pprint import pprint
from pychart import *

date_p = re.compile(r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})")
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
# insert into ussdefects values(NULL,"SHELL","z1501","ttt zz","133","2012-02-01","2012-02-11","lljli","close","only for test");
# insert into ussdefects values(NULL,"SHELL","z1502","ttt zz","133.1","2012-02-01","2012-02-11","lljli","close","only for test fdasfsae \n ffff");

_localDir=os.path.dirname(__file__)
_curpath=os.path.normpath(os.path.join(os.getcwd(),_localDir))
_staticpath = os.path.join(_curpath,"static")
#_picpath = os.path.join(_staticpath,"pics")
_defectpicpath = os.path.join(_staticpath,"ussdefects")

make_defect_py = os.path.join(_curpath,"ussdefectpic1.py")

defect_fun_fn1 = "ussdefect1"
defect_csv_fn1 = os.path.join(_defectpicpath,"ussdefect1.csv")
defect_eps_fn1 = os.path.join(_defectpicpath,"ussdefect1.eps")
defect_png_fn1 = os.path.join(_defectpicpath,"ussdefect1.png")

defect_fun_fn2 = "ussdefect2"
defect_csv_fn2 = os.path.join(_defectpicpath,"ussdefect2.csv")
defect_eps_fn2 = os.path.join(_defectpicpath,"ussdefect2.eps")
defect_png_fn2 = os.path.join(_defectpicpath,"ussdefect2.png")

defect_fun_fn3 = "ussdefect3"
defect_csv_fn3 = os.path.join(_defectpicpath,"ussdefect3.csv")
defect_eps_fn3 = os.path.join(_defectpicpath,"ussdefect3.eps")
defect_png_fn3 = os.path.join(_defectpicpath,"ussdefect3.png")


defect_status = ["open", "verify", "close", "returned", "cancel",]

USSdefect_app = Bottle()

@USSdefect_app.route("/") 
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
    d_reject = 0
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
        elif r[8] == "reject":
            d_reject += 1
        else:
            d_other += 1
    return template("ussdefect/defect.htm",user=request.user, defects=rs, d_total=d_total, d_open=d_open, d_verify=d_verify, d_close=d_close,
                    d_returned=d_returned, d_cancel=d_cancel, d_reject=d_reject, d_other=d_other)

@USSdefect_app.route("/defect/new/") 
@login_required
def defect_new():
    return template("ussdefect/defect_new.htm", user=request.user)

@USSdefect_app.route("/defect/new/",method="POST") 
@login_required
def defect_new_post():
    component = request.forms.get('component',"")
    number = request.forms.get('number',"")
    title = request.forms.get('title',"")
    Lineitem = request.forms.get('Lineitem',"")
    open_date = request.forms.get('open_date',"")
    close_date = request.forms.get('close_date',"")
    poster = request.forms.get('poster',"")
    status = request.forms.get('status',"")
    comment = request.forms.get('comment',"")
    
    component = component.replace("'","''")
    number = number.replace("'","''")
    title = title.replace("'","''")
    Lineitem = Lineitem.replace("'","''")
    open_date = open_date.replace("'","''")
    close_date = close_date.replace("'","''")
    poster = poster.replace("'","''")
    status = status.replace("'","''")
    comment = comment.replace("'","''")   
    
    if component == "":
        return template("myerror.htm", user=request.user, msg="Error,component is null!")
    if number == "":
        return template("myerror.htm", user=request.user, msg="Error, number is null!")
    if title == "":
        return template("myerror.htm", user=request.user, msg="Error,title is null!")
    if Lineitem == "":
        return template("myerror.htm", user=request.user, msg="Error,Lineitem is null!")
    if open_date == "":
        return template("myerror.htm", user=request.user, msg="Error,open_date is null!")
    if poster == "":
        return template("myerror.htm", user=request.user, msg="Error,poster is null!")
    if status == "":
        return template("myerror.htm", user=request.user, msg="Error,status is null!")
    m = date_p.match(open_date)
    if not m:
        return template("myerror.htm", user=request.user, msg="Error, open_date is invalid -- " + open_date)
    m = date_p.match(close_date)
    if close_date and not m:
        return template("myerror.htm", user=request.user, msg="Error, close_date is invalid -- " + close_date)
    try:
        f2 = float(Lineitem)
    except ValueError,e:
        return template("myerror.htm", user=request.user, msg="Error, Lineitem format is invalid -- "+ Lineitem)

        
    cx = sqlite.connect('branding.db')
    cu = cx.cursor()
    command = "insert into ussdefects values(NULL,'%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (component, number, title, Lineitem, open_date, close_date, poster, status, comment)
    cu.execute(command)
    cx.commit()
    cu.close()
    redirect("/USSdefect/defect/")

@USSdefect_app.route("/defect/modify/<did>/") 
@login_required
def defect_new(did):
    cx = sqlite.connect('branding.db')
    cu = cx.cursor()
    command = "select * from ussdefects where id=%s" %did
    cu.execute(command)
    rs = cu.fetchone()
    if rs == None:
        return template("myerror.htm", user=request.user, msg="Error,invalid defect id -- "+did)
    cu.close()
    
    did = rs[0]
    component = rs[1]
    number = rs[2]
    title = rs[3]
    Lineitem = rs[4]
    open_date = rs[5]
    close_date = rs[6]
    poster = rs[7]
    status = rs[8]
    comment = rs[9]
    

    return template("ussdefect/defect_modify.htm", user=request.user, did=did, component=component, number=number, title=title, Lineitem=Lineitem, 
                    open_date=open_date, close_date=close_date, poster=poster,status=status,comment=comment)


@USSdefect_app.route("/defect/modify/<did>/",method="POST") 
@login_required
def defect_modify_post(did):
    component = request.forms.get('component',"")
    number = request.forms.get('number',"")
    title = request.forms.get('title',"")
    Lineitem = request.forms.get('Lineitem',"")
    open_date = request.forms.get('open_date',"")
    close_date = request.forms.get('close_date',"")
    poster = request.forms.get('poster',"")
    status = request.forms.get('status',"")
    comment = request.forms.get('comment',"")

    component = component.replace("'","''")
    number = number.replace("'","''")
    title = title.replace("'","''")
    Lineitem = Lineitem.replace("'","''")
    open_date = open_date.replace("'","''")
    close_date = close_date.replace("'","''")
    poster = poster.replace("'","''")
    status = status.replace("'","''")
    comment = comment.replace("'","''")  
    
    if component == "":
        return template("myerror.htm", user=request.user, msg="Error,component is null!")
    if number == "":
        return template("myerror.htm", user=request.user, msg="Error, number is null!")
    if title == "":
        return template("myerror.htm", user=request.user, msg="Error,title is null!")
    if Lineitem == "":
        return template("myerror.htm", user=request.user, msg="Error,Lineitem is null!")
    if open_date == "":
        return template("myerror.htm", user=request.user, msg="Error,open_date is null!")
    if poster == "":
        return template("myerror.htm", user=request.user, msg="Error,poster is null!")
    if status == "":
        return template("myerror.htm", user=request.user, msg="Error,status is null!")
    m = date_p.match(open_date)
    if not m:
        return template("myerror.htm", user=request.user, msg="Error, open_date is invalid -- " + open_date)
    m = date_p.match(close_date)
    if close_date and not m:
        return template("myerror.htm", user=request.user, msg="Error, close_date is invalid -- " + close_date)
    try:
        f2 = float(Lineitem)
    except ValueError,e:
        return template("myerror.htm", user=request.user, msg="Error, Lineitem format is invalid -- "+ Lineitem)

        
    cx = sqlite.connect('branding.db')
    cu = cx.cursor()
    command = "update ussdefects set component='%s',number='%s',title='%s',Lineitem='%s',open_date='%s',close_date='%s',poster='%s',status='%s',comment='%s' where  id='%s';" % (component, number, title, Lineitem, open_date, close_date, poster, status, comment, did)
    cu.execute(command)
    cx.commit()
    cu.close()
    redirect("/USSdefect/defect/")


@USSdefect_app.route("/defect/delete/<did:int>/")                   #delete a user
@login_required
def user_delete(did):
    #if MessageBox(None, 'Do you confirm to delete this user?', 'Delete the user', 1)==1:
    cx = sqlite.connect('branding.db')
    cu = cx.cursor()
    command = "delete from ussdefects where id= '%s' " % did
    cu.execute(command)
    cx.commit()
    redirect("/USSdefect/defect/")

def create_month_range(start_year, start_month, end_year, end_month):
    if start_year*12+start_month > end_year*12+end_month:
        raise Exception("invalid parameter")
    year = start_year
    month = start_month
    while year*12+month <= end_year*12+end_month:
        #yield datetime.date(year,month,1)
        yield (year,month)
        if month < 12:
            month += 1
        else:
            month = 1
            year += 1

@USSdefect_app.route("/defect/draw/")                   #delete a user
@login_required
def defect_draw():
    result = []
    # create pic1,pic2,pic3
    result.append( create_defect_csv123() )
    result.append( create_pic(make_defect_py, defect_fun_fn1, defect_csv_fn1, defect_eps_fn1, defect_png_fn1) )
    result.append( create_pic(make_defect_py, defect_fun_fn2, defect_csv_fn2, defect_eps_fn2, defect_png_fn2) )
    result.append( create_pic(make_defect_py, defect_fun_fn3, defect_csv_fn3, defect_eps_fn3, defect_png_fn3) )
    return "<pre>\n"+"\n".join(result) +"</pre>\n"

def create_pic(targetpy, targetfun, targetcsv, targeteps, targetpng):
    result = []
    if sys.platform == "win32":
        command1 = targetpy + " " + targetfun + " " + targetcsv + " > " +targeteps
        command2 = "gswin64c -dBATCH -dNOPAUSE -dEPSCrop -sDEVICE=png16m -r300 -sOutputFile="+targetpng+" "+targeteps
    else:
        command1 = "python " + targetpy + " " + targetfun + " " + targetcsv + " > " +targeteps
        command2 = "gs -dBATCH -dNOPAUSE -dEPSCrop -sDEVICE=png16m -r300 -sOutputFile="+targetpng+" "+targeteps
    #print command1
    #time.sleep(1)
    t_f = os.popen(command1)
    result.append( t_f.read() )
    t_f = os.popen(command2)
    result.append( t_f.read() )
    return "\n".join(result)

def create_defect_csv123():   
    ''' create csv for 
         (1) increase number of open_defect and close_defect pic per month 
         (2) total number of open_defect and close_defect pic per month 
         (3) defect number of each member
    ''' 
    result = []
    result.append("<b>create_defect_csv1()</b>")
    Lineitem_filter = ["3204","133","133.1","1981"]

    # we only use the data between (START_YEAR,START_MONTH) and (CURRENT_YEAR, CURRENT_MONTH)
    START_YEAR = 2011
    START_MONTH = 9
    CURRENT_YEAR = datetime.date.today().year
    CURRENT_MONTH = datetime.date.today().month

    cx = sqlite.connect('branding.db')
    cu = cx.cursor()
    #cu.execute('select * from ussdefects')
    cu.execute('select max(open_date),min(open_date) from ussdefects')
    rs = cu.fetchall()
    
    max_date = rs[0][0]
    min_date = rs[0][1]

    m = date_p.match(min_date)
    if m:
        min_date_year = int(m.group("year"))
        min_date_month = int(m.group("month"))
    else:
        return template("myerror.htm", user=request.user, msg="Error, min(open_date) is invalid -- " + min_date)

    from_date_year = min(min_date_year, START_YEAR)
    from_date_month = min(min_date_month, START_MONTH)

    # get the month range for x_axis
    x_months = {}
    month_generator = create_month_range(from_date_year, from_date_month, CURRENT_YEAR, CURRENT_MONTH)
    for mm in month_generator:
        x_months[mm] = [0,0]   # first is number of open_defect,  second is number of close_defect
    

    cu.execute('select * from ussdefects')
    rs = cu.fetchall()  
    for r in rs:
        # calculate number of open defect for each month
        if r[4] not in Lineitem_filter:
            continue
            
        open_date = r[5]
        m = date_p.match(open_date)
        if m:
            year = int( m.group("year") )
            month = int( m.group("month") )
            open_number = x_months[(year,month)]
            open_number[0] += 1
            x_months[(year,month)] = open_number
        else:
            return template("myerror.htm", user=request.user, msg="Error, open_date is invalid, did-- " + str(r[0]))
            
        # calculate number of close defect for each month
        close_date = r[6]
        m = date_p.match(close_date)
        if m:
            year = int( m.group("year") )
            month = int( m.group("month") )
            close_number = x_months[(year,month)]
            close_number[1] += 1
            x_months[(year,month)] = close_number
        else:
            if close_date != "":
                return template("myerror.htm", user=request.user, msg="Error, close_date is invalid, did-- " + str(r[0]))        
    
    #pprint(x_months)
    result.append("&nbsp;&nbsp; read defects data successfully!")

    ###############################
    # output data to csv file1    #
    ###############################
    
    x_months2 = []
    for key,value in x_months.items():
        x_months2.append(["%d-%02d" % key,str(value[0]),str(value[1])])
    x_months2.sort()

    f1 = open(defect_csv_fn1,"w+")
    for x in x_months2:
        f1.write(",".join(x)+"\n")    
    f1.close()
    result.append("&nbsp;&nbsp; generate "+defect_csv_fn1+" successfully!")


    ###############################
    # output data to csv file2    #
    ###############################

    # x_months3 = [ ["%d-%02d" % x,0,0] for x in x_months.keys() ]
    # for m2 in x_months2:
    #     for m3 in x_months3:
    #         if m2[0] >= m3[0]:
    #             m3[1] += int(m2[1])
    #             m3[2] += int(m2[2])
    x_months3 = [ [x[0],int(x[1]),int(x[2])] for x in x_months2]
    lens3 = len(x_months3)
    if lens3 == 0:
        return template("myerror.htm", user=request.user, msg="Error, x_months3 is emptry ")
    for m3 in range(1,lens3):
        x_months3[m3][1] += x_months3[m3-1][1]
        x_months3[m3][2] += x_months3[m3-1][2]
    
    f1 = open(defect_csv_fn2,"w+")
    for x in x_months3:
        f1.write(x[0]+","+ str(x[1]) +"," +str(x[2]) + "\n")    
    f1.close()
    result.append("&nbsp;&nbsp; generate "+defect_csv_fn2+" successfully!")


    ###############################
    # output data to csv file3    #
    ###############################
    member_defects = {}
    for r in rs:
        # calculate number of open defect for each month
        if r[4] not in Lineitem_filter:
            continue        
        open_number = member_defects.get(r[7],0)
        open_number += 1
        member_defects[r[7]] = open_number
        
    f1 = open(defect_csv_fn3,"w+")
    for key,value in member_defects.items():
        f1.write(key+","+ str(value) + "\n")    
    f1.close()
    result.append("&nbsp;&nbsp; generate "+defect_csv_fn3+" successfully!")   

    return "<br>".join(result)



   
if __name__=="__main__":
    pass

