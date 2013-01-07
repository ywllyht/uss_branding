# coding:utf-8
# created time is 16:15:03 2012-03-26
# filename: searchapp.py
# ywllyht@yahoo.com.cn

from bottle import route, run, Bottle, template, request, abort, redirect                                   
import sqlite3 as sqlite                                                                                    
import os                                                                                                
import time
from users import login_required


separator = "%%^^\t"

 #  return "unimplemented"                                                                                  
_curpath = os.path.dirname(__file__)
_uppath = os.path.dirname(_curpath)
AQpath = os.path.join(_uppath,"AQUSS")
datasetpath = os.path.join(AQpath,"dataset")
new2012path = os.path.join(datasetpath,"2012")       # this directory contains new data files which uses upload, from 2012 !
#AQpath = r"E:\test\python\Bottle\AQUSS"
#new2012path = r"E:\test\python\Bottle\AQUSS\dataset\2012\"


#VSU_ALLOW_LIST = ["PASS","UNSUPPORTED","UNTESTED","FIP","WARNING","NOTINUSE"]
VSU_ALLOW_LIST = ["PASS","UNSUPPORTED","UNTESTED","WARNING","NOTINUSE"]
VSC_ALLOW_LIST = ["PASS","UNSUPPORTED","UNTESTED","WARNING","NOTINUSE","NOT_IMPLEMENTED","UNAPPROVED_ASSERTION"]

search_app = Bottle()

case_catalog_list = [
    #"INSTALL",
    #"PROBLEM",
    "VSC5",
    "VST5",
    "VSU5",
    "VSX4",
    #"ZOSR12",
    ]


keyword_catalog_list = [
    "INSTALL",
    "problem",
    #"VSC5",
    #"VST5",
    #"VSU5",
    #"VSX4",
    #"ZOSR12",
    ]



@search_app.route("/") 
@login_required
def search():                                                                                               
    searchtext = request.query.searchtext                                                                   
    #searchtext = searchtext.encode("utf-8")
    #print searchtext                                                                                        
    #print request.query.searchtext                                                        
    log_time = time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime()) 
    return template("search/index.htm",title="USS FVT Search ",user=request.user, log_time=log_time)
    # if searchtext == "":                                                                                    
    #     return template("search/index.htm",title="USS FVT Search ",user=request.user)                           
    # else:    
    #     search_targs = []
    #     for s in keyword_catalog_list:
    #         try:
    #             r = request.query[s]
    #             search_targs.append(s)
    #         except KeyError,e:
    #             pass
        
    #     search_result = []
    #     for s in search_targs:
    #         r = keyword_search1(s,searchtext)
    #         search_result.append((s,r))
    #     #print search_result
    #     return template("search/result.htm",title="USS FVT Search result",rs=search_result, user=request.user)                           

# print search_result
# [
#   ('PROBLEM', ["ddaa1,fffff", "dataa2, linesss","dtaa3,lin"]),
#   ('VSC5', ["dataa1,fasdfas", "dtaaa2,fdfsa"]),
# ]                                                                                 


@search_app.route("/case_search") 
@login_required
def case_search():                                                                                               
    searchtext = request.query.searchtext
    #searchtext = searchtext.encode("utf-8")
    #print searchtext                                                                                        
    #print request.query.searchtext                                                                          
    if searchtext == "":                                                                                    
        return template("search/index.htm",title="USS FVT Search ",user=request.user)                           
    else:    
        try:
            case_catalog = request.query['case_catalog']
        except KeyError,e:
            return "You should choose a catalog first, such as VSC5, VSU5..."
        searchtext = searchtext.strip()
        if searchtext == "":
            return "inpurt parameter format error 1 ! you should input case_name and case_number, like 'sendmsg.ex 255'"
        sp = searchtext.split()
        if len(sp) != 2:
            return "inpurt parameter format error 2 ! you should input case_name and case_number, like 'sendmsg.ex 255'"
        case_name = sp[0]
        case_no = sp[1]

        search_result = []

        code,r = PIN_search1(case_catalog,case_name,case_no)
        if code != "OK":
            return "PIN search Fail! "+code+","+r
        search_result.append(("PIN "+case_catalog+" "+case_name+" "+case_no,r))

        code,r = case_search1(case_catalog,case_name,case_no)
        if code != "OK":
            return "case search Fail! "+code+","+r
        search_result.append((case_catalog+" "+case_name+" "+case_no,r))

        #print search_result
        return template("search/result1.htm",title="USS FVT Case Search result",rs=search_result, user=request.user)                           


@search_app.route("/keyword_search") 
@login_required
def keyword_search():                                                                                               
    searchtext = request.query.searchtext                                                                   
    #searchtext = searchtext.encode("utf-8")
    #print searchtext                                                                                        
    #print request.query.searchtext                                                                          
    if searchtext == "":                                                                                    
        return template("search/index.htm",title="USS FVT Search ",user=request.user)                           
    else:    
        search_targs = []
        for s in keyword_catalog_list:
            try:
                r = request.query[s]
                search_targs.append(s)
            except KeyError,e:
                pass
        
        search_result = []
        for s in search_targs:
            r = keyword_search1(s,searchtext)
            search_result.append((s,r))
        #print search_result
        return template("search/result.htm",title="USS FVT KeyWord Search result",rs=search_result, user=request.user)                           



@search_app.route("/log_upload",method="POST") 
@login_required
def log_upload():     
    ##################################################
    #                                                #
    # this function only parse JOURNAL, and generate #
    # 2 files.                                       #
    # (1) $READ                                      #
    # (2) FAILURES                                   #
    #                                                #
    ##################################################
    analytic_result = "getting parameters from web page...\n"
    ##########################
    # get parameters         #
    ##########################
    try:
        case_catalog = request.forms['case_catalog']
    except KeyError,e:
        return "You should choose a catalog first, such as VSC5, VSU5..."  

    try:
        log_version = request.forms['log_version']
    except KeyError,e:
        return "You should input a version first, such as V533, V474..." 
    log_version = log_version.strip()
    if not log_version:
        return "You should input a version first, such as V533, V474......" 
    if len(log_version) > 6:
        return "version length should not be greater than 6"
    if not log_version.isalnum():
        return "version format error! only alphanumeric character is legal"
    log_version = log_version.upper()


    try:
        log_time = request.forms['log_time']
    except KeyError,e:
        return "You should input the log time(GMT) when you kick off this test"

    log_comment = ""
    try:
        log_comment = request.forms['log_comment']
    except KeyError,e:
        return "You should input a version first, such as V533, V474..." 
    
    #print "case_catalog=",case_catalog
    #print "log_version=",log_version
    #print "log_comment=",log_comment
    if len(request.user.username) > 8:
        newusername = request.user.username[:8]
    else:
        newusername = request.user.username

    log_time2 = time.strftime("D%y%m%d.T%H%M%S",time.gmtime()) 


    data = request.files.data
    #print "data=",data
    try:
        filename = data.filename
    except AttributeError,e:
        return "You should choose the log file"
    #print "filename=",filename

    analytic_result += "  log_version="+log_version+"\n"
    analytic_result += "  log_time="+log_time+"\n"
    analytic_result += "  log_comment="+log_comment+"\n"
    
    
    analytic_result += "create directory and files...\n"
    ###################################
    # create directory and files      #
    ###################################
    newdirname = "POSIX.CMPL."+case_catalog+"."+log_version+"."+newusername+"."+log_time2
    newdirname = newdirname.upper()
    newdirname2 = os.path.join(new2012path,newdirname)
    if not os.path.isdir(newdirname2):
        os.mkdir(newdirname2)

    analytic_result += "create directory "+ newdirname+"\n"

    newjournal_name = "JOURNAL"
    newjournal_name2 = os.path.join(newdirname2,newjournal_name)
    f1 = open(newjournal_name2,"wb+")
    read_length_total = 0
    #print data
    while True:
        r = data.file.read(4096)
        #print read_length_total,repr(r)
        read_length = len(r)
        read_length_total += read_length
        f1.write(r)
        if read_length == 0:
            break
        if read_length_total > 50000000:  # 40M is the max limition
            break

    f1.close()

    analytic_result += "create JOURNAL, write bytes "+str(read_length_total)+"\n"

    newreadme_name = "$README"
    newreadme_name2 = os.path.join(newdirname2,newreadme_name)
    f1 = open(newreadme_name2,"w+")
    f1.write("username:     " + request.user.username + "\n")
    f1.write("catalog:      " + case_catalog + "\n")
    f1.write("case_version: " + log_version + "\n")
    f1.write("run time:     " + log_time + "\n")
    f1.write("comment:      " + log_comment + "\n")
    f1.close()

    analytic_result += "create $README\n"

    
    newfailures_name = "FAILURES"
    newfailures_name2 = os.path.join(newdirname2,newfailures_name)
    if case_catalog == "VSU5":
        r = vsu_parse(newjournal_name2, newfailures_name2, case_catalog, log_version)
    elif case_catalog == "VSX4":
        r = vsu_parse(newjournal_name2, newfailures_name2, case_catalog, log_version)
    elif case_catalog == "VSC5":
        r = vsc_parse(newjournal_name2, newfailures_name2, case_catalog, log_version)
    elif case_catalog == "VST5":
        r = vst_parse(newjournal_name2, newfailures_name2, case_catalog, log_version)
    else:
        r = "unsupported!"
    
    analytic_result += r

    return template("search/log_upload.htm",title="USS FVT LOG UPLOAD",analytic_result=analytic_result, logdir=newdirname, user=request.user)  


@search_app.route("/log_view/<logdir>") 
@login_required
def log_view(logdir):   
    newdirname2 = os.path.join(new2012path,logdir)
    if not os.path.isdir(newdirname2):
        return "Error! "+logdir+" does not exist!"
    filelists = os.listdir(newdirname2)
    filelist2 = []
    f1 = lambda x:time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(x))
    for file1 in filelists:
        file2 = os.path.join(newdirname2,file1)
        st = os.stat(file2)
        mode,ino,dev,nlink,uid,gid,size,atime,mtime,ctime = st
        filelist2.append((file1,oct(mode),uid,size,f1(ctime),f1(mtime)))
    
    readme_content = ""
    newreadme_name = "$README"
    newreadme_name2 = os.path.join(newdirname2,newreadme_name)
    if os.path.isfile(newreadme_name2):
        #print "read readme!"
        f1 = open(newreadme_name2)
        lines = f1.readlines()
        f1.close()
        read_max = min(10,len(lines))
        readme_content = "".join(lines[:read_max]) #dislay the first 10 lines of $readme
    #print newreadme_name2
    #print "readme_content=",readme_content
    return  template("search/log_view.htm",title="USS FVT LOG VIEW",logdir=logdir, filelist2=filelist2, readme_content=readme_content, user=request.user)  

@search_app.route("/log_delete/<logdir>") 
@login_required
def log_delete(logdir):   
    newdirname2 = os.path.join(new2012path,logdir)
    if not os.path.isdir(newdirname2):
        return "Error! "+logdir+" does not exist!"


    newdirname_delete = logdir+"_delete"
    newdirname_delete2 = os.path.join(new2012path,newdirname_delete)
    if os.path.isdir(newdirname_delete):
        return "Error! "+newdirname_delete+" already exists!"
    
    newreadme_name = "$README"
    newreadme_name2 = os.path.join(newdirname2,newreadme_name)
    if os.path.isfile(newreadme_name2):
        #print "read readme!"
        f1 = open(newreadme_name2,"a")
        f1.write(request.user.username+" attemped to delete this directory at "+ time.ctime()+"\n")
        f1.close()

    os.rename(newdirname2,newdirname_delete2)
    #print "readme_content=",readme_content
    redirect("../log_view/"+newdirname_delete)
    #return template("mydirect.htm",title="user list",msg=msg,next_url="../log_view/"+logdir,user=request.user)
        


@search_app.route("/log_view_all") 
@login_required
def log_view_all():   
    if not os.path.isdir(new2012path):
        return "Error! "+os.path.basename(new2012path)+" directory does not exist!"
    dirlists = os.listdir(new2012path)
    dirlists.sort()

    return  template("search/log_view_all.htm",title="USS FVT LOG VIEW",dirlists=dirlists, user=request.user)  


# ajax interface for get #README content in log_view_all page
@search_app.route("/log_view_file_ajax/<logdir>/<logfile>/") 
@login_required
def log_view_readme_ajax(logdir,logfile): 
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        newdirname2 = os.path.join(new2012path,logdir)
        if not os.path.isdir(newdirname2):
            return "Error! "+logdir+" does not exist or it is not a directory!"
        newfilename2 = os.path.join(newdirname2,logfile)
        if not os.path.isfile(newfilename2):
            return "Error! " + logdir + "("+logfile+") dos not exist or it is not a file!"
        f1 = open(newfilename2)
        content = f1.read()
        f1.close()
        return content
    else:
        return 'This is a normal request'


# view each file($README,FAILURES) under target directory
@search_app.route("/log_view_file/<logdir>/<logfile>/") 
@login_required
def log_view_file(logdir,logfile):   
    newdirname2 = os.path.join(new2012path,logdir)
    if not os.path.isdir(newdirname2):
        return "Error! "+logdir+" does not exist or it is not a directory!"
    newfilename2 = os.path.join(newdirname2,logfile)
    if not os.path.isfile(newfilename2):
        return "Error! " + logdir + "("+logfile+") dos not exist or it is not a file!"
    f1 = open(newfilename2)
    content = f1.read()
    f1.close()

    return  template("search/log_view_file.htm",title="USS FVT LOG VIEW",logdir=logdir, logfile=logfile, content=content, user=request.user)  

# view each file($README,FAILURES) under target directory
@search_app.route("/log_view_file/<logdir>/<logfile>/",method="POST") 
@login_required
def log_view_file(logdir,logfile):   
    newdirname2 = os.path.join(new2012path,logdir)
    if not os.path.isdir(newdirname2):
        return "Error! "+logdir+" does not exist or it is not a directory!"
    newfilename2 = os.path.join(newdirname2,logfile)
    if not os.path.isfile(newfilename2):
        return "Error! " + logdir + "("+logfile+") dos not exist or it is not a file!"
    content = request.forms.content
    lines = content.splitlines()
    result = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if len(line) > 255:
            line = line[:255]
        result.append(line)

    total_lenth = reduce(lambda x,y:x+y+1,map(len,result))
    f1 = open(newfilename2,"w+")
    f1.write("\n".join(result))
    f1.close()
             

    msg = "modify successful! " + str(total_lenth) + " bytes written!"
    return template("mydirect.htm",title="user list",msg=msg,next_url="../../../log_view/"+logdir,user=request.user)




@search_app.route("/log_analytic/<logdir>") 
@login_required
def log_analytic(logdir):   
    newdirname2 = os.path.join(new2012path,logdir)
    if not os.path.isdir(newdirname2):
        return "Error! "+logdir+" does not exist!"
    newfailures_name = "FAILURES"
    newfailures_name2 = os.path.join(newdirname2,newfailures_name)
    if not os.path.isfile(newfailures_name2):
        return "Error! "+newfailures_name+" does not exist!"


    case_catalog = ""
    for catalog in ["VSC5","VSU5","VSX4","VST5"]:
        if logdir.find(catalog) > 0:
            case_catalog = catalog
            break
    if case_catalog == "":
        return "Error! could not find catalog in dir name!"
    
    pin_r = []     # pin cases
    known_r = []   # known_failure cases
    oldfailures_r = []   # old cases
    oldfailures_r2 = []
    newfailures_r = []   # new cases

    pin_lines = []
    known_lines = []
    case_lines = []
    
    
    # read cases which need to be analyzed
    cases_w = []
    f1 = open(newfailures_name2)
    lines = f1.readlines()
    f1.close()
    for line in lines:
        line = line.strip()
        sps = line.split()  #case_name,case_no,case_status
        cases_w.append([case_catalog,sps[0],sps[1],sps[2]]) #case_catalog,case_name,case_no,case_status
        
    print "len of cases is ",len(cases_w)
    # read PIN index
    fn0 = "B95PIN"
    fn1 = os.path.join(AQpath,fn0)
    if not os.path.isfile(fn1):
        pin_r.append("PIN index doe not exist")
    else:
        f1 = open(fn1)
        pin_lines = f1.readlines()
        f1.close()

    # if PIN index exists, search PIN index
    if pin_lines:
        for case_w in cases_w:
            for line in pin_lines:
                if line.find(case_w[1]+separator+case_w[2])>=0:
                    rs = line.split(separator)
                    catalog2 = rs[0]
                    case = rs[1]
                    case_no = rs[2]
                    status = rs[3]
                    pin = rs[4]
                    dataset = rs[5]
                    member = rs[6]         
                    pin_r.append(case_w[1]+" "+case_w[2]+" "+case_w[3]+" --- " + catalog2+" "+case+" "+case_no+" "+status+" "+pin)
                    if case_catalog != catalog2:
                        pin_r.append("Warning! this case belongs to"+catalog2+", not "+catalog)  
                    if case_w[3] != status and status != "VSU5":
                        pin_r.append("Warning! different status")
                    case_w.append("pin!")
                    break

    # read known_failures
    fn0 = "BKNOWNFS"
    fn1 = os.path.join(AQpath,fn0)
    if not os.path.isfile(fn1):
        known_r.append("FAIL,"+fn1+" -- known_failures index does not exist")
    else:
        f1 = open(fn1)
        known_lines = f1.readlines()
        f1.close()        
    
    #if know_failures index exists, search case index
    if known_lines:
        for case_w in cases_w:
            if len(case_w) == 5 and case_w[4] == "pin!": # we do not search PIN case
                continue
            for line in known_lines:
                if line.find(case_w[1]+" "+case_w[2]) >= 0:
                    known_r.append(line)
                    case_w.append("known!")
                    break   
   


    # read case Index
    fn0 = "B95"+case_catalog
    fn1 = os.path.join(AQpath,fn0)
    if not os.path.isfile(fn1):
        oldfailures_r2.append("FAIL,"+fn1+" -- catalog file index does not exist")
    else:
        f1 = open(fn1)
        case_lines = f1.readlines()
        f1.close()        

        
    # if case Index exists, search case index
    if case_lines:
        for case_w in cases_w:
            if len(case_w) == 5 and case_w[4] == "pin!": # we do not search PIN case
                continue
            if len(case_w) == 5 and case_w[4] == "known!": # we do not search known_failures case
                continue
            for line in case_lines:
                if line.find(case_w[1]+separator+case_w[2]) >= 0:
                    rs = line.split(separator)
                    case = rs[0]
                    case_no = rs[1]
                    line2 = rs[2]
                    dataset = rs[3]
                    member = rs[4]

                    part1 = case_w[1]+" "+case_w[2]+" "+case_w[3]
                    part2 = dataset+"("+member+")"
                    oldfailures_r.append((part1,part2))
                    #oldfailures_r.append(case_w[1]+" "+case_w[2]+" "+case_w[3]+" -- " + dataset+"("+member+")")

                    oldulr = case_catalog+","+case_w[1]+","+case_w[2]
                    oldfailures_r2.append(oldulr.replace("/","@"))
                    case_w.append("old!")
                    break

    # check new failures, only new failures contain 4 elements, others contain 5 element
    # (1) if it is a PIN              --  case_catalog, case_name, case_no, case_status, "pin!"
    # (2) if it is a old failure      --  case_catalog, case_name, case_no, case_status, "old!"
    # (3) if it is a new failure      --  case_catalog, case_name, case_no, case_status
    for i,case_w in enumerate(cases_w):
        if len(case_w) == 4:
            newfailures_r.append(case_w[1]+" "+case_w[2]+" "+case_w[3])


    #print "len of cases 2 is ",len(cases_w)
    #print "new len =",len(newfailures_r)
    #print "old len =",len(oldfailures_r)

    return  template("search/log_analytic.htm",title="LOG VIEW",logdir=logdir, totaln=len(cases_w),pins=pin_r, knowns=known_r, oldfailures=oldfailures_r, 
                     oldfailures2=oldfailures_r2, newfailures=newfailures_r, user=request.user)  



@search_app.route("/log_case_search/<case_info>") 
@login_required
def log_case_search(case_info):
    case_info = case_info.replace("@","/")
    case_catalog,case_name,case_no = case_info.split(",")
    
    # search PIN
    pins_r = []
    code,r = PIN_search1(case_catalog,case_name,case_no)
    if code != "OK":
        pins_r.append("PIN search Fail! "+code+","+r)
    else:
        pins_r = r
    
    # search old case
    cases_r = []
    code,r = case_search1(case_catalog,case_name,case_no)
    if code != "OK":
        cases_r.append("case search Fail! "+code+","+r)
    else:
        cases_r = r

        level_1 = os.path.join(AQpath,"dataset")


    # search keyword
    key = case_name+ " "+ case_no
    keywords_r = []
    for catalog1 in keyword_catalog_list:
        level_2 = os.path.join(datasetpath,catalog1)
        datasets = os.listdir(level_2)
        result = []
        for ds in datasets:
            ds2 = os.path.join(level_2,ds)
            if not os.path.isdir(ds2):
                continue
            members = os.listdir(ds2)
            for member in members:
                member2 = os.path.join(ds2,member)
                if not os.path.isfile(member2):
                    continue
                for line_num,line in enumerate(open(member2,'rb')):
                    line = line.decode("utf-8","ignore")
                    if line.find(key) >= 0:
                        keywords_r.append(catalog1+"/"+ds+"/"+member+", "+str(line_num+1)+", "+line)
    return  template("search/log_case_search.htm",title="LOG case search", case_catalog=case_catalog, case_name=case_name, case_no=case_no,
                     pins_r=pins_r, cases_r = cases_r, keywords_r=keywords_r, user=request.user)  
    



def vsu_parse(fn,fn2,case_catalog,log_version):
    tempr = "create "+os.path.basename(fn2)+"\n"
    f1 = open(fn)  #JOURNAL
    lines = f1.readlines()
    f1.close()
    
    tset = ""
    tset_num = ""
    tset_result = ""

    f1 = open(fn2,"w+") #FAILURES
    for line in lines:
        line = line.strip()
        if line.startswith("30||TEST_PACKAGES"):
            tempr += "  "+line+"\n"
        if line.find("/tetexec.cfg")>0:
            tempr += "  "+line+"\n"
        if line.startswith("10|"):
            sps = line.split("|")
            sps2 = sps[1].split()
            tset = sps2[1]
        if line.startswith("220|"):
            sps = line.split("|")
            tset_result = sps[2]
            if tset_result not in VSU_ALLOW_LIST:
                sps2 = sps[1].split()
                tset_num = sps2[1]
                temp = tset+" "+tset_num
                temp2 = "%-56s %s\n" % (temp,tset_result)
                f1.write(temp2)
    f1.close()
    return tempr




def vsc_parse(fn,fn2, case_catalog, log_version):
    tempr = "create "+os.path.basename(fn2)+"\n"
    f1 = open(fn,"rb")
    lines = f1.readlines()
    f1.close()
    
    tset = ""
    tset_num = ""
    tset_result = ""

    f1 = open(fn2,"w+")
    for line in lines:
        line = line.strip()
        if line.find("/tetexec.cfg")>0:
            tempr += "  "+line+"\n"
        #print line
        if line.startswith("10|"):
            sps = line.split("|")
            sps2 = sps[1].split()
            tset = sps2[1]
        if line.startswith("520|"):
            if tset_num == "":
                pos1 = line.find("#")
                pos2 = line.find(" ",pos1)
                if pos2 > pos1:
                    tset_num = line[pos1:pos2]
        if line.startswith("400|"):
            if tset_num == "":
                sps = line.split("|")
                sps2 = sps[1].split()
                tset_num = sps2[1]
        if line.startswith("220|"):
            sps = line.split("|")
            tset_result = sps[2]
            #print tset,tset_num,tset_result
            if tset_result not in VSC_ALLOW_LIST:
                #sps2 = sps[1].split()
                #tset_num = sps2[1]
                temp = tset+" "+tset_num
                temp2 = "%-56s %s\n" % (temp,tset_result)
                f1.write(temp2)
            tset_num = ""
    f1.close()
    return tempr

def vst_parse(fn,fn2, case_catalog, log_version):
    tempr = "create "+os.path.basename(fn2)+"\n"
    f1 = open(fn,"rb")
    lines = f1.readlines()
    f1.close()
    
    tset = ""
    tset_num = ""
    tset_result = ""

    f1 = open(fn2,"w+")
    for line in lines:
        line = line.strip()
        if line.find("/tetexec.cfg")>0:
            tempr += "  "+line+"\n"
        #print line
        if line.startswith("10|"):
            sps = line.split("|")
            sps2 = sps[1].split()
            tset = sps2[1]
        if line.startswith("520|"):
            if tset_num == "":
                sps = line.split("|")
                sps2 = sps[1].split()
                tset_num = sps2[1]
                #pos1 = line.find("#")
                #pos2 = line.find(" ",pos1)
                #if pos2 > pos1:
                #    tset_num = line[pos1:pos2]
        if line.startswith("400|"):
            if tset_num == "":
                sps = line.split("|")
                sps2 = sps[1].split()
                tset_num = sps2[1]
        if line.startswith("220|"):
            sps = line.split("|")
            tset_result = sps[2]
            #print tset,tset_num,tset_result
            if tset_result not in VSC_ALLOW_LIST:
                #sps2 = sps[1].split()
                #tset_num = sps2[1]
                temp = tset+" "+tset_num
                temp2 = "%-56s %s\n" % (temp,tset_result)
                f1.write(temp2)
            tset_num = ""
    f1.close()
    return tempr



def keyword_search1(catalog1,key):
    level_1 = os.path.join(AQpath,"dataset")
    level_2 = os.path.join(level_1,catalog1)
    datasets = os.listdir(level_2)
    result = []
    for ds in datasets:
        ds2 = os.path.join(level_2,ds)
        if not os.path.isdir(ds2):
            continue
        members = os.listdir(ds2)
        for member in members:
            member2 = os.path.join(ds2,member)
            if not os.path.isfile(member2):
                continue
            for line_num,line in enumerate(open(member2,'rb')):
                line = line.decode("utf-8","ignore")
                if line.find(key) >= 0:
                    result.append(catalog1+"/"+ds+"/"+member+", "+str(line_num+1)+", "+line)
    return result


def case_search1(catalog,case,case_no):
    fn0 = "B95"+catalog
    fn1 = os.path.join(AQpath,fn0)
    if not os.path.isfile(fn1):
        return "FAIL",fn1+" -- catalog file index does not exist"
    result = []
    f1 = open(fn1)
    lines = f1.readlines()
    f1.close()
    for i,line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        line = line.decode("utf-8","ignore")
        if line.find(case+separator+case_no) >= 0:
            rs = line.split(separator)
            case = rs[0]
            case_no = rs[1]
            line2 = rs[2]
            dataset = rs[3]
            member = rs[4]
            result.append(line2)
            result.append("    "+dataset+"("+member+")")
    return "OK",result


def PIN_search1(catalog,case,case_no):
    fn0 = "B95PIN"
    fn1 = os.path.join(AQpath,fn0)
    if not os.path.isfile(fn1):
        return "FAIL",fn1+" -- catalog file index does not exist"
    result = []
    f1 = open(fn1)
    lines = f1.readlines()
    f1.close()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        #print line
        if line.find(case+separator+case_no) >= 0:
            rs = line.split(separator)
            catalog2 = rs[0]
            case = rs[1]
            case_no = rs[2]
            status = rs[3]
            pin = rs[4]
            dataset = rs[5]
            member = rs[6]
            result.append(catalog2+" "+case+" "+case_no+" "+status+" "+pin)
            result.append("    "+dataset+"("+member+")")
            if catalog != catalog2:
                result.append("Warning! this case belongs to"+catalog2+", not "+catalog)
    return "OK",result



if __name__ == '__main__':                                                                                  
    run(search_app,host="0.0.0.0",reloader=True)             



if __name__ == '__main__':
    pass

