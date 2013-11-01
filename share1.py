# coding:utf-8
# created time is 13:43:08 2012-03-20
# filename: share1.py
# ywllyht@yahoo.com.cn

from bottle import Bottle, run, static_file

app = Bottle()

def html_escape(string):
    ''' Escape HTML special characters ``&<>`` and quotes ``'"``. '''
    return string.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')\
                 .replace('"','&quot;').replace("'",'&#039;')


@app.route('/hello')
def hello():
    return "Hello World!"


import os

curpath = os.path.dirname("__name__")
@app.route('/<path:path>')
def hello1(path):
    pa1 = os.path.join(curpath,path)
    return "<pre>"+html_escape(open(pa1).read())+"</pre>"
    #return static_file(path,curpath)
    #return "<pre>"+html_escape(open('users.py').read())+"</pre>"





if __name__ == '__main__':
    run(app,host="0.0.0.0",port=7070)

