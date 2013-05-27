# coding:utf-8

from bottle import route, run, Bottle, template, request, abort, redirect, static_file
import os
import sys
import time
import qrcode


_localDir=os.path.dirname(__file__)
_curpath=os.path.normpath(os.path.join(os.getcwd(),_localDir))
_staticpath = os.path.join(_curpath,"static")
_uppath = os.path.dirname(_curpath)
_picpath1 = os.path.join(_staticpath,"pics")
logopath1 = os.path.join(_picpath1,"zblog_logo.jpg")

if sys.platform == "win32":  # winXP, developer environment
    _ftppath = os.path.join(_uppath,"ftp")
else:                        # linux server, running environment
    _ftppath = "/home/lljli/ftp"
_qrpath0 = os.path.join(_ftppath,"temp")
_qrpath  = os.path.join(_qrpath0,"qrcode")


if not os.path.isdir(_qrpath):
    os.makedirs(_qrpath)
    

myqrcode_app = Bottle()

@myqrcode_app.route("/") 
def index():
    return template("qrcode/index.htm",user=request.user)


@myqrcode_app.route("/generate",method="POST") 
def generate():
    data = request.forms.get('data',"")
    if len(data) >= 300:
        return template("myerror.htm", user=request.user, msg="Error,input data exceeds 200 characters! "+str(len(data)))
    time_1 = str(int(time.time()*1000))
    ip_1 = request.remote_addr.replace(".","")
    url_1 = time_1+"_"+ip_1

    
    logo = request.forms.get("logo","")
    if not logo:
        return template("myerror.htm", user=request.user, msg="Error, can not find logo type")

    size = request.forms.get("size","")
    if not size:
        return template("myerror.htm", user=request.user, msg="Error, can not find size")


    print "lenth of data=%d,size=%s,logo=%s" % (len(data),size,logo)
    
    # if len(data) > 200:
    #     box_size1 = 5
    # elif len(data) > 100:
    #     box_size1 = 7
    # else:
    #     box_size1 = 10

    # ERROR_CORRECT_L
    #     About 7% or less errors can be corrected.
    # ERROR_CORRECT_M (default)
    #     About 15% or less errors can be corrected.
    # ERROR_CORRECT_Q
    #     About 25% or less errors can be corrected.
    # ERROR_CORRECT_H.
    #     About 30% or less errors can be corrected. 
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=size,
        border=4,
    )
    qr.add_data(data)
    qr.make()
    m=qr.make_image()
    fn1 = os.path.join(_qrpath,url_1+".png")
    m.save(fn1)
    
    
    redirect("/myqrcode/display/"+url_1)

@myqrcode_app.route("/display/<urlname>")
def display(urlname):
    fn1 = "/ftp/temp/qrcode/"+urlname+".png"
    return template("qrcode/display.htm",user=request.user, urlname=fn1)


    
