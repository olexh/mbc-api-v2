from apscheduler.schedulers.background import BackgroundScheduler
from flask import jsonify, render_template
from flask_socketio import SocketIO
from flask_caching import Cache
from flask_cors import CORS
from flask import Flask
from . import utils
import eventlet
import config
import time

eventlet.monkey_patch()

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config["SECRET_KEY"] = config.secret
cache = Cache(config={"CACHE_TYPE": "simple"})
sio = SocketIO(app, cors_allowed_origins="*", message_queue="redis://")
cache.init_app(app)
CORS(app)

start_time = time.monotonic()

watch_addresses = {}
subscribers = {}
connections = 0
thread = None

from .sync import sync_blocks
from .esplora import esplora
from .rest import rest
from . import socket

app.register_blueprint(esplora)
app.register_blueprint(rest)
socket.init(sio)

@app.route("/")
def frontend():
    return render_template("index.html")

@app.errorhandler(404)
def page_404(error):
    return jsonify(utils.dead_response("Method not found"))


background = BackgroundScheduler()
background.add_job(sync_blocks, "interval", seconds=10)
background.start()
