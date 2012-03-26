# coding:utf-8
# created time is 17:15:20 2012-03-22
# filename: test.py
# ywllyht@yahoo.com.cn

from bottle import Bottle, run
from bottle import static_file
import os

app = Bottle()

@app.route("/")
def index():
    return template("index.htm",content="Hello,world")

@app.route("/hello")
@app.route("/hello2")
def hello():
    return "<html><b>hello2</b></html>"

@app.route("/template/test1")
def test1():
    fd = open("views/test1.htm")
    lines = fd.readlines()
    return "".join(lines)

@app.route("/template/test2")
def test2():
    return open("views/test1.htm")

@app.route('/static/<path:path>')
def staticfile(path):
    return static_file(path,root="E:/Dropbox/test/python/Bottle/branding/static/")

@app.route('/static2/<path:path>')
def staticfile2(path):
    file1 = os.path.join("E:/Dropbox/test/python/Bottle/branding/static/",path)
    return open(file1)


from bottle import template
@app.route('/template1/')
@app.route('/template1/<name>')
def template1(name='World'):
    return template('template1.htm',name=name)






if __name__ == '__main__':
    run(app,reloader=True)
    

