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
import random
from pprint import pprint
from pychart import *
import subprocess

date_p = re.compile(r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})")

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

project_fun_fn0 = "ussproject0"
project_csv_fn0 = os.path.join(_defectpicpath,"ussproject0.csv")
project_eps_fn0 = os.path.join(_defectpicpath,"ussproject0.eps")
project_png_fn0 = os.path.join(_defectpicpath,"ussproject0.png")

project_fun_did = "ussprojectdid"

ussfvt_users = ["lljli","yoga","rucy","wenzhong"]
Lineitem_filter = ["3204","133","133.1","1981"]

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
    d_working = 0
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
        elif r[8] == "working":
            d_working += 1
        else:
            d_other += 1
    return template("ussdefect/defect.htm",user=request.user, defects=rs, d_total=d_total, d_open=d_open, d_verify=d_verify, d_close=d_close,
                    d_returned=d_returned, d_cancel=d_cancel, d_reject=d_reject, d_working=d_working, d_other=d_other)

@USSdefect_app.route("/defect/new/") 
@login_required
def defect_new():
    if request.user.username not in ussfvt_users:
        return template("myerror.htm", user=request.user, msg="Error,Only uss fvt members can visit here!")
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
def defect_modify(did):
    if request.user.username not in ussfvt_users:
        return template("myerror.htm", user=request.user, msg="Error,Only uss fvt members can visit here!")
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

    if status in ["close","cancel"] and close_date=="":
        return template("myerror.htm", user=request.user, msg="Error, you must input close_date for a close or cancel defect")
        
        
    cx = sqlite.connect('branding.db')
    cu = cx.cursor()
    command = "update ussdefects set component='%s',number='%s',title='%s',Lineitem='%s',open_date='%s',close_date='%s',poster='%s',status='%s',comment='%s' where  id='%s';" % (component, number, title, Lineitem, open_date, close_date, poster, status, comment, did)
    cu.execute(command)
    cx.commit()
    cu.close()
    redirect("/USSdefect/defect/")


@USSdefect_app.route("/defect/delete/<did:int>/")                   #delete a user
@login_required
def defect_delete(did):
    if request.user.username not in ussfvt_users:
        return template("myerror.htm", user=request.user, msg="Error,Only uss fvt members can visit here!")
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
    if request.user.username not in ussfvt_users:
        return template("myerror.htm", user=request.user, msg="Error,Only uss fvt members can visit here!")
        
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
    result.append(command1)
    #time.sleep(1)
    #t_f = os.popen(command1)
    p =  subprocess.Popen(command1,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE,)
    #p.stdout, p.stderr
    result.append( p.stdout.read() )
    result.append( p.stderr.read() )
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

################################################################################
#                                                                              #
#       projects part                                                          #
#                                                                              #
#                                                                              #
################################################################################
@USSdefect_app.route("/projects/") 
@login_required
def projects():
    cx = sqlite.connect('branding.db')
    cu = cx.cursor()
    cu.execute('select * from ussprojects')
    rs = cu.fetchall()

    return template("ussdefect/projects.htm",user=request.user, projects=rs,)

@USSdefect_app.route("/projects/new/") 
@login_required
def projects_new():
    if request.user.username not in ussfvt_users:
        return template("myerror.htm", user=request.user, msg="Error,Only uss fvt members can visit here!")
    return template("ussdefect/projects_new.htm", user=request.user)

@USSdefect_app.route("/projects/new/",method="POST") 
@login_required
def projects_new_post():
    name = request.forms.get('name',"")
    total_num = request.forms.get('total_num',"")
    current_attempt = request.forms.get('current_attempt',"0")
    current_succ = request.forms.get('current_succ',"0")
    draw_flag = request.forms.get('draw_flag',"")
    start_date = request.forms.get('start_date',"")
    end_date = request.forms.get('end_date',"")
    comment = request.forms.get('comment',"")
    
    name = name.replace("'","''")
    total_num = total_num.replace("'","''")
    current_attempt = current_attempt.replace("'","''")
    current_succ = current_succ.replace("'","''")
    draw_flag = draw_flag.replace("'","''")
    start_date = start_date.replace("'","''")
    end_date = end_date.replace("'","''")
    comment = comment.replace("'","''")   
    
    if name == "":
        return template("myerror.htm", user=request.user, msg="Error,name is null!")
    if total_num == "":
        return template("myerror.htm", user=request.user, msg="Error, total_num is null!")
    if current_attempt == "":
        return template("myerror.htm", user=request.user, msg="Error,current_attempt is null!")
    if current_succ == "":
        return template("myerror.htm", user=request.user, msg="Error,current_succ is null!")
    if draw_flag == "":
        return template("myerror.htm", user=request.user, msg="Error,draw_flag is null!")
    m = date_p.match(start_date)
    if not m:
        return template("myerror.htm", user=request.user, msg="Error, start_date is invalid -- " + open_date)
    m = date_p.match(end_date)
    if end_date and not m:
        return template("myerror.htm", user=request.user, msg="Error, end_date is invalid -- " + end_date)
    if end_date < start_date:
        return template("myerror.htm", user=request.user, msg="Error, end_date < start_date -- " + end_date+" , "+start_date)

        
    cx = sqlite.connect('branding.db')
    cu = cx.cursor()
    command = "insert into ussprojects values(NULL,'%s','%s','%s','%s','%s','%s','%s','%s');" % (name, total_num, current_attempt, current_succ, draw_flag, start_date, end_date, comment)
    cu.execute(command)
    cx.commit()
    cu.close()
    redirect("/USSdefect/projects/")


@USSdefect_app.route("/projects/modify/<did>/") 
@login_required
def projects_modify(did):
    if request.user.username not in ussfvt_users:
        return template("myerror.htm", user=request.user, msg="Error,Only uss fvt members can visit here!")
        
    cx = sqlite.connect('branding.db')
    cu = cx.cursor()
    command = "select * from ussprojects where id=%s" %did
    cu.execute(command)
    rs = cu.fetchone()
    if rs == None:
        return template("myerror.htm", user=request.user, msg="Error,invalid projects id -- "+did)
    cu.close()
    
    did = rs[0]
    name = rs[1]
    total_num = rs[2]
    current_attempt = rs[3]
    current_succ = rs[4]
    draw_flag = rs[5]
    start_date = rs[6]
    end_date = rs[7]
    comment = rs[8]
    

    return template("ussdefect/projects_modify.htm", user=request.user, did=did, name=name, total_num=total_num, current_attempt=current_attempt, current_succ=current_succ, 
                    draw_flag=draw_flag, start_date=start_date, end_date=end_date,comment=comment)


@USSdefect_app.route("/projects/modify/<did>/",method="POST") 
@login_required
def projects_modify_post(did):
    name = request.forms.get('name',"")
    total_num = request.forms.get('total_num',"")
    current_attempt = request.forms.get('current_attempt',"")
    current_succ = request.forms.get('current_succ',"")
    draw_flag = request.forms.get('draw_flag',"")
    start_date = request.forms.get('start_date',"")
    end_date = request.forms.get('end_date',"")
    comment = request.forms.get('comment',"")
    
    name = name.replace("'","''")
    total_num = total_num.replace("'","''")
    current_attempt = current_attempt.replace("'","''")
    current_succ = current_succ.replace("'","''")
    draw_flag = draw_flag.replace("'","''")
    start_date = start_date.replace("'","''")
    end_date = end_date.replace("'","''")
    comment = comment.replace("'","''")   
    
    if name == "":
        return template("myerror.htm", user=request.user, msg="Error,name is null!")
    if total_num == "":
        return template("myerror.htm", user=request.user, msg="Error, total_num is null!")
    if current_attempt == "":
        return template("myerror.htm", user=request.user, msg="Error,current_attempt is null!")
    if current_succ == "":
        return template("myerror.htm", user=request.user, msg="Error,current_succ is null!")
    if draw_flag == "":
        return template("myerror.htm", user=request.user, msg="Error,draw_flag is null!")
    m = date_p.match(start_date)
    if not m:
        return template("myerror.htm", user=request.user, msg="Error, start_date is invalid -- " + open_date)
    m = date_p.match(end_date)
    if end_date and not m:
        return template("myerror.htm", user=request.user, msg="Error, end_date is invalid -- " + end_date)
    if end_date < start_date:
        return template("myerror.htm", user=request.user, msg="Error, end_date < start_date -- " + end_date+" , "+start_date)

        
    cx = sqlite.connect('branding.db')
    cu = cx.cursor()
    command = "update ussprojects set name='%s',total_num='%s',current_attempt='%s',current_succ='%s',draw_flag='%s',start_date='%s',end_date='%s',comment='%s' where  id='%s';" % (name, total_num, current_attempt, current_succ, draw_flag, start_date, end_date, comment, did)
    cu.execute(command)
    cx.commit()
    cu.close()
    redirect("/USSdefect/projects/")
    
@USSdefect_app.route("/projects/delete/<did:int>/")                   #delete a user
@login_required
def projects_delete(did):
    if request.user.username not in ussfvt_users:
        return template("myerror.htm", user=request.user, msg="Error,Only uss fvt members can visit here!")
        
    #if MessageBox(None, 'Do you confirm to delete this user?', 'Delete the user', 1)==1:
    cx = sqlite.connect('branding.db')
    cu = cx.cursor()
    command = "delete from ussprojects where id= '%s' " % did
    cu.execute(command)

    command = "delete from ussproject where projectid= '%s' " % did
    cu.execute(command)
    
    cx.commit()
    #print "redirect hahaha"
    redirect("/USSdefect/projects/")

@USSdefect_app.route("/projects/project/list/<did>/") 
@login_required
def projects_project_list(did):
    cx = sqlite.connect('branding.db')
    cu = cx.cursor()

    cu.execute('select * from ussprojects where id='+did)
    rs = cu.fetchall()
    if len(rs) != 1:
        return template("myerror.htm", user=request.user, msg="Error, id is not existed in ussprojects -- " + did)
    r = rs[0]
    name = r[1]
    totalnum = r[2]
        
    cu.execute('select * from ussproject where projectid='+did)
    rs = cu.fetchall()

    rs2 = [ [x,float(x[5])/totalnum*100, float(x[6])/totalnum*100] for x in rs]
    

    return template("ussdefect/projects_project_list.htm",user=request.user, records=rs2, project=r)



@USSdefect_app.route("/projects/project/new/<did>/") 
@login_required
def projects_project_new(did):
    if request.user.username not in ussfvt_users:
        return template("myerror.htm", user=request.user, msg="Error,Only uss fvt members can visit here!")
        
    return template("ussdefect/projects_project_new.htm", user=request.user, did=did)

@USSdefect_app.route("/projects/project/new/<did>/",method="POST") 
@login_required
def projects_project_new_post(did):
    datepoint = request.forms.get('datepoint',"")
    plan_attempt = request.forms.get('plan_attempt',"")
    plan_succ = request.forms.get('plan_succ',"")
    actual_attempt = request.forms.get('actual_attempt',"")
    actual_succ = request.forms.get('actual_succ',"")
    comment = request.forms.get('comment',"")
    
    datepoint = datepoint.replace("'","''")
    plan_attempt = plan_attempt.replace("'","''")
    plan_succ = plan_succ.replace("'","''")
    actual_attempt = actual_attempt.replace("'","''")
    actual_succ = actual_succ.replace("'","''")
    comment = comment.replace("'","''")   
    
    if datepoint == "":
        return template("myerror.htm", user=request.user, msg="Error,datepoint is null!")
    if plan_attempt == "":
        plan_attempt = "0"
        #return template("myerror.htm", user=request.user, msg="Error, plan_attempt is null!")
    if plan_succ == "":
        plan_succ = "0"
        #return template("myerror.htm", user=request.user, msg="Error,plan_succ is null!")
    if actual_attempt == "":
        actual_attempt = "0"
        #return template("myerror.htm", user=request.user, msg="Error,actual_attempt is null!")
    if actual_succ == "":
        actual_succ = "0"
        #return template("myerror.htm", user=request.user, msg="Error,actual_succ is null!")

        
    cx = sqlite.connect('branding.db')
    cu = cx.cursor()
    command = "insert into ussproject values(NULL,'%s','%s','%s','%s','%s','%s','%s');" % (did, datepoint, plan_attempt, plan_succ, actual_attempt, actual_succ, comment)
    cu.execute(command)
    cx.commit()
    cu.close()
    redirect("/USSdefect/projects/project/list/"+did+"/")
    

@USSdefect_app.route("/projects/project/modify/<ddid>/") 
@login_required
def projects_project_modify(ddid):
    if request.user.username not in ussfvt_users:
        return template("myerror.htm", user=request.user, msg="Error,Only uss fvt members can visit here!")
        
    cx = sqlite.connect('branding.db')
    cu = cx.cursor()
    command = "select * from ussproject where id=%s" %ddid
    cu.execute(command)
    rs = cu.fetchone()
    if rs == None:
        return template("myerror.htm", user=request.user, msg="Error,invalid project id -- "+ddid)
    cu.close()
    
    ddid = rs[0]
    projectid = rs[1]
    datepoint = rs[2]
    plan_attempt = rs[3]
    plan_succ = rs[4]
    actual_attempt = rs[5]
    actual_succ = rs[6]
    comment = rs[7]

    

    return template("ussdefect/projects_project_modify.htm", user=request.user, ddid=ddid, projectid=projectid, datepoint=datepoint, plan_attempt=plan_attempt, plan_succ=plan_succ, 
                    actual_attempt=actual_attempt, actual_succ=actual_succ, comment=comment)


@USSdefect_app.route("/projects/project/modify/<ddid>/",method="POST") 
@login_required
def projects_project_modify_post(ddid):
    projectid = request.forms.get('projectid',"")
    datepoint = request.forms.get('datepoint',"")
    plan_attempt = request.forms.get('plan_attempt',"")
    plan_succ = request.forms.get('plan_succ',"")
    actual_attempt = request.forms.get('actual_attempt',"")
    actual_succ = request.forms.get('actual_succ',"")
    comment = request.forms.get('comment',"")

    current_flag = request.forms.get('current_flag',"")

    projectid = projectid.replace("'","''")
    datepoint = datepoint.replace("'","''")
    plan_attempt = plan_attempt.replace("'","''")
    plan_succ = plan_succ.replace("'","''")
    actual_attempt = actual_attempt.replace("'","''")
    actual_succ = actual_succ.replace("'","''")
    comment = comment.replace("'","''")   
    current_flag = current_flag.replace("'","''")


    if projectid == "":
        return template("myerror.htm", user=request.user, msg="Error,projectid is null!")
    if datepoint == "":
        return template("myerror.htm", user=request.user, msg="Error,datepoint is null!")
    if plan_attempt == "":
        plan_attempt = "0"
    if not plan_attempt.isdigit():
        return template("myerror.htm", user=request.user, msg="Error, plan_attempt is not number!")
        
    if plan_succ == "":
        plan_succ = "0"
    if not plan_succ.isdigit():
        return template("myerror.htm", user=request.user, msg="Error,plan_succ is not number!")
        
    if actual_attempt == "":
        actual_attempt = "0"
    if not actual_attempt.isdigit():
        return template("myerror.htm", user=request.user, msg="Error,actual_attempt is not number!")
        
    if actual_succ == "":
        actual_succ = "0"
    if not actual_succ.isdigit():
        return template("myerror.htm", user=request.user, msg="Error,actual_succ is not number!")

    if int(actual_attempt) < int(actual_succ):
        return template("myerror.htm", user=request.user, msg="Error,actual_attempt(" +actual_attempt +") < actual_succ(" + actual_succ +")")


    cx = sqlite.connect('branding.db')
    cu = cx.cursor()
    command = "select * from ussprojects where id=%s" % projectid
    cu.execute(command)
    rs = cu.fetchone()
    if rs == None:
        return template("myerror.htm", user=request.user, msg="Error,invalid projects id -- "+projectid)
    cu.close()
    

    total_num = rs[2]
    if int(actual_attempt) > total_num:
        return template("myerror.htm", user=request.user, msg="Error, actual_attempt(" +actual_attempt +") > total_num(" + str(total_num) +")")

        
    cx = sqlite.connect('branding.db')
    cu = cx.cursor()
    command = "update ussproject set datepoint='%s',plan_attempt='%s',plan_succ='%s',actual_attempt='%s',actual_succ='%s',comment='%s' where  id='%s';" % (datepoint, 
              plan_attempt, plan_succ, actual_attempt, actual_succ, comment, ddid)
    cu.execute(command)

    if current_flag == "on":
        command = "update ussprojects set current_attempt='%s',current_succ='%s' where  id='%s';" % (actual_attempt, actual_succ, projectid)
    cu.execute(command)
    
    cx.commit()
    cu.close()
    redirect("/USSdefect/projects/project/list/"+projectid+"/")
    

@USSdefect_app.route("/projects/project/delete/<ddid>/<projectid>/")                   #delete a user
@login_required
def projects_project_delete(ddid,projectid):
    if request.user.username not in ussfvt_users:
        return template("myerror.htm", user=request.user, msg="Error,Only uss fvt members can visit here!")
        
    #if MessageBox(None, 'Do you confirm to delete this user?', 'Delete the user', 1)==1:
    cx = sqlite.connect('branding.db')
    cu = cx.cursor()
    command = "delete from ussproject where id= '%s' " % ddid
    cu.execute(command)
    
    cx.commit()
    #print "redirect hahaha"
    redirect("/USSdefect/projects/project/list/"+projectid+"/")


@USSdefect_app.route("/projects/project/generate/<did>/") 
@login_required
def projects_project_generate(did):
    if request.user.username not in ussfvt_users:
        return template("myerror.htm", user=request.user, msg="Error,Only uss fvt members can visit here!")
        
    cx = sqlite.connect('branding.db')
    cu = cx.cursor()
    command = "select * from ussprojects where id=%s" %did
    cu.execute(command)
    rs = cu.fetchone()
    if rs == None:
        return template("myerror.htm", user=request.user, msg="Error,invalid projects id -- "+did)

    start_date = rs[6]
    end_date = rs[7]

    m = date_p.match(start_date)
    if not m:
         return template("myerror.htm", user=request.user, msg="Error, start_date is invalid -- " + start_date)
    #print map(lambda x:int(x),m.groups())
    #start_day = datetime.date(*map(lambda x:int(x),m.groups()))
    start_day = datetime.date(int(m.group("year")),int(m.group("month")),int(m.group("day")))
    
    m = date_p.match(end_date)
    if not m:
         return template("myerror.htm", user=request.user, msg="Error, end_date is invalid -- " + end_date)
    end_day = datetime.date(int(m.group("year")),int(m.group("month")),int(m.group("day")))
    print start_day, end_day

    weeks = []
    months = []
    day1 = start_day
    while day1 <= end_day:
        weeks.append("%d-%02d-%02d" % (day1.year, day1.month, day1.day) )
        day1 = day1 + datetime.timedelta(7)
        
    day1 = start_day
    while day1 <= end_day:
        months.append(day1)
        day1 = day1 + datetime.timedelta(30)
    #print weeks, months
    return template("ussdefect/projects_project_generate.htm", user=request.user, did=did, project=rs, weeks=weeks, months=months)

@USSdefect_app.route("/projects/project/generate/<did>/", method="post") 
@login_required
def projects_project_generate_post(did):

    cx = sqlite.connect('branding.db')
    cu = cx.cursor()
    command = "select * from ussprojects where id=%s" %did
    cu.execute(command)
    rs = cu.fetchone()
    if rs == None:
        return template("myerror.htm", user=request.user, msg="Error,invalid projects id -- "+did)

    name = rs[1]
    total_num = rs[2]
    current_attempt = rs[3]
    current_succ = rs[4]
    draw_flag = rs[5]
    start_date = rs[6]
    end_date = rs[7]
    comment = rs[8]

    m = date_p.match(start_date)
    if not m:
         return template("myerror.htm", user=request.user, msg="Error, start_date is invalid -- " + start_date)
    start_day = datetime.date(int(m.group("year")),int(m.group("month")),int(m.group("day")))
    
    m = date_p.match(end_date)
    if not m:
         return template("myerror.htm", user=request.user, msg="Error, end_date is invalid -- " + end_date)
    end_day = datetime.date(int(m.group("year")),int(m.group("month")),int(m.group("day")))
    #print start_day, end_day
    
    
    gflag = request.forms.get('gflag',"weekly")
    datepoints = []
    day1 = start_day
    if gflag == "weekly":
        while day1 <= end_day:
            datepoints.append("%d-%02d-%02d" % (day1.year, day1.month, day1.day) )
            day1 = day1 + datetime.timedelta(7)
    elif gflag == "monthly":
        while day1 <= end_day:
            datepoints.append("%d-%02d-%02d" % (day1.year, day1.month, day1.day) )
            day1 = day1 + datetime.timedelta(30)
    else:
        return template("myerror.htm", user=request.user, msg="Error, gflag is invalid -- " + gflag)

    ###############################################################
    #  generate data with different algorithem                    #
    #   (1) gtype == "empty"                                      #
    #     only generate datepoints                                #
    #   (2) gtype == "algorithm1"                                 # 
    #     generate datepoints, plan_attempts, plan_succs           #
    #   (3) gtype == "algorithm2"                                 # 
    #     generate datepoints, plan_attempts, plan_succs,          #
    #             actual_attempts, actual_succs                    #
    ###############################################################
    lens = len(datepoints)
    gtype = request.forms.get('gtype',"empty")
    if gtype == "empty":
        plan_attempts = [ 0 for x in xrange(lens)]
        plan_succs = [ 0 for x in xrange(lens)]
        actual_attempts = [ 0 for x in xrange(lens)]
        actual_succs = [ 0 for x in xrange(lens)]
    elif gtype == "algorithm1":
        if lens < 3:
            plan_attempts = random.sample(range(total_num),lens)
            plan_succs = random.sample(range(total_num),lens)
        else:
            plan_attempts = random.sample(range(total_num),lens-2)
            plan_succs = random.sample(range(total_num),lens-2)
     
            plan_attempts.append(total_num)
            plan_attempts.append(total_num)
            plan_succs.append(total_num)
            plan_succs.append(total_num)    
        actual_attempts = [ 0 for x in xrange(lens)]
        actual_succs = [ 0 for x in xrange(lens)]
    elif gtype == "algorithm2":
        if lens < 3:
            plan_attempts = random.sample(range(total_num),lens)
            plan_succs = random.sample(range(total_num),lens)
            actual_attempts = random.sample(range(total_num),lens)
            actual_succs = random.sample(range(total_num),lens)
        else:
            plan_attempts = random.sample(range(total_num),lens-2)
            plan_succs = random.sample(range(total_num),lens-2)
            actual_attempts = random.sample(range(total_num),lens-2)
            actual_succs = random.sample(range(total_num),lens-2)      
            plan_attempts.append(total_num)
            plan_attempts.append(total_num)
            plan_succs.append(total_num)
            plan_succs.append(total_num)
            actual_attempts.append(total_num)  
            actual_attempts.append(total_num)
            actual_succs.append(total_num)
            actual_succs.append(total_num)

    plan_attempts.sort()
    plan_succs.sort()
    actual_attempts.sort()
    actual_succs.sort()
    # make sure attempt >= succ
    for ii in range(lens):
        if plan_attempts[ii] < plan_succs[ii]:
            plan_attempts[ii], plan_succs[ii] =  plan_succs[ii], plan_attempts[ii]
        if actual_attempts[ii] < actual_succs[ii]:
            actual_attempts[ii], actual_succs[ii] = actual_succs[ii], actual_attempts[ii]
    
    #print "plan_attempts=", plan_attempts

    command = "delete from ussproject where projectid=%s" % did
    #print "command1=",command
    cu.execute(command)

    command = "update ussprojects set current_attempt='%s',current_succ='%s' where  id='%s';" % ("0", "0", did)
    cu.execute(command)

    
    for dd in range(lens):
        command = "insert into ussproject values(NULL,'%s','%s','%s','%s','%s','%s','%s');" % (did, datepoints[dd], plan_attempts[dd], plan_succs[dd], actual_attempts[dd], actual_succs[dd], "")
        #print "command2=",command
        cu.execute(command)
        
    cx.commit()

    
    redirect("/USSdefect/projects/project/list/"+did+"/")


def create_project_csv0():   
    result = []
    
    cx = sqlite.connect('branding.db')
    cu = cx.cursor()
    command = "select * from ussprojects where draw_flag=1"
    cu.execute(command)
    rs = cu.fetchall()

    data = []
    for r in rs:
        name = r[1]
        name = name.replace(",","")
        total_num = r[2]
        current_attempt = r[3]
        current_succ = r[4]
        
        step1 = float(current_succ)/total_num*100
        step2 = float(current_attempt - current_succ)/total_num*100
        step3 = float(total_num - current_attempt)/total_num*100

        perc1 = "%2.2f" % step1
        perc2 = "%2.2f" % step2
        perc3 = "%2.2f" % step3

        data.append((name,perc1,perc2,perc3))

    f1 = open(project_csv_fn0,"w+")
    for dd in data:
        f1.write(",".join(dd)+"\n")
    f1.close()
    
    result.append("generate "+project_fun_fn0+" successfully!")
    return "<br>".join(result)

def create_project_csv_did(did,name,total_num):   
    result = []
    

    
    name = name.replace(",","")
    total_num = str(total_num)

    cx = sqlite.connect('branding.db')
    cu = cx.cursor()
    cu.execute('select * from ussproject where projectid='+str(did))
    rs = cu.fetchall()

    fn1 = os.path.join(_defectpicpath,project_fun_did+str(did) +".csv")
    
    f1 = open(fn1,"w+")
    for dd in rs:
        datepoint = dd[2]
        datepoint = datepoint.replace(",","")
        plan_attempt = str(dd[3])
        plan_succ = str(dd[4])
        actual_attempt = str(dd[5])
        actual_succ = str(dd[6])
        f1.write(datepoint+","+plan_attempt+","+plan_succ+","+actual_attempt+","+actual_succ+"\n")
    f1.write(name+","+total_num+",0,0,0\n")
    f1.close()
    
    result.append("generate "+project_fun_did+str(did)+" successfully!")
    return "<br>".join(result)

# def create_project_csv_did2():   
#     result = []
#     
#     cx = sqlite.connect('branding.db')
#     cu = cx.cursor()
#     command = "select * from ussprojects where draw_flag=1"
#     cu.execute(command)
#     rs = cu.fetchall()
#     for r in rs:
#         result.append( create_project_csv_did(r[0], r[1], r[2]) )
#     return "<br>".join(result)


@USSdefect_app.route("/projects/draw/")                  
@login_required
def projects_draw():
    if request.user.username not in ussfvt_users:
        return template("myerror.htm", user=request.user, msg="Error,Only uss fvt members can visit here!")
        
    result = []
    # create percent progress pic for all projects
    result.append( create_project_csv0() )
    result.append( create_pic(make_defect_py, project_fun_fn0, project_csv_fn0, project_eps_fn0, project_png_fn0) )

    # create report pic for each progject
    cx = sqlite.connect('branding.db')
    cu = cx.cursor()
    command = "select * from ussprojects where draw_flag=1"
    cu.execute(command)
    rs = cu.fetchall()
    for r in rs:
        result.append( create_project_csv_did(r[0], r[1], r[2]) )
        project_fun_did_csv = os.path.join(_defectpicpath, project_fun_did+str(r[0])+".csv" )
        project_fun_did_eps = os.path.join(_defectpicpath, project_fun_did+str(r[0])+".eps" )
        project_fun_did_png = os.path.join(_defectpicpath, project_fun_did+str(r[0])+".png" )
        result.append( create_pic(make_defect_py, project_fun_did, project_fun_did_csv, project_fun_did_eps, project_fun_did_png) )
        
    return "<pre>\n"+"\n".join(result) +"</pre>\n"



if __name__=="__main__":
    pass

