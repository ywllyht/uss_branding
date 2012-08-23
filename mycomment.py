# coding:utf-8
# created time is 12:17:12 2012-03-11
# filename: index.py
# ywllyht@yahoo.com.cn


#how to find the static file?
#how to find the template file?

import sqlite3
from bottle import Bottle, route, run, debug, template, request, validate, static_file,  error, redirect
#MessageBox = ctypes.windll.user32.MessageBoxA 
comment_app = Bottle()
from users import login_required


@comment_app.route('/')
def index():
    s = request.environ.get('beaker.session')
    maxcharacter = s.get('maxcharacter','77')
    indent = s.get('indent','0')
    style = s.get('maxcharacter','c')
    return template("comment/index.htm",title="input comment",user=request.user,maxcharacter=maxcharacter,indent=indent,style=style,comment="",result="")

@comment_app.route('/',method="POST")
def post_comment():
    maxcharacter = request.forms.get('maxcharacter')
    indent = request.forms.get('indent')
    style = request.forms.get('style')
    comment = request.forms.get('comment')

    try:
        maxcharacter2 = int(maxcharacter)
    except ValueError,e:
        return template("mydirect.htm",title="error", msg="maxcharacter error", next_url=".", user=request.user)

    try:
        indent2 = int(indent)
    except ValueError,e:
        return template("mydirect.htm",title="error", msg="indent error", next_url=".", user=request.user)

    if indent2 > 40:
        return template("mydirect.htm",title="error", msg="indent > 40", next_url=".", user=request.user)

    #print "maxcharacter=",maxcharacter
    #print "indent=",indent
    #print "style=",style
    #print "comment=",comment

    indent_c = " " * indent2

    r = []
    if style == "rexx":
        gap = maxcharacter2 - indent2 - 2
        separator = indent_c+"/*"+ "-"*gap+" */\n"
        r.append(separator)
    else:
        gap = maxcharacter2 - indent2 - 2
        separator = indent_c+"/*"+ "*"*gap+" */\n"
        r.append(separator)
        

    # add line-head for first line
    line_len = 0
    r.append(indent_c)
    line_len += indent2
    r.append("/* ")
    line_len += 3

    lines = comment.splitlines()
    for line in lines:
        # find the indent blanks of this line
        line_len2 = len(line)
        cc = 0
        while cc < line_len2:
            if line[cc] != " ":
                break
            cc += 1
        r.append(" "*cc)
        line_len += cc

        words = line.split()
        for word in words:
            if line_len + len(word) >= maxcharacter2:
                # add line-tail for current line
                gap = maxcharacter2 - line_len
                r.append(" "*gap)
                r.append(" */")
                # start new line, 
                r.append("\n")
                line_len = 0
                r.append(word+" ")
                line_len += len(word)+1
                r.append(indent_c)
                line_len += indent2
                r.append("/* ")
                line_len += 3
            else:
                r.append(word+" ")
                line_len += len(word)+1

        # add line-tail and the line-head of next line
        gap = maxcharacter2 - line_len
        r.append(" "*gap)
        r.append(" */")
        r.append("\n")
        line_len = 0
        r.append(indent_c)
        line_len += indent2
        r.append("/* ")
        line_len += 3
         

    # add line-tail for last line
    gap = maxcharacter2 - line_len
    r.append(" "*gap)
    r.append(" */")
    r.append("\n")



    if style == "rexx":
        gap = maxcharacter2 - indent2 - 2
        separator = indent_c+"/*"+ "-"*gap+" */\n"
        r.append(separator)
    else:
        gap = maxcharacter2 - indent2 - 2
        separator = indent_c+"/*"+ "*"*gap+" */\n"
        r.append(separator)

    #print "r=",repr("".join(r))

    # save user's choice in session
    s = request.environ.get('beaker.session')
    s['maxcharacter'] = maxcharacter
    s['indent'] = indent
    s['style'] = style
    s.save()

    return template("comment/index.htm",title="input comment",user=request.user,maxcharacter=maxcharacter,indent=indent,style=style,comment=comment,result="".join(r))


if __name__ == '__main__':
    debug(True)
    run(host="0.0.0.0",reloader=True)


