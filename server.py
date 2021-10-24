import socketio
import eventlet
import sqlite3
import re
from datetime import date
import os

# Create a Socket.IO server (CORS arg required on server, not locally)
sio = socketio.Server()
#sio = socketio.Server(cors_allowed_origins='URL or *')

RPSLS_PATH = './' #edit if launched from elsewhere
DB_PATH = RPSLS_PATH + 'db/rpsls.sqlite'

searching = {} #someone seeks a game? (uid + sid)
connected = {} #map uid --> sid (seek stage)

@sio.event
def disconnect(sid):
    """ Triggered at page reload or tab close """
    global connected, searching
    try:
        key_idx = list(connected.values()).index(sid)
        del connected[list(connected.keys())[key_idx]]
    except ValueError:
        # If the user didn't seek, no key to find
        pass
    if searching and searching["sid"] == sid:
        searching = {}

@sio.event
def login(sid, data):
    """ When user sends name from /login page """
    if not re.match(r"^[a-zA-Z]{3,}$", data):
        sio.emit("login", {"err": "Name: letters only"}, room=sid)
        return
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    uid = 0
    try:
        # Always try to insert (new) Users row
        cur.execute("insert into Users (name) values (?)", (data,))
        uid = cur.lastrowid
    except sqlite3.IntegrityError as err:
        # If fails: user already exists, find its ID
        if str(err) == "UNIQUE constraint failed: Users.name":
            cur.execute("select id from Users where name = ?", (data,))
            uid = cur.fetchone()[0]
        else:
            raise
    con.commit()
    con.close()
    sio.emit("login", {"name": data, "uid": uid}, room=sid)

@sio.event
def seek(sid, data):
    """ When user click on 'Play' button """
    global connected, searching
    connected[data["uid"]] = sid
    if not searching:
        searching = {"uid": data["uid"], "sid": sid, "name": data["name"]}
    else:
        # Active seek pending: create game
        opponent = searching
        searching = {}
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        today = (date.today(),)
        cur.execute("insert into Games (created) values (?)", today)
        gid = cur.lastrowid
        # To room == sid, opponent is me. To my room, it's him/her
        sio.emit("play",
            {"gid":gid, "oppid":opponent["uid"], "oppname":opponent["name"]},
            room=sid)
        sio.emit("play",
            {"gid":gid, "oppid":data["uid"], "oppname":data["name"]},
            room=opponent["sid"])
        id_list = [(data["uid"],gid), (opponent["uid"],gid)]
        cur.executemany("insert into Players (uid,gid) values (?,?)", id_list)
        con.commit()
        con.close()

@sio.event
def move(sid, data):
    """ New move to DB + transmit to opponent """
    sio.emit("move", data, room=connected[data["oppid"]])
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("insert into Moves (uid,gid,choice,mnum) values (?,?,?,?)",
                (data["uid"],data["gid"],data["choice"],data["mnum"]))
    con.commit()
    con.close()

static_files = {
    '/': RPSLS_PATH + 'index.html',
    '/rpsls.js': RPSLS_PATH + 'rpsls.js',
    '/favicon.ico': RPSLS_PATH + 'favicon.ico',
    '/assets': RPSLS_PATH + 'assets'
}

PORT = os.getenv('RPSLS_PORT')
if PORT is None:
    PORT = "8000"
PORT = int(PORT)

# Wrap with a WSGI application
app = socketio.WSGIApp(sio, static_files=static_files)
eventlet.wsgi.server(eventlet.listen(('127.0.0.1', PORT)), app)
