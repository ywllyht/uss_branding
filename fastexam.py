# coding:utf-8

from bottle import route, run, Bottle, template, request, abort, redirect, static_file
import os
import sys
import time
import base64
from users import login_required


_localDir = os.path.dirname(__file__)
_curpath = os.path.normpath(os.path.join(os.getcwd(),_localDir))
_uppath = os.path.dirname(_curpath)
_exampath = os.path.join(_uppath,"fastexam")

MYSPLIT = "^^"

TEMPLATE1_FILE = "template1.txt" # 
END_FILE = "end.txt"             # if this examination is end

if not os.path.isdir(_exampath):
    os.makedirs(_exampath)

fastexam_app = Bottle()

@fastexam_app.route("/") 
def index():
    dirlist = os.listdir(_exampath)
    for dd in dirlist:
        dd2 = os.path.join(_exampath,dd)
        template1_fn = os.path.join(dd2,TEMPLATE1_FILE)
        end_fn = os.path.join(dd2,END_FILE)
        
    
    return template("fastexam/index.htm",user=request.user)

@fastexam_app.route("/new/") 
@login_required
def new():
    return template("fastexam/new.htm",user=request.user)


@fastexam_app.route("/new/",method="POST") 
@login_required
def new_post():
    time_1 = str(int(time.time()*1000))
    ip_1 = request.remote_addr.replace(".","")
    url_1 = time_1+"_"+ip_1
    new_path = os.path.join(_exampath,url_1)
    if not os.path.isdir(new_path):
        os.makedirs(new_path)

    title = request.forms.get("title","")
    content = request.forms.get("content","")

    if not title:
        return template("myerror.htm", user=request.user, msg="Error, title is empty")

    if not content:
        return template("myerror.htm", user=request.user, msg="Error, content is empty")
    
    print "title=",title
    print "content=",repr(content)

    r = parse_conent(content,title,new_path)
    print "r=",r
    if r == "OK!":
        redirect("../new_display/"+url_1+"/")
    else:
        return template("myerror.htm", user=request.user, msg=r)
    
@fastexam_app.route("/new_display/<exam_path>/") 
@login_required
def new_display(exam_path):
    new_path2 = os.path.join(_exampath,exam_path)
    if not os.path.isdir(new_path2):
        return template("myerror.htm", user=request.user, msg="Error, this path is empty")
        
    fn1 = os.path.join(new_path2, TEMPLATE1_FILE)
    f1 = open(fn1,"r")
    content = f1.read()
    f1.close()
    #content = content.replace("<","&lt;")
    #content = content.replace(">","&gt;")
    
    return template("fastexam/new_display.htm",user=request.user, content=content)




def parse_conent(content,title,new_path):
    questions = []
    number = 0
    # question=what is your age?
    # choice=A 6^^B 7^^C 8
    # answer_expect=A^^B
    
    qtype = ""
    question = ""
    choice = []
    answer_expect = []
    lines = content.splitlines()
    for i,line in enumerate(lines):
        print i,line
        line = line.strip()
        if not line:
            continue
        if line.startswith("question="):
            if question:
                return "Error at line %d, duplicate question" % (i+1)
            sp1 = line.split("=",1)
            question = sp1[1]
            if len(question) <= 1:
                return "Error at line %d, illegal question" % (i+1)
        elif line.startswith("choice="):
            if len(choice) != 0:
                return "Error at line %d, duplicate choice" % (i+1)
            sp1 = line.split("=",1)
            sp2 = sp1[1].split(MYSPLIT)
            choice = map(lambda x:x.strip(),sp2) # drop blanks
            if len(choice) <= 2:
                return "Error at line %d, illegal choice" % (i+1)
            elif len(choice) > 6:
                return "Error at line %d, too much choice" % (i+1)
        elif line.startswith("answer_expect="):
            if len(answer_expect)!=0:
                return "Error at line %d, duplicate answer_expect" % (i+1)
            sp1 = line.split("=",1)
            sp2 = sp1[1].split(MYSPLIT)
            answer_expect = map(lambda x:x.strip(),sp2)
            #print "sp1=",sp1
            #print "sp2=",sp2
            if len(answer_expect) < 1:
                return "Error at line %d, illegal answer_expect, length < 1" % (i+1)
            if len(answer_expect) > len(choice):
                return "Error at line %d, too much answer_expect" % (i+1)
            for aa in answer_expect:
                if aa not in ['A','B','C','D','E','F']:
                    return "Error at line %d, illegal answer_expect, not in ABCDEF" % (i+1)
                    
            if not question:
                return "Error at line %d, question is empty when generating q_html" % (i+1)
            if len(choice) == 0:
                return "Error at line %d, choice is empty when generating q_html" % (i+1)

            
            if len(answer_expect) > 1:
                qtype = "multi_choice"
            else:
                qtype = "single_choice"

            q_html = []
            q_html.append("START_QQ_"+str(number))
            if qtype == "single_choice":
                # <p>question1</p> 
                # <input type=radio name="q_1" value="A" checked> None
                # <input type=radio name="q_1" value="B"> logo_zswpublish
                # <input type=radio name="q_1" value="C"> logo_huitailang
                # <input type="hidden" name="q_1_expect" value="A">
                # <input type="hidden" name="q_1_type" value="single_choice">
                q_n = "<p>%s</p>" % question
                q_html.append(q_n)
                base_choice = 65  # A
                for cc in choice:
                    q_n = "q_"+str(number)
                    check_html = '<input type=radio name="%s" value="%s">%s<p>' % (q_n,chr(base_choice),cc)
                    q_html.append(check_html)
                    base_choice += 1
                    
                q_n = "q_"+str(number)+"_expect"
                q_answer_expect = answer_expect[0]
                q_base64value = base64.b64encode(q_n+MYSPLIT+q_answer_expect)
                hidden_html = '<input type="hidden" name="%s" value="%s">' %(q_n,q_base64value)
                q_html.append(hidden_html)

                q_n = "q_"+str(number)+"_type"
                hidden_html = '<input type="hidden" name="%s" value="single_choice">' % q_n
                q_html.append(hidden_html)
            else:
                # <p>question2</p>
                # <input type=checkbox name="q_2_A">Banana<p>
                # <input type=checkbox name="q_2_B" checked>Apple<p>
                # <input type=checkbox name="q_2_C">Orange<p>
                # <hiden name="q_1_expect" value="A_B">
                # <input type="hidden" name="q_1_type" value="multi_choice">
                q_n = "<p>%s</p>" % question
                q_html.append(q_n)
                base_choice = 65
                for cc in choice:
                    q_n = "q_"+str(number)+"_"+chr(base_choice)
                    check_html = '<input type=checkbox name="%s">%s<p>' % (q_n,cc)
                    q_html.append(check_html)
                    base_choice += 1
                    
                q_n = "q_"+str(number)+"_expect"
                q_answer_expect = MYSPLIT.join(answer_expect)
                q_base64value = base64.b64encode(q_n+MYSPLIT+q_answer_expect)
                hidden_html = '<input type="hidden" name="%s" value="%s">' %(q_n,q_base64value)
                q_html.append(hidden_html)

                
                q_n = "q_"+str(number)+"_type"
                hidden_html = '<input type="hidden" name="%s" value="multi_choice">' % q_n
                q_html.append(hidden_html)

                
            q_html.append("END_QQ_"+str(number))
            
            questions.append("\n".join(q_html))
            number += 1
            qtype = ""
            question = ""
            choice = []
            answer_expect = []
            
    fn1 = os.path.join(new_path,TEMPLATE1_FILE)
    f1 = open(fn1,"w+")
    f1.write("\n".join(questions))
    f1.close()
    return "OK!"
    

