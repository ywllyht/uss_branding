# coding:utf-8
# created time is 16:15:03 2012-03-26
# filename: searchapp.py
# ywllyht@yahoo.com.cn

from bottle import route, run, Bottle, template, request, abort, redirect                                   
import sqlite3 as sqlite                                                                                    
import os                                                                                                
from users import login_required


separator = "%%^^\t"



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
    "PROBLEM",
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
    return template("search/index.htm",title="USS FVT Search ",user=request.user)                           
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



 #  return "unimplemented"                                                                                  
_curpath = os.path.dirname(__file__)
_uppath = os.path.dirname(_curpath)
AQpath = os.path.join(_uppath,"AQUSS")
#AQpath = r"E:\test\python\Bottle\AQUSS"


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
    for line in lines:
        line = line.strip()
        if not line:
            continue
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

