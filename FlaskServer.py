from flask import Flask, jsonify, abort, request, make_response
import SQLiteHandler
import SessionHandler
from aiohttp import web
import socketio
import wrtcHandler

sh = SessionHandler.Session_Handler()
wrtch = wrtcHandler.WRTCHandler()

sqlh = SQLiteHandler.SQL_Handler()

app = Flask(__name__)

sio = socketio.AsyncServer(cors_allowed_origins='*')
app2 = web.Application()
sio.attach(app2)

@app.route("/hello", methods=['GET'])
def hello():
    return "Hello World!"


@app.route("/register", methods=['POST'])
def register():
    result = request.get_json()
    response = sqlh.addUser(result["name"], result["mail"], result["password"])
    if response == "Success":
        return response, 200, {"Content-Type": "application/json"}
    else:
        return response, 400, {"Content-Type": "application/json"}


@app.route("/login", methods=['POST'])
def login():
    result = request.get_json()

    if sqlh.checkPasswd(result["name"], result["password"]):
        sqlh.updateLastlogin(result["name"])
        sh.add_session(result["name"], request.environ['REMOTE_ADDR'])
        token = sh.find_user_token(result["name"])
        if token is not False:
            return token, 200, {"Content-Type": "application/json"}
    else:
        return "Fail", 400, {"Content-Type": "application/json"}


@app.route("/friends", methods=['GET'])
def friends():
    token = request.args.get('token')
    user = sh.find_user_by_token(token)
    if user is not False:
        sqlh.updateLastlogin(user)
        friends = sqlh.getFriends(user)
        sh.add_session(user, request.environ['REMOTE_ADDR'])
        token = sh.find_user_token(user)
        j = sqlh.friends_to_json(friends, token)
        return j, 200, {"Content-Type": "application/json"}
    else:
        return 400

@app.route("/notifications", methods=['GET'])
def notifications():
    token = request.args.get('token')
    user = sh.find_user_by_token(token)
    if user is not False:
        sqlh.updateLastlogin(user)
        notifications = sqlh.getNotifications(user)
        sh.add_session(user, request.environ['REMOTE_ADDR'])
        token = sh.find_user_token(user)
        j = sqlh.notifications_to_json(notifications, token)
        return j, 200, {"Content-Type": "application/json"}
    else:
        return 400


@app.route("/friends", methods=['POST'])
def add_friends():
    result = request.get_json()
    user = sh.find_user_by_token(result["token"])
    if user is not False:
        sqlh.updateLastlogin(user)
        result = sqlh.addFriends(user, result["friend"])
        sh.add_session(user, request.environ['REMOTE_ADDR'])
        token = sh.find_user_token(user)
        if result != "Fail":
            return token, 200, {"Content-Type": "application/json"}
        else:
            return "Fail", 400, {"Content-Type": "application/json"}
    else:
        return "Fail", 400, {"Content-Type": "application/json"}


@app.route("/approve", methods=['POST'])
def approve_friends():
    result = request.get_json()
    user = sh.find_user_by_token(result["token"])
    if user is not False:
        sqlh.updateLastlogin(user)
        result = sqlh.approveInvitation(user, result["friend"])
        sh.add_session(user, request.environ['REMOTE_ADDR'])
        token = sh.find_user_token(user)
        if result != "Fail":
            return token, 200, {"Content-Type": "application/json"}
        else:
            return "Fail", 400, {"Content-Type": "application/json"}
    else:
        return 'Fail', 400, {"Content-Type": "application/json"}

@app.route("/reject", methods=['POST'])
def reject_friends():
    result = request.get_json()
    user = sh.find_user_by_token(result["token"])
    if user is not False:
        sqlh.updateLastlogin(user)
        result = sqlh.rejectInvitation(user, result["friend"])
        sh.add_session(user, request.environ['REMOTE_ADDR'])
        token = sh.find_user_token(user)
        if result != "Fail":
            return token, 200, {"Content-Type": "application/json"}
        else:
            return "Fail", 400, {"Content-Type": "application/json"}
    else:
        return 'Fail', 400, {"Content-Type": "application/json"}

@app.route("/mailchange", methods=['POST'])
def change_mail():
    result = request.get_json()
    user = sh.find_user_by_token(result["token"])
    if user is not False:
        sqlh.updateLastlogin(user)
        result = sqlh.changeMail(user, result["mail"])
        sh.add_session(user, request.environ['REMOTE_ADDR'])
        token = sh.find_user_token(user)
        if result != "Fail":
            return token, 200, {"Content-Type": "application/json"}
        else:
            return "Fail", 400, {"Content-Type": "application/json"}
    else:
        return 'Fail', 400, {"Content-Type": "application/json"}

@app.route("/delete", methods = ['GET'])
def delete():
    token = request.args.get('token')
    user = sh.find_user_by_token(token)
    if user is not False:
        result = sqlh.deleteUser(user)

        if result != "Fail":
            return "Success", 200, {"Content-Type": "application/json"}
        else:
            return "Fail", 400, {"Content-Type": "application/json"}
    else:
        return "Fail", 400, {"Content-Type": "application/json"}

@app.route("/call", methods = ['POST'])
def call():
    result = request.get_json()
    user = sh.find_user_by_token(result["token"])
    if user is not False:
        friend = result["friend"]
        if wrtch.find_user_room(friend) == friend:
            sio.leave_room(wrtch.find_user_sid(user),wrtch.find_user_room(user))
            sio.enter_room(wrtch.find_user_sid(user),wrtch.find_user_room(friend))
            wrtch.change_room(user, friend)
        else:
            return 'User offline or in other call', 400, {"Content-Type": "application/json"}
    else:
        return 'Fail', 400, {"Content-Type": "application/json"}



@sio.event
async def connect(sid, environ):
    print('Connected', sid)
    user = sh.find_user_ip(environ['REMOTE_ADDR'])
    if user is not False:
        wrtch.add_session(user, sid, environ['REMOTE_ADDR'])
        await sio.emit('ready', room=user, skip_sid=sid)
        sio.enter_room(sid, user)
    else:
        return 400


@sio.event
def disconnect(sid):
    sio.leave_room(sid, wrtch.find_user_room(wrtch.find_user_by_sid(sid)))
    print('Disconnected', sid)


@sio.event
async def data(sid, data):
    print('Message from {}: {}'.format(sid, data))
    await sio.emit('data', data, room=wrtch.find_user_room(wrtch.find_user_by_sid(sid)), skip_sid=sid)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    web.run_app(app2, port=9999)
