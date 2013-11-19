# coding:utf-8
# created time is 16:15:03 2013-02-21
# filename: Inter2013.py
# ywllyht@yahoo.com.cn

from bottle import route, run, Bottle, template, request, abort, redirect, static_file
import sqlite3 as sqlite                                                                                    
import os                                                                                                
import sys
import time
from users import login_required
from urllib import urlencode, unquote
import re


_curpath = os.path.dirname(__file__)
_uppath = os.path.dirname(_curpath)
words_en_path = os.path.join(_uppath,"words_en")

english_app = Bottle()

@english_app.route("/") 
def index():      
    searchtext = request.query.searchtext
    searchtext = searchtext.encode("utf-8")
    #print repr(searchtext)
    if len(searchtext) > 0:                       
        if not searchtext[0].isalpha():
            explanation2 = "Local DB does not support non-english words now!"
        else:
            explanation = readDic(searchtext)
            #print repr(explanation)
            explanation2 = explanation.decode("utf-8")
    else:
        explanation2 = "input your words!"
    return template("english/index.htm",title="English dictionary ",user=request.user,explanation2=explanation2,word=searchtext)


def readDic(word):
    if len(word) > 1:
        prefix = word[:2]
    else:
        prefix = "other"
    word_file_fn = prefix+".txt"
    word_file_path = os.path.join(words_en_path,word_file_fn)
    if not os.path.isfile(word_file_path):
        return "DictFile Path does not exist! "+word_file_fn

    f4 = open(word_file_path)
    lines_f4 = f4.readlines()
    f4.close()
    result = []
    flag = False
    for i,line in enumerate(lines_f4):
        #print i,flag,line
        if flag:
            #print "  ",line.find("--")
            if line.find("--") == 0:
                flag = False
                break
            result.append(line)
        else:
            if line.find("--"+word) == 0:
                flag = True
                continue
    if result:
        s = "".join(result)
        #print repr(s)
        return s
    else:
        return "can not find explanation for === " +word+" ==="
    #print repr(s2)
    #print s2.encode("gbk","ignore")

if __name__ == '__main__':                          
    run(english_app,host="0.0.0.0",reloader=True)             



