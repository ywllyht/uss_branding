# coding:utf-8

from bottle import route, run, Bottle, template, request, abort, redirect, static_file
import os
import sys
import time
import qrcode
from PIL import Image

_localDir=os.path.dirname(__file__)
_curpath=os.path.normpath(os.path.join(os.getcwd(),_localDir))
_staticpath = os.path.join(_curpath,"static")
_uppath = os.path.dirname(_curpath)
_picpath1 = os.path.join(_staticpath,"pics")


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

    error_correction = request.forms.get("error_correction","")
    if not error_correction:
        return template("myerror.htm", user=request.user, msg="Error, can not find error_correction")

    print "lenth of data=%d,size=%s,logo=%s,error_correction=%s" % (len(data),size,logo,error_correction)
    
    if error_correction == "ERROR_CORRECT_L":
        error_correction0 = qrcode.constants.ERROR_CORRECT_L
    elif error_correction == "ERROR_CORRECT_M":
        error_correction0 = qrcode.constants.ERROR_CORRECT_M
    elif error_correction == "ERROR_CORRECT_Q":
        error_correction0 = qrcode.constants.ERROR_CORRECT_Q
    elif error_correction == "ERROR_CORRECT_H":
        error_correction0 = qrcode.constants.ERROR_CORRECT_H
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
        error_correction=error_correction0,
        box_size=size,
        border=4,
    )
    qr.add_data(data)
    qr.make()
    m=qr.make_image()
    fn1 = os.path.join(_qrpath,url_1+".png")
    m.save(fn1)
    
    if logo != "None":

        im1 = Image.open(fn1);  #1676x343
        im =  im1.convert('RGB')
        #print im.format, im.size, im.mode
        width = im.size[0]
        hight = im.size[1]

        logopath1 = os.path.join(_picpath1,logo)
        if not os.path.isfile(logopath1):
            print logopath1
            return template("myerror.htm", user=request.user, msg="Error, This logo does not exist! "+logo)

        foreground = Image.open(logopath1);       
        logosize = 60        
        box = (0, 0, logosize, logosize)
        box2 = ((width-logosize)/2,(hight-logosize)/2,(width+logosize)/2,(hight+logosize)/2)
        region = foreground.crop(box)

        im.paste(region, box2)
        im.save(fn1)
    
    
    redirect("/myqrcode/display/"+url_1)

@myqrcode_app.route("/display/<urlname>")
def display(urlname):
    ftp_fn1 = "/ftp/temp/qrcode/"+urlname+".png"

    if sys.platform == "win32":  # winXP, developer environment
        decode_data = ""
    else:
        abs_fn1 = os.path.join(_qrpath,urlname+".png")
        try:
           decode_data = zbar_read(abs_fn1)
        except Exception,e:
           decode_data = "zbar read Error! " + str(e)

    return template("qrcode/display.htm",user=request.user, ftp_fn1=ftp_fn1, decode_data=decode_data)

def zbar_read(fn1):
    # create a reader  
    import zbar  
    scanner = zbar.ImageScanner()  
    # configure the reader  
    scanner.parse_config('enable')  
    # obtain image data  
    pil = Image.open(fn1).convert('L')  
    width, height = pil.size  
    raw = pil.tostring()  
    # wrap image data  
    image = zbar.Image(width, height, 'Y800', raw)  
    # scan the image for barcodes  
    scanner.scan(image)  
    # extract results  
    result = []
    for symbol in image:  
        # do something useful with results  
        result.append("decoded type=%s, data=%s" % (symbol.type,symbol.data))
        print 'decoded', symbol.type, 'symbol', '"%s"' % symbol.data
    # clean up  
    del(image)
    return "\n".join(result)
