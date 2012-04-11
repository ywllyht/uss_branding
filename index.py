# coding:utf-8
# created time is 20:53:12 2012-03-21
# filename: index.py
# ywllyht@yahoo.com.cn

from bottle import Bottle, run,request, static_file
from bottle import template,view,SimpleTemplate
from users import users_app,User
from searchapp import search_app
from todo import todo_app
import os
from beaker.middleware import SessionMiddleware

index_app = Bottle()

_curpath = os.path.dirname(__file__)
_staticpath = os.path.join(_curpath,"static")
_beakerpath = os.path.join(os.path.dirname(_curpath),"beaker")

if not os.path.isdir(_beakerpath):
    os.mkdir(_beakerpath)

session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 86400,
    'session.data_dir': _beakerpath,
    'session.auto': True
}



@index_app.hook('before_request')
@users_app.hook('before_request')
@search_app.hook('before_request')
@todo_app.hook('before_request')
def get_user_request():
    #userid = request.get_cookie("userid","0")
    #username = request.get_cookie("username","")
    #print "get_user_request",userid,username

    s = request.environ.get('beaker.session')
    userid2 = s.get('userid',"0")
    username2 = s.get('username',"")
    request.user = User(userid2,username2)
    #print "get_user_request2",userid2,username2


# @search_app.hook('before_request')
# def get_user_request():
#     userid = request.get_cookie("userid","0")
#     username = request.get_cookie("username","")
#     print "get_user_request",userid,username
#     request.user = User(userid,username)


# @users_app.hook('before_request')
# def get_user_request():
#     userid = request.get_cookie("userid","0")
#     username = request.get_cookie("username","")
#     print "get_user_request",userid,username
#     request.user = User(userid,username)



index_app.mount("/users/",users_app)
index_app.mount("/search/",search_app)
index_app.mount("/todo/",todo_app)

@index_app.route('/')
def index():
    return template('index.htm',user=request.user)

@index_app.route('/static/<path:path>')
def statics(path):
    return static_file(path,root=_staticpath)

# @index_app.route('/search/')
# def search():
#     return template('search.htm',content="guest",user=request.user)


@index_app.route('/hello')
def hello():
    s = request.environ.get('beaker.session')
    s['test'] = s.get('test',0) + 1
    s.save()
    return "Hello World!" + ' Test counter: %d' % s['test']
    
@index_app.route('/favicon.ico')
def favicon():
    return static_file("favicon.ico", _curpath)


index_app_beaker = SessionMiddleware(index_app, session_opts)
if __name__ == '__main__':
    run(index_app_beaker,host="0.0.0.0",reloader=True)

