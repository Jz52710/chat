from flask import Flask,render_template,session,request
from flask_socketio import SocketIO,join_room,close_room,rooms,leave_room,emit,send
import time,os

# 用户
usernames = ['admin1','admin2','xm','xb'] 
# 在线人
online = []
# 在线房间
onlineroomname = "online"  


app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['DEBUG'] = True

socket = SocketIO(app)

@app.route("/")
def index():
    return render_template("index.html")


@socket.on('login')
def login(data):
    username = data['username']
    lingshiroom = str(time.time())
    join_room(lingshiroom)
    # 如果是用户

    if username in usernames:
        # 如果用户已经登录
        if username not in online:
            online.append(username)  #加入 在线列表
            roomname = username
            join_room(roomname)
            join_room(onlineroomname)
            socket.emit('islogin',{'res':'ok'},room=roomname)
            socket.emit('listfriends',{'friends':online},room=onlineroomname)
        else:
            socket.emit('islogin',{'res':'no','message':'已在线'},room=lingshiroom)
    else:
        socket.emit("islogin",{'res':'no','message':'没有此用户'},room=lingshiroom)
    close_room(lingshiroom)

@socket.on("loginout")
def beforeunload(data):
    username = data['username']
    online.pop(online.index(username))
    # 离开在线房间
    leave_room(onlineroomname)
    
    # 发送到前台 做离开、离线
    socket.emit('listfriends',{'friends':online},room=onlineroomname)
    socket.emit('isloginout',{'res':"ok"},room=username)
    socket.emit('listfriends',{'friends':[]},room=username)

    # 关闭自身房间
    close_room(username)


@socket.on("send")
def send(data):
    to = data['to']
    con = data['con']
    user = data['user']
    socket.emit('myaccept',{'to':to,'con':con,'user':user},room=to)


if __name__ == "__main__":
    socket.run(app)