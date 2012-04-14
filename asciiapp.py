#!/usr/bin/python
# coding:utf-8
# 16:58:08 create asciiapp.py
#  ywllyht@yahoo.com.cn  


import os                                                                                                
import types

from bottle import route, run, Bottle, template, request, abort, redirect
from users import login_required

try:
    import Image, ImageDraw,ImageFont
    unsupport = ""
except ImportError,e:
    unsupport = "You must install pil First!"

#font_path = r"C:\Windows\Fonts\simyou.ttf"
font_path = r"C:\Windows\Fonts\G0v1.otf"
if not os.path.isfile(font_path):
    unsupport = "You must prepare font first!"
font_size = 24
pic_size = 25


ascii_app = Bottle()



@ascii_app.route("/")
def index():
    if unsupport:
        return unsupport
    inputtext = request.query.inputtext   
    #searchtext = searchtext.encode("utf-8")
    #print inputtext, type(inputtext)
    if inputtext == "":                                                                                    
        return template("ascii/index.htm",title="ASCII ART ",ascii_text=u"请输入要转换的字符!",user=request.user)
    else:    
        ascii_type = request.query.ascii_type
        #print ascii_type,type(ascii_type)
        try:
            if ascii_type == "basic":
                ascii_text = "".join(draw_text2(inputtext))
            elif ascii_type == "chn":
                ascii_text = "".join(draw_text3(inputtext))
            else:
                ascii_text = "Error,Unknow ascii_type"
            
        except Exception,e:
            ascii_text = str(e)
        return template("ascii/index.htm",title="ASCII ART ",ascii_text=ascii_text,user=request.user) 


def group(seq, size):
   """
   Returns an iterator over a series of lists of length size from iterable.

       >>> list(group([1,2,3,4], 2))
       [[1, 2], [3, 4]]
   """
   if not hasattr(seq, 'next'):
       seq = iter(seq)
   while True:
       yield [seq.next() for i in xrange(size)]



def draw_text2(string,fill_c="*",factor=2):
    if type(string) != types.UnicodeType:
        raise Exception("Error, You must input unicode string")
    if len(string) > 10:
        raise Exception("Error, Only support up to 10 characters")
    im = Image.new('RGB', (pic_size*len(string),pic_size))  
    #print im.format,im.size,im.mode
    width,height = im.size
    draw = ImageDraw.Draw(im)
    #draw.line((0, 0) + im.size, fill=128)
    #draw.line((0, im.size[1], im.size[0], 0), fill=128)

    font = ImageFont.truetype(font_path , font_size )
    draw.text((0,0),string,font=font)
    del draw 
    #im.save(fn)

    data = list(im.getdata())
    data2 = map(lambda x: sum(x), data)
    data3 = list(group(data2,width))
    # delete the blank lines in the head
    i = 0
    data3_len= len(data3)
    for i in range(data3_len):
        if sum(data3[i]) > 0:
            break
    data3 = data3[i:]

    # delete the blank lines in the bottom
    i = 0
    data3_len= len(data3)
    for i in range(data3_len-1,0,-1):
        if sum(data3[i]) > 0:
            break
    data3 = data3[:i+1]


    # delete the blank lines in the right
    i = 0
    data3_len= len(data3)
    flag = False
    for i in range(width-1,0,-1):
        for dd in data3:
            if dd[i] > 0:
                flag = True
                break
        if flag:
            break

    right_border = i
    
    result = []
    for dd in data3:
        for i,ddd in enumerate(dd):
            if i > right_border:
                break
            if ddd > 0:
                result.append(fill_c*factor)
            else:
                result.append(" "*factor)
        result.append("\n")
    return result

def draw_text3(string,factor=1):
    if type(string) != types.UnicodeType:
        return "Error, You must input unicode string"
    if len(string) > 4:
        return "Error, Only support 1 characters"

    data_merge = [[] for x in range(pic_size)]
    for i in range(len(string)):
        s = string[i]
        im = Image.new('RGB', (pic_size,pic_size))  
        #print im.format,im.size,im.mode
        width,height = im.size
        draw = ImageDraw.Draw(im)
        font = ImageFont.truetype(font_path , font_size )
        draw.text((0,0),s,font=font)
        del draw 

        data = list(im.getdata())
        data2 = map(lambda x: sum(x), data)
        data3 = list(group(data2,width))

        # delete the blank lines in the right
        ii = 0
        data3_len= len(data3)
        flag = False
        for ii in range(width-1,0,-1):
            for dd in data3:
                if dd[ii] > 0:
                    flag = True
                    break
            if flag:
                break
        right_border = ii
        #print i,right_border


       # change the content of this block. fill it with fill_c
        fill_c = s.encode("utf-8")
        for j in range(height):
            data3_temp = []
            for jj in data3[j][:right_border]:
                if jj > 0:
                    data3_temp.append(fill_c*factor)
                else:
                    data3_temp.append("  "*factor)
            data3_temp.append("  ")
            data_merge[j] += data3_temp

        #print data_merge[0]
        # delete the blank lines in the head
    i = 0
    data_merge_len= len(data_merge)
    for i in range(data_merge_len):
        b = lambda x: sum(map(lambda y:ord(y)-32,x))
        if sum(map(b,data_merge[i])) > 0:
            break
    data_merge = data_merge[i:]
    
    # delete the blank lines in the bottom
    i = 0
    data_merge_len= len(data_merge)
    for i in range(data_merge_len-1,0,-1):
        b = lambda x: sum(map(lambda y:ord(y)-32,x))
        if sum(map(b,data_merge[i])) > 0:
            break
    data_merge = data_merge[:i+1]


    result = []
    #fill_c = string.encode("utf-8")
    for dd in data_merge:
        result.append("".join(dd)+"\n")
    return result



if __name__ == '__main__':
    pass

