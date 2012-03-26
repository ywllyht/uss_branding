# coding:utf-8
# created time is 16:15:03 2012-03-26
# filename: searchapp.py
# ywllyht@yahoo.com.cn

from bottle import route, run, Bottle, template, request, abort, redirect                                   
import sqlite3 as sqlite                                                                                    
import md5  
import os                                                                                                
from users import login_required

search_app = Bottle()

catalog_list = [
    "INSTALL",
    "PROBLEM",
    "VSC5",
    "VST5",
    "VSU5",
    "VSX4",
    "ZOSR12",
    ]


@search_app.route("/") 
@login_required
def search():                                                                                               
    searchtext = request.query.searchtext                                                                   
    searchtext = searchtext.encode("utf-8")
    #print searchtext                                                                                        
    #print request.query.searchtext                                                                          
    if searchtext == "":                                                                                    
        return template("search/index.htm",title="USS FVT Search ",user=request.user)                            
    else:    
        search_targs = []
        for s in catalog_list:
            try:
                r = request.query[s]
                search_targs.append(s)
            except KeyError,e:
                pass
        
        search_result = []
        for s in search_targs:
            r = search1(s,searchtext)
            search_result.append((s,r))
        #print search_result
        return template("search/result.htm",title="USS FVT Search result",rs=search_result, user=request.user)                            
    return "unimplemented" 

# print search_result
# [
#   ('PROBLEM', ["ddaa1,fffff", "dataa2, linesss","dtaa3,lin"]),
#   ('VSC5', ["dataa1,fasdfas", "dtaaa2,fdfsa"]),
# ]                                                                                 


 #  return "unimplemented"                                                                                  
AQpath = r"E:\test\python\Bottle\AQUSS"


def search1(catalog1,key):
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
            for line in open(member2,'rb'):
                if line.find(key) >= 0:
                    result.append(catalog1+"/"+ds+"/"+member+", "+line)
    return result

if __name__ == '__main__':                                                                                  
    run(search_app,host="0.0.0.0",reloader=True)             



if __name__ == '__main__':
    pass

