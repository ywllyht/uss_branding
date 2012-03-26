# coding:utf-8
# created time is 20:53:12 2012-03-21
# filename: index.py
# ywllyht@yahoo.com.cn

from bottle import Bottle, run,request
from bottle import template,view,SimpleTemplate
from users import users_app,User
from searchapp import search_app
from todo import todo_app

app = Bottle()

@app.hook('before_request')
@users_app.hook('before_request')
@search_app.hook('before_request')
@todo_app.hook('before_request')
def get_user_request():
    userid = request.get_cookie("userid","0")
    username = request.get_cookie("username","")
    #print "get_user_request",userid,username
    request.user = User(userid,username)


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



app.mount("/users/",users_app)
app.mount("/search/",search_app)
app.mount("/todo/",todo_app)

@app.route('/')
def index():
    return template('index.htm',user=request.user)

# @app.route('/search/')
# def search():
#     return template('search.htm',content="guest",user=request.user)


@app.route('/hello')
def hello():
    return "Hello World!"


if __name__ == '__main__':
    run(app,host="0.0.0.0",reloader=True)

