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



_curpath = os.path.dirname(__file__)
_uppath = os.path.dirname(_curpath)
commentpath = os.path.join(_uppath,"SVT3_Intern_2013_comment")
if sys.platform == "win32":  # winXP, developer environment
    resumepath = os.path.join(_uppath,"SVT3_Intern_2013_resume")
else:                        # linux server, running environment
    resumepath = r'/home/lljli/ftp/temp/SVT3_Intern_2013'


Intern2013_app = Bottle()

@Intern2013_app.route("/") 
@login_required
def index():                                                                                               
    #log_time = time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime()) 
    resumelist = os.listdir(resumepath)
    #resumelist2 = map(lambda x:x.decode("gbk"), resumelist)
    return template("Intern2013/index.htm",title="SVT3 Intern 2013 ",user=request.user,resumes=resumelist)

# ajax interface for get #README content in log_view_all page
@Intern2013_app.route("/index_ajax/<resume_name>/") 
@login_required
def index_ajax(resume_name): 
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        resume_name2 = resume_name.decode("utf-8")
        slice1 = resume_name2.split(".",1)
        if len(slice1) != 2:
            return "name error, split fails! ",resume_name2
        resume_comment_name3 = slice1[0]+".txt"
        resume_comment_name4 = os.path.join(commentpath,resume_comment_name3)
        if not os.path.isfile(resume_comment_name4):
            comment2 = "No comment yet!"
        else:
            f1 = open(resume_comment_name4,"r")
            comment2 = f1.read()
            f1.close()
        return comment2
    else:
        return 'This is a normal request'


@Intern2013_app.route("/download/<resume_name>/") 
@login_required
def download(resume_name):
    #resume_name2 = unquote(resume_name)
    #print repr(resume_name)
    #print repr(resume_name2)
    resume_name2 = resume_name.decode("utf-8")
    return static_file(resume_name2,root=resumepath)

@Intern2013_app.route("/comment/<resume_name>/") 
@login_required
def comment(resume_name):
    #resume_name2 = unquote(resume_name)
    #print repr(resume_name)
    #print repr(resume_name2)
    resume_name2 = resume_name.decode("utf-8")
    slice1 = resume_name2.split(".",1)
    if len(slice1) != 2:
        return "name error, split fails! ",resume_name2
    resume_comment_name3 = slice1[0]+".txt"
    resume_comment_name4 = os.path.join(commentpath,resume_comment_name3)
    if not os.path.isfile(resume_comment_name4):
        f1 = open(resume_comment_name4,"w+")
        f1.close()
        comment2 = ""
    else:
        f1 = open(resume_comment_name4,"r")
        comment2 = f1.read()
        f1.close()
    template2 =   '''
  ------------------------------
  | interview record           |
  ------------------------------
  Score:        
  interview datetime:    
  graduate time:
  available time for Intern: 

  description:   

'''

    return template("Intern2013/comment.htm",title="SVT3 Intern 2013 ",user=request.user,resume_name=resume_name,comment2=comment2, template2=template2)

@Intern2013_app.route("/comment/<resume_name>/",method="post") 
@login_required
def comment_post(resume_name):
    #resume_name2 = unquote(resume_name)
    #print repr(resume_name)
    #print repr(resume_name2)
    resume_name2 = resume_name.decode("utf-8")
    slice1 = resume_name2.split(".",1)
    if len(slice1) != 2:
        return "name error, split fails! ",resume_name2
    resume_comment_name3 = slice1[0]+".txt"
    resume_comment_name4 = os.path.join(commentpath,resume_comment_name3)

    comment = request.forms.get('comment')
    f1 = open(resume_comment_name4,"a+")
    f1.write("     " + request.user.username+time.strftime("  %Y-%m-%d %H:%M:%S",time.gmtime()) +"\n")
    f1.write(comment+"\n")
    f1.write("---------------------------------------------------------------------------------\n\n")
    f1.close()

    return template("mydirect.htm",title="OK", msg="Add comment successful", next_url=".", user=request.user)




if __name__ == '__main__':                                                                                  
    run(search_app,host="0.0.0.0",reloader=True)             



