# coding:utf-8
# created time is 20:25:12 2012-03-21
# filename: user.py
# ywllyht@yahoo.com.cn

from bottle import route, run, Bottle, template, request, abort, redirect, response, hook
import sqlite3 as sqlite
import hashlib
#import md5
import bottle
import time
import ctypes
#MessageBox = ctypes.windll.user32.MessageBoxA 


# create table users(
#         id integer primary key,
#         username varchar(20),
#         fullname varchar(40),
#         email varchar(30),
#         password varchar(32)
# );                               
# insert into users values(NULL,"lljli","Li LiangJie","llilj@cn.ibm.com","860c85c91ca99778da806cd5a3b094c7");

users_app = Bottle()


class User(object):
    
    def __init__(self,userid=0,username="",role=""):
        self.userid = userid
        self.username = username
        self.role = role


def login_required(fn):
    #if username == "":
    #    abort(401,"sorry, you need to login first!")
    def _fn(*args, **kwargs):
        #from pprint import pprint
        #print request.path
        #print request.url
        #print request.urlparts
        #print request.fullpath
        #pprint(request.environ)
        
        if request.user.username == "":
            msg = 'sorry, you need to login first!'
	    return template("mydirect.htm",title="login required", msg=msg, next_url="/users/login/?next="+request.environ['REQUEST_URI'], user=request.user)
            #abort(401,'sorry, you need to login first!')
        return fn(*args,**kwargs)
    return _fn 


# @users_app.hook('before_request')
# def get_user_request():
#     userid = request.get_cookie("userid","0")
#     username = request.get_cookie("username","")
#     print "get_user_request",userid,username
#     request.user = User(userid,username)
    

@users_app.route("/")
@login_required
def index():
    return template("users/index.htm",user=request.user)


@users_app.route("/list/")
def user_list():
    cx = sqlite.connect('branding.db')
    cu = cx.cursor()
    cu.execute('select * from users')
    rs = cu.fetchall()
    #return str(rs)
    if request.user.role=="0":
       return template("users/list.htm",users=rs,title="user list",user=request.user)
    elif   request.user.role=="1":
       return template("users/list1.htm",users=rs,title="user list",user=request.user)
    else:
       msg = "Sorry,you don't have the authority!"
       return template("mydirect.htm",title="user list",msg=msg,next_url="/users/",user=request.user)

    
@users_app.route("/display/<userid:int>")
def user_display(userid):
    cx = sqlite.connect('branding.db')
    cu = cx.cursor()
    command = "select * from users where id= '%d' " % userid
    cu.execute(command)
    rs=cu.fetchone()
    return template("users/display.htm",users=rs,title="user display",user=request.user)  
    


#http://127.0.0.1:7070/views/users/add.htm
#@users_app.route("/add/",method="POST")
@users_app.route("/add/")
@login_required
def user_add():
    if request.user.role=='0' :
       return template("users/add.htm",title="add new user", user=request.user)
    else:
       msg = "Sorry,you don't have the authority!"
       return template("mydirect.htm",title="add new user",msg=msg,next_url="/users/",user=request.user)

@users_app.route("/add/",method="POST")
def user_add_post():
    username = request.forms.get('username')
    password = request.forms.get('password')
    fullname = request.forms.get('fullname')
    email = request.forms.get('email')
    role=request.forms.get('role')
    if not username:
        msg="sorry, the username should not be empty "
        return template("mydirect.htm",title="login successful",msg=msg,next_url="/users/add/",user=request.user) 
    if len(password) < 3 or len(password) > 15:
        msg="sorry, the length of password is invalid "
        return template("mydirect.htm",title="login successful",msg=msg,next_url="/users/add/",user=request.user) 
    
    m = hashlib.md5()
    m.update(password)
    password2 = m.hexdigest()
    #password2 = md5.md5(password).hexdigest()
    cx = sqlite.connect('branding.db')
    cu = cx.cursor()

    command = "select id,password,role from users where username = '%s'" % username
    cu.execute(command)
    rs = cu.fetchall()
    if len(rs) >= 1:
        abort(401,"sorry, username already exist! choose another username")

    command = "insert into users values(NULL,'%s','%s','%s','%s','%s')" % (username, fullname, email, password2,role)
    cu.execute(command)
    cx.commit()
    #print username+","+password+","+fullname+","+email+","+password2
    redirect("/users/list/")
    #return username+","+password+","+fullname+","+email


@users_app.route("/changepw/")                    #change password
@login_required
def user_changepw():
    userid = request.user.userid
    if userid == "0":
        msg = "You need to login first"
        return template("mydirect.htm",title="You need to login first",msg=msg,next_url="/users/login/",user=request.user) 
    cx = sqlite.connect('branding.db')
    cu = cx.cursor()
    cu.execute("select * from users where id='%s'" % userid)
    rs = cu.fetchone()
    return template("users/changepw.htm",users=rs,title="change password",user=request.user)

@users_app.route("/changepw/",method="POST")                    #change passwor
@login_required
def user_changepw_post():
    userid = request.user.userid
    if userid == "0":
        msg = "You need to login first"
        return template("mydirect.htm",title="You need to login first",msg=msg,next_url="/users/login/",user=request.user) 

    oldpassword = request.forms.get('oldpassword')
    newpassword = request.forms.get('newpassword')
    newpassword2 = request.forms.get('newpassword2')

    if len(newpassword) <= 4:
        msg = "The length password should > 4"
        return template("mydirect.htm",title="Error",msg=msg,next_url="/users/changepw/",user=request.user) 
    if newpassword != newpassword2:
        msg = "The two new password are not the same!"
        return template("mydirect.htm",title="Error",msg=msg,next_url="/users/changepw/",user=request.user) 
    if newpassword.find("'") >=0 or newpassword.find('"') >=0:
        msg = "You new password is illegal"
        return template("mydirect.htm",title="Error",msg=msg,next_url="/users/changepw/",user=request.user) 


    cx = sqlite.connect('branding.db')
    cu = cx.cursor()

    command = "select id,password,role from users where username = '%s'" % request.user.username
    cu.execute(command)
    rs = cu.fetchall()
    if len(rs) == 0:
        abort(401,"sorry, no such users")
    if len(rs) > 1:
        abort(401,"sorry, duplicated users found")

    m = hashlib.md5()
    m.update(oldpassword)
    password2 = m.hexdigest()

    if password2 != rs[0][1]:
        msg = "you password is not correct"
        return template("mydirect.htm",title="Error",msg=msg,next_url="/users/changepw/",user=request.user) 

    m = hashlib.md5()
    m.update(newpassword)
    password2 = m.hexdigest()

    command = "update users set password='%s' where id='%s'" % (password2, userid)
    cu.execute(command)
    cx.commit()
    redirect("/")


    return template("users/changepw.htm",users=rs,title="change password",user=request.user)




@users_app.route("/modify/<userid:int>/")                    #Modify a user
def user_modify(userid):
    cx = sqlite.connect('branding.db')
    cu = cx.cursor()
    cu.execute("select * from users where id='%d'" % userid)
    rs = cu.fetchone()
    return template("users/modify.htm",users=rs,title="modify user",user=request.user)
    
    

@users_app.route("/modify/<userid:int>/",method="POST")      #modify a user --'POST'
def user_modify_post(userid):
    username = request.forms.get('username')
    password = request.forms.get('password')
    fullname = request.forms.get('fullname')
    email = request.forms.get('email')
    role = request.forms.get('role')
    if not username:
        abort(401,"sorry, username should not be empty")
    if len(password) < 3 or len(password) > 32:
        abort(401,"sorry, the length of password is invalid")
    m = hashlib.md5()
    m.update(password)
    password2 = m.hexdigest()
    #password2 = md5.md5(password).hexdigest()
    cx = sqlite.connect('branding.db')
    cu = cx.cursor()
    command = "update users set username='%s',fullname='%s',email='%s', password='%s',role='%s' where id='%d'" % (username,fullname,email,password2,role, userid)
    cu.execute(command)
    cx.commit()
    redirect("/users/list/")
   


@users_app.route("/delete/<userid:int>")                   #delete a user
def user_delete(userid):
    #if MessageBox(None, 'Do you confirm to delete this user?', 'Delete the user', 1)==1:
    if 1==1:
      cx = sqlite.connect('branding.db')
      cu = cx.cursor()
      command = "delete from users where id= '%d' " % userid
      cu.execute(command)
      cx.commit()
      redirect("/users/list/")
    else:
      redirect("/users/list/")

@users_app.route("/login/")
def user_login():
    nexturl = request.query.next or ""
    #print nexturl
    return template("users/login.htm",title="login", nexturl=nexturl,user=request.user)

@users_app.route("/login/",method="POST")
def user_login_post():
    nexturl = request.query.next or "/"
    #print "post",nexturl
    username = request.forms.get('username')
    password = request.forms.get('password')
    if not username:
        abort(401,"sorry, username should not be empty")
    if len(password) < 3 or len(password) > 15:
        abort(401,"sorry, the length of password is invalid")
    m = hashlib.md5()
    m.update(password)
    password2 = m.hexdigest()
    #password2 = md5.md5(password).hexdigest()
    cx = sqlite.connect('branding.db')
    cu = cx.cursor()
    command = "select id,password,role from users where username = '%s'" % username
    cu.execute(command)
    rs = cu.fetchall()
    if len(rs) == 0:
        abort(401,"sorry, no such users")
    if len(rs) > 1:
        abort(401,"sorry, duplicated users found")
    #cx.commit()
    #print str(rs)
    #print username+","+password2+","+rs[0][1]
    if password2 == rs[0][1]:
        #response.set_cookie("username",username,path="/")
        #response.set_cookie("userid",str(rs[0][0]),path="/")

        s = request.environ.get('beaker.session')
        t = request.forms.get("two_weeks")
        if t:
            s.cookie[s.key]['path'] = s._path
            s.cookie[s.key]['expires'] = time.strftime("%a, %d-%b-%Y %H:%M:%S GMT", time.gmtime(time.time() + 86400*14))
            s._update_cookie_out()
        s['username'] = username
        s['userid'] = str(rs[0][0])
        s['role'] = str(rs[0][2])
        s.save()
        msg = "Login successful!"
        return template("mydirect.htm",title="login successful",msg=msg,next_url=nexturl,user=request.user)

    else:
        #return "password error"
        msg="password error,please login again!"
        if nexturl == "/":
            return template("mydirect.htm",title="login successful",msg=msg,next_url="/users/login/",user=request.user)
        else:
            return template("mydirect.htm",title="login successful",msg=msg,next_url="/users/login/?next="+nexturl,user=request.user)
    #redirect("../list/")


@users_app.route("/logout/")
def user_logout():
    #response.delete_cookie("username",path="/")
    #response.delete_cookie("userid",path="/")
    msg = "Logout successful!"

    s = request.environ.get('beaker.session')
    s.delete()
    return template("mydirect.htm",title="login required", msg=msg, next_url="/", user=request.user)




if __name__ == '__main__':
    bottle.debug(True)
    run(users_app,host="0.0.0.0",reloader=True)

 
