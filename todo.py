# coding:utf-8
# created time is 12:17:12 2012-03-11
# filename: index.py
# ywllyht@yahoo.com.cn


#how to find the static file?
#how to find the template file?

import sqlite3
from bottle import Bottle, route, run, debug, template, request, validate, static_file,  error, redirect

todo_app = Bottle()

@todo_app.route('/')
def index():
    return template("todo/index.htm",user=request.user)


@todo_app.route('/todo')
def todo_list():
    conn = sqlite3.connect('branding.db')
    c = conn.cursor()
    #c.execute("SELECT id, task FROM todo WHERE status LIKE '1'")
    c.execute("SELECT id, task, status,username FROM todo")
    result = c.fetchall()
    count = len(result)
    #done_count = 0
    #for line in result:
    #    if line[2] == 0:
    #        done_count += 1 
    done_count = len([x for x in result if x[2]==0]) 
      
    c.close()
    output = template('todo/make_table.htm',rows=result, title="todo list", count=count, done_count=done_count, user=request.user)
    #return str(result)
    return output

#    --------------------------------- make_table.htm -------------------------------
#    %#template to generate a HTML table from a list of tuples (or list of lists, or tuple of tuples or ...)
#    <p>The open items are as follows:</p>
#    <table border="1">
#    %for row in rows:
#      <tr>
#      %for col in row:
#        <td>{{col}}</td>
#      %end
#      </tr>
#    %end
#    </table>
#    

@todo_app.route('/delete/<no:int>')
def todo_delete(no):
    cx = sqlite3.connect('branding.db')
    cu = cx.cursor()
    command = "delete from todo where id= '%d' " % no
    cu.execute(command)
    cx.commit()
    redirect("../todo")



@todo_app.route('/new/', method='GET')
def new_item():
    if request.GET.get('save','').strip():
    
        new = request.GET.get('task', '').strip()
        conn = sqlite3.connect('branding.db')
        c = conn.cursor()
    
        c.execute("INSERT INTO todo (task,status,username) VALUES (?,?,?)", (new,1,""))
        new_id = c.lastrowid
    
        conn.commit()
        c.close()
        msg = 'The new task was inserted into the database, the ID is %s' % new_id
        return template("mydirect.htm",title="create new task ok",msg=msg,next_url="../todo",user=request.user)
        #return '<p>The new task was inserted into the database, the ID is %s</p>' % new_id
    else:
        return template('todo/new_task.htm',title="new task", user=request.user)

#    ------------------------ new_task.htm ---------------------------
#    <p>Add a new task to the ToDo list:</p>
#    <form action="/new" method="GET">
#      <input type="text" size="100" maxlength="100" name="task">
#      <input type="submit" name="save" value="save">
#    </form>
#    


@todo_app.route('/edit/<no>', method='GET')
@validate(no=int)
def edit_item(no):

    if request.GET.get('save','').strip():
        edit = request.GET.get('task','').strip()
        status = request.GET.get('status','').strip()
        username = request.GET.get('username','').strip()

        if status == 'open':
            status = 1
        else:
            status = 0

        conn = sqlite3.connect('branding.db')
        c = conn.cursor()
        c.execute("UPDATE todo SET task = ?, status = ?, username= ? WHERE id LIKE ?", (edit, status, username, no))
        conn.commit()

        msg = 'The item number %s was successfully updated' % no
        return template("mydirect.htm",title="modify new task successfully",msg=msg,next_url="../todo",user=request.user)
    else:
        conn = sqlite3.connect('branding.db')
        c = conn.cursor()
        command = "SELECT task,status,username FROM todo WHERE id=%s" % no
        c.execute(command)
        #c.execute("SELECT task,status FROM todo WHERE id=%d ?", (str(no)))
        cur_data = c.fetchone()
        #print cur_data
        if cur_data[1] == 1:
            options = [ "selected",""]
        else:
            options = [ "","selected"]
        #print options
        return template('todo/edit_task.htm', old=cur_data, no=no, options=options, title="edit", user=request.user)

#   ---------------------------- edit_task.htm  ----------------------------------
#    %#template for editing a task
#    %#the template expects to receive a value for "no" as well a "old", the text of the selected ToDo item
#    <p>Edit the task with ID = {{no}}</p>
#    <form action="/edit/{{no}}" method="get">
#      <input type="text" name="task" value="{{old[0]}}" size="100" maxlength="100">
#      <select name="status">
#        <option {{options[0]}}>open</option>
#        <option {{options[1]}}>closed</option>
#      </select>
#      <br/>
#      <input type="submit" name="save" value="save">
#    </form>
#    


#@todo_app.route('/item:item#[1-9]+#')
@todo_app.route('/item<item:re:[0-9]+>')
def show_item(item):
    conn = sqlite3.connect('branding.db')
    c = conn.cursor()
    command = "SELECT task FROM todo WHERE id='%s' " % item
    c.execute(command)
    result = c.fetchall()
    c.close()
    if not result:
        return 'This item number does not exist!'
    else:
        return 'Task: %s' %result[0]


@todo_app.route('/help')
def help():
    return static_file('help.html', root=r'E:\Dropbox\test\python\Bottle\branding\static')



#@todo_app.route('/json:json#[1-9]+#')
@todo_app.route('/json<json:re:[1-9]+>')
def show_json(json):
    conn = sqlite3.connect('branding.db')
    c = conn.cursor()
    c.execute("SELECT task FROM todo WHERE id LIKE ?", (json))
    result = c.fetchall()
    c.close()

    if not result:
        return {'task':'This item number does not exist!'}
    else:
        return {'Task': result[0]}


# @error(403)
# def mistake403(code):
#     return 'The parameter you passed has the wrong format!'


# @error(404)
# def mistake404(code):
#     return 'Sorry, this page does not exist!'

if __name__ == '__main__':
    debug(True)
    run(host="0.0.0.0",reloader=True)


