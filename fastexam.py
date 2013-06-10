# coding:utf-8

from bottle import route, run, Bottle, template, request, abort, redirect, static_file
import os
import sys
import time
import base64
import random
from users import login_required


_localDir = os.path.dirname(__file__)
_curpath = os.path.normpath(os.path.join(os.getcwd(),_localDir))
_uppath = os.path.dirname(_curpath)
_exampath = os.path.join(_uppath,"fastexam")

MYSPLIT = "^^"
MAX_CHOICE = 6   # only support 'A','B','C','D','E','F'   6 choice now

TITLE_FILE = "title.txt"
TEMPLATE1_FILE = "template1.txt" # 
END_FILE = "end.txt"             # if this examination is end
STUDENT_FILE = "student.txt"     # student's name,sn,noteid
SCORE_FILE = "score.txt"         # each user has a score file
PAPER_FILE = "paper.txt"         # each user's paper, generated from template1.txt


if not os.path.isdir(_exampath):
    os.makedirs(_exampath)

fastexam_app = Bottle()

@fastexam_app.route("/") 
def index():
    exams = []
    dirlist = os.listdir(_exampath)
    for dd in dirlist:
        dd2 = os.path.join(_exampath,dd)
        template1_fn = os.path.join(dd2,TEMPLATE1_FILE)
        end_fn = os.path.join(dd2,END_FILE)
        title_fn = os.path.join(dd2,TITLE_FILE)
        if os.path.isfile(title_fn) and os.path.isfile(template1_fn):
            title,per_score,number,use_number = parse_TITLE_FILE(title_fn)
            if title != "":
                exams.append((title,per_score,number,use_number,dd))

        
    
    return template("fastexam/index.htm",user=request.user,exams=exams)

@fastexam_app.route("/summary/<exam_path>/") 
def summary(exam_path):
    new_path2 = os.path.join(_exampath,exam_path)
    if not os.path.isdir(new_path2):
        return template("myerror.htm", user=request.user, msg="Error, exam_path path is empty")

    template1_fn = os.path.join(new_path2,TEMPLATE1_FILE)
    end_fn = os.path.join(new_path2,END_FILE)
    title_fn = os.path.join(new_path2,TITLE_FILE)

    title = ""
    per_score = ""
    number = ""      # total number of questions
    use_number = ""  # real number in a examination
    if os.path.isfile(title_fn) and os.path.isfile(template1_fn):
        title,per_score,number,use_number = parse_TITLE_FILE(title_fn)

    
    scores_path = os.path.join(new_path2,"scores")
    if not os.path.isdir(scores_path):
        os.mkdir(scores_path)

    students = []
    dirlist = os.listdir(scores_path)
    for dd in dirlist:
        student_path = os.path.join(scores_path,dd)
        # get studentinfo 
        student_fn1 = os.path.join(student_path,STUDENT_FILE)  
        name,snid,notesid = parse_STUDENT_FILE(student_fn1)  


        score = ""
        # judge is this paper submitted?
        score_fn = os.path.join(student_path,SCORE_FILE)
        if os.path.isfile(score_fn):
            f1 = open(score_fn)
            lines = f1.readlines()
            score = lines[0].strip()
            f1.close()
        students.append((name,snid,notesid,score,dd))
        
    return template("fastexam/summary.htm",user=request.user,students=students,title=title,per_score=per_score,
                    number=number,use_number=use_number, exam_path=exam_path)

    
@fastexam_app.route("/delscore/<exam_path>/<student_path0>/")
@login_required 
def delscore(exam_path,student_path0):
    new_path2 = os.path.join(_exampath,exam_path)
    if not os.path.isdir(new_path2):
        return template("myerror.htm", user=request.user, msg="Error, exam_path path is empty")

    scores_path = os.path.join(new_path2,"scores")
    if not os.path.isdir(scores_path):
        os.mkdir(scores_path)

    student_path = os.path.join(scores_path,student_path0)
    if not os.path.isdir(student_path):
        os.makedirs(student_path)

    dirlist = os.listdir(student_path)
    for dd in dirlist:
        dd2 = os.path.join(student_path,dd)
        os.remove(dd2)
    os.rmdir(student_path)
    
    redirect("../../../summary/"+exam_path+"/")

    
@fastexam_app.route("/displayscore/<exam_path>/<student_path0>/")
@login_required 
def displayscore(exam_path,student_path0):
    new_path2 = os.path.join(_exampath,exam_path)
    if not os.path.isdir(new_path2):
        return template("myerror.htm", user=request.user, msg="Error, exam_path path is empty")

    template1_fn = os.path.join(new_path2,TEMPLATE1_FILE)
    end_fn = os.path.join(new_path2,END_FILE)
    title_fn = os.path.join(new_path2,TITLE_FILE)
    
    title = ""
    per_score = ""
    number = ""
    use_number = ""
    if os.path.isfile(title_fn) and os.path.isfile(template1_fn):
        title,per_score,number,use_number = parse_TITLE_FILE(title_fn)
    

    scores_path = os.path.join(new_path2,"scores")
    if not os.path.isdir(scores_path):
        os.mkdir(scores_path)

    student_path = os.path.join(scores_path,student_path0)
    if not os.path.isdir(student_path):
        os.makedirs(student_path)

    # judge is this paper submitted?
    score_fn = os.path.join(student_path,SCORE_FILE)
    if not os.path.isfile(score_fn):
        return template("myerror.htm", user=request.user, msg="Error, score file is not exist!")
        
    f1 = open(score_fn)
    scorecontent = f1.read()
    f1.close()

    student_fn1 = os.path.join(student_path,STUDENT_FILE)  
    name,snid,notesid = parse_STUDENT_FILE(student_fn1) 
    
    return template("fastexam/displayscore.htm",user=request.user, title=title,number=number,use_number=use_number,per_score=per_score,scorecontent=scorecontent,
                    name=name, snid=snid, notesid=notesid, exam_path=exam_path)
    


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
    
    #print "title=",title
    #print "content=",repr(content)

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

    fn2 = os.path.join(new_path2, TITLE_FILE)
    f2 = open(fn2,"r")
    content2 = f2.read()
    f2.close()
    
    #content = content.replace("<","&lt;")
    #content = content.replace(">","&gt;")
    
    return template("fastexam/new_display.htm",user=request.user, content=content, content2=content2)




def parse_conent(content,title,new_path):
    questions = []
    number = 0
    # question=what is your age?
    # choice=A 6^^B 7^^C 8
    # answer_expect=A^^B

    per_score = ""
    use_number = ""
    qtype = ""
    question = ""
    choice = []
    answer_expect = []
    lines = content.splitlines()
    for i,line in enumerate(lines):
        #print i,line
        line = line.strip()
        if not line:
            continue
        if line.startswith("per_score"):
            if per_score != "":
                return "Error at line %d, duplicate per_score" % (i+1)
            sp1 = line.split("=",1)
            per_score = sp1[1]
        if line.startswith("use_number"):
            if use_number != "":
                return "Error at line %d, duplicate use_number" % (i+1)
            sp1 = line.split("=",1)
            use_number = sp1[1]            
        elif line.startswith("question="):
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
            elif len(choice) > MAX_CHOICE:
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
                if aa not in ['A','B','C','D','E','F']: # MAX_CHOICE=6
                    return "Error at line %d, illegal answer_expect, not in A B C D E F" % (i+1)
                    
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
                q_html.append('<div id="div_q_%d">' % number )
                q_n = "<p>%s</p>" % question
                q_html.append(q_n)
                base_choice = 65  # A
                for cc in choice:
                    q_n = "q_"+str(number)
                    check_html = '<input type=radio class="question" divid="div_q_%d" name="%s" value="%s">%s<p>' % (number, q_n,chr(base_choice),cc)
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
                q_html.append("</div>")
            else:
                # <p>question2</p>
                # <input type=checkbox name="q_2_A">Banana<p>
                # <input type=checkbox name="q_2_B" checked>Apple<p>
                # <input type=checkbox name="q_2_C">Orange<p>
                # <hiden name="q_1_expect" value="A_B">
                # <input type="hidden" name="q_1_type" value="multi_choice">
                q_html.append('<div id="div_q_%d">' % number )
                q_n = "<p>%s</p>" % question
                q_html.append(q_n)
                base_choice = 65
                for cc in choice:
                    q_n = "q_"+str(number)+"_"+chr(base_choice)
                    check_html = '<input type=checkbox class="question" divid="div_q_%d" name="%s">%s<p>' % (number,q_n,cc)
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
                q_html.append("</div>")

                
            q_html.append("END_QQ_"+str(number))
            
            questions.append("\n".join(q_html))
            number += 1
            qtype = ""
            question = ""
            choice = []
            answer_expect = []

    if int(use_number) > number:
          return "Error use_number:%s > total_number:%d" % (use_number,number)
    fn1 = os.path.join(new_path,TEMPLATE1_FILE)
    f1 = open(fn1,"w+")
    f1.write("\n".join(questions))
    f1.close()

    fn2 = os.path.join(new_path,TITLE_FILE)
    f2 = open(fn2,"w+")
    f2.write("title="+title+"\n")
    f2.write("per_score="+per_score+"\n")
    f2.write("number="+str(number)+"\n")
    f2.write("use_number="+use_number+"\n")
    f2.close()
    
    return "OK!"
    

def parse_TITLE_FILE(title_fn):
    f1 = open(title_fn)
    lines = f1.readlines()
    title = ""
    per_score = ""
    number = ""
    use_number = ""
    for line in lines:
        line = line.strip()
        if line.startswith("title="):
            sp1 = line.split("=",1)
            title = sp1[1]
        elif line.startswith("per_score="):
            sp1 = line.split("=",1)
            per_score = sp1[1]
        elif line.startswith("number="):
            sp1 = line.split("=",1)
            number = sp1[1]
        elif line.startswith("use_number="):
            sp1 = line.split("=",1)
            use_number = sp1[1]
    return (title,per_score,number,use_number)
    f1.close()

def parse_TEMPLATE1_FILE(template1_fn):
    questions = {}
    f1 = open(template1_fn)
    lines = f1.readlines()
    question = []
    flag = False
    q_number = -1
    for line in lines:
        line = line.strip()
        if line.startswith("START_QQ_"):
            flag = True
            sp1 = line.split("_",2)
            q_number = int(sp1[2])
        elif line.startswith("END_QQ_"):
            flag = False       
            questions[q_number] = "\n".join(question)
            question = []
        elif flag:
            question.append(line)
    f1.close()
    return questions


def parse_STUDENT_FILE(fn):
    f1 = open(fn)
    lines = f1.readlines()
    name = ""
    snid = ""
    notesid = ""
    for line in lines:
        line = line.strip()
        if line.startswith("name="):
            sp1 = line.split("=",1)
            name = sp1[1]
        elif line.startswith("snid="):
            sp1 = line.split("=",1)
            snid = sp1[1]
        elif line.startswith("notesid="):
            sp1 = line.split("=",1)
            notesid = sp1[1]
    return (name,snid,notesid)
    f1.close()

@fastexam_app.route("/start/<exam_path>/") 
def start(exam_path):
    new_path2 = os.path.join(_exampath,exam_path)
    if not os.path.isdir(new_path2):
        return template("myerror.htm", user=request.user, msg="Error, this path is empty")

    template1_fn = os.path.join(new_path2,TEMPLATE1_FILE)
    end_fn = os.path.join(new_path2,END_FILE)
    title_fn = os.path.join(new_path2,TITLE_FILE)

    title = ""
    per_score = ""
    number = ""
    use_number = ""
    if os.path.isfile(title_fn) and os.path.isfile(template1_fn):
        title,per_score,number,use_number = parse_TITLE_FILE(title_fn)
        #print "title=",title
        #print "number=",repr(number)
        #print "per_score=",repr(per_score)

    if title == "" or number == "":
        return template("myerror.htm", user=request.user, msg="Error, title is empty")
    if number == "" or not number.isdigit():
        return template("myerror.htm", user=request.user, msg="Error, number is illegal")
    if per_score == "" or not per_score.isdigit():
        return template("myerror.htm", user=request.user, msg="Error, per_score is illegal")
        
    return template("fastexam/start.htm",user=request.user, title=title,number=number,per_score=per_score,use_number=use_number)


@fastexam_app.route("/start/<exam_path>/",method="POST") 
def start_post(exam_path):
    new_path2 = os.path.join(_exampath,exam_path)
    if not os.path.isdir(new_path2):
        return template("myerror.htm", user=request.user, msg="Error, this path is empty")

    # get form information
    name = request.forms.get("name","")
    snid = request.forms.get("snid","")
    notesid = request.forms.get("notesid","")

    
    if not name:
        return template("myerror.htm", user=request.user, msg="Error, name is empty")

    if not snid or not snid.isdigit():
        return template("myerror.htm", user=request.user, msg="Error, sn is illegal")

    if not notesid:
        return template("myerror.htm", user=request.user, msg="Error, notesid is empty")

    # get metainfo from exam path
    template1_fn = os.path.join(new_path2,TEMPLATE1_FILE)
    end_fn = os.path.join(new_path2,END_FILE)
    title_fn = os.path.join(new_path2,TITLE_FILE)

    title = ""
    per_score = ""
    number = ""
    use_number = ""
    if os.path.isfile(title_fn) and os.path.isfile(template1_fn):
        title,per_score,number,use_number = parse_TITLE_FILE(title_fn)

    # generate random questions
    questions = parse_TEMPLATE1_FILE(template1_fn)
    total_number = int(number)
    use_number = int(use_number)
    range1 = range(total_number)
    range2 = random.sample(range1,use_number)
    questions2 = []

    #print range2
    for rr in range2:
        q = questions[rr]
        questions2.append(q)
    #from pprint import pprint
    #pprint(questions2)
    # make new dir
    time_1 = str(int(time.time()*1000))
    ip_1 = request.remote_addr.replace(".","")
    url_1 = time_1+"_"+ip_1



    scores_path = os.path.join(new_path2,"scores")
    if not os.path.isdir(scores_path):
        os.mkdir(scores_path)

    
    student_path = os.path.join(scores_path,url_1)
    if not os.path.isdir(student_path):
        os.makedirs(student_path)

    # write STUDENT_FILE
    student_fn1 = os.path.join(student_path,STUDENT_FILE)
    f1 = open(student_fn1,"w+")
    f1.write("name="+name+"\n")
    f1.write("snid="+snid+"\n")
    f1.write("notesid="+notesid+"\n")
    f1.close()

    # write PAPER_FILE
    paper_fn1 = os.path.join(student_path, PAPER_FILE)
    f1 = open(paper_fn1,"w+")
    for i,qq in enumerate(questions2):
        f1.write("<h3>"+str(i+1)+"</h3>\n")
        f1.write(qq+"\n")
    f1.close()
    
    #print "title=",title
    #print "content=",repr(content)


    redirect("../../start2/"+exam_path+"/"+url_1+"/")


@fastexam_app.route("/start2/<exam_path>/<student_path0>/") 
def start2(exam_path,student_path0):
    new_path2 = os.path.join(_exampath,exam_path)
    if not os.path.isdir(new_path2):
        return template("myerror.htm", user=request.user, msg="Error, exam_path path is empty")
    
    
    scores_path = os.path.join(new_path2,"scores")
    if not os.path.isdir(scores_path):
        os.mkdir(scores_path)

    
    student_path = os.path.join(scores_path,student_path0)
    if not os.path.isdir(student_path):
        os.makedirs(student_path)



    # get metainfo from exam path
    template1_fn = os.path.join(new_path2,TEMPLATE1_FILE)
    end_fn = os.path.join(new_path2,END_FILE)
    title_fn = os.path.join(new_path2,TITLE_FILE)

    title = ""
    per_score = ""
    number = ""
    use_number = ""
    if os.path.isfile(title_fn) and os.path.isfile(template1_fn):
        title,per_score,number,use_number = parse_TITLE_FILE(title_fn)

    # get studentinfo 
    student_fn1 = os.path.join(student_path,STUDENT_FILE)  
    name,snid,notesid = parse_STUDENT_FILE(student_fn1)  



    # judge is this paper submitted?
    score_fn = os.path.join(student_path,SCORE_FILE)
    if os.path.isfile(score_fn):
        f1 = open(score_fn)
        lines = f1.readlines()
        score = lines[0].strip()
        f1.close()
        return template("fastexam/score.htm",user=request.user, title=title,number=number,use_number=use_number,per_score=per_score,score=score,
                    name=name, snid=snid, notesid=notesid)
    else:
        # get paperinfo
        paper_fn1 = os.path.join(student_path,PAPER_FILE)
        f1 = open(paper_fn1)
        paper = f1.read()
        f1.close()

        return template("fastexam/start2.htm",user=request.user, title=title,number=number,use_number=use_number,per_score=per_score,paper=paper,
                    name=name, snid=snid, notesid=notesid)



@fastexam_app.route("/start2/<exam_path>/<student_path0>/",method="POST") 
def start2(exam_path,student_path0):
    new_path2 = os.path.join(_exampath,exam_path)
    if not os.path.isdir(new_path2):
        return template("myerror.htm", user=request.user, msg="Error, exam_path path is empty")
    
    
    scores_path = os.path.join(new_path2,"scores")
    if not os.path.isdir(scores_path):
        os.mkdir(scores_path)

    
    student_path = os.path.join(scores_path,student_path0)
    if not os.path.isdir(student_path):
        os.makedirs(student_path)

    # judge is this paper submitted?
    score_fn = os.path.join(student_path,SCORE_FILE)
    if os.path.isfile(score_fn):
        return template("myerror.htm", user=request.user, msg="Error, You have already submitted!")


    # get metainfo from exam path
    template1_fn = os.path.join(new_path2,TEMPLATE1_FILE)
    end_fn = os.path.join(new_path2,END_FILE)
    title_fn = os.path.join(new_path2,TITLE_FILE)

    title = ""
    per_score = ""
    number = ""
    use_number = ""
    if os.path.isfile(title_fn) and os.path.isfile(template1_fn):
        title,per_score,number,use_number = parse_TITLE_FILE(title_fn)
    per_score = int(per_score)
    
    # get studentinfo 
    student_fn1 = os.path.join(student_path,STUDENT_FILE)  
    name,snid,notesid = parse_STUDENT_FILE(student_fn1) 

    #for ee in request.forms:
    #    print ee,request.forms[ee]


    total_number = int(number)
    use_number = int(use_number)
    results = []
    score = 0
    for i in range(total_number):
        q_type = "q_"+str(i)+'_type'
        q_expect = "q_"+str(i)+"_expect"
        q_s   = "q_"+str(i)
        #q_m   = []
        #base_choice = 65
        #for j in range(MAX_CHOICE):
        #    q_m_0 = "q_"+str(i)+"_"+chr(base_choice)
        #    base_choice += 1
        #    q_m.append(q_m_0)
        #q_m_A = "q_"+str(i)+"_A"
        #q_m_B = "q_"+str(i)+"_B"
        #q_m_C = "q_"+str(i)+"_C"
        #q_m_D = "q_"+str(i)+"_D"
        #q_m_E = "q_"+str(i)+"_E"
        #q_m_F = "q_"+str(i)+"_F"    

        # check real info from POST
        q_type_2 = request.forms.get(q_type,"")
        if not q_type_2:
            continue
            #return template("myerror.htm", user=request.user, msg="Error, no type at question:"+str(i))
        q_expect2 = request.forms.get(q_expect,"")
        if not q_expect2:
            return template("myerror.htm", user=request.user, msg="Error, no expect at question:"+str(i))
        if q_type_2 == "single_choice":
            # q_0_type single_choice
            # q_expect cV8wX2V4cGVjdF5eQg==   | 'q_0_expect^^B'
            # q_0 B
            expect2 = base64.b64decode(q_expect2)
            sp1 = expect2.split(MYSPLIT) # ["q_0","B"]
            expect3 = sp1[1]  # B
            actual3 = request.forms.get(q_s,"")
            if actual3 == expect3:
                result = "OK"
                score += per_score
            else:
                result = "FAIL"
                # user did not answer this question

        elif q_type_2 == "multi_choice":
            # q_1_type multi_choice
            # q_1_expect cV8xX2V4cGVjdF5eQl5eRA==  | 'q_1_expect^^B^^D'
            # q_1_A on
            # q_1_C on
            expect2 = base64.b64decode(q_expect2)
            sp1 = expect2.split(MYSPLIT) # ["q_1","B","D"]
            expect3 = "".join(sp1[1:])  #BD
            actual1 = []
            base_choice = 65
            for j in range(MAX_CHOICE):
                q_m_0 = "q_"+str(i)+"_"+chr(base_choice)
                q_m_2 = request.forms.get(q_m_0,"")
                if q_m_2 == "on":
                    actual1.append(chr(base_choice))
                base_choice += 1
                #print i,q_m_0,q_m_2
            actual3 = "".join(actual1)
            if expect3 == actual3:
                result = "OK"
                score += per_score
            else:
                result = "FAIL"    
        else:
            return template("myerror.htm", user=request.user, msg="Error, illegal type at question:"+str(i)+","+q_type_2)
            
        line = "%d %s,expect:%s, actaul:%s" % (i,result,expect3, actual3)
        results.append(line)
            
    fn1 = os.path.join(student_path,SCORE_FILE)
    f1 = open(fn1,"w+")
    f1.write(str(score)+"\n")
    f1.write("\n".join(results))
    f1.close()


    redirect(".")






    