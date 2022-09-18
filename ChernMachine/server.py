import daemon
import tarfile
from daemon import pidfile
import subprocess
from flask import Flask
from flask import request
from flask import render_template
from flask import send_from_directory
import os

from ChernMachine.kernel.VJob import VJob
from ChernMachine.kernel.VImage import VImage
from ChernMachine.kernel.VContainer import VContainer

from celery import Celery

app = Flask(__name__)
# app.config['SECRET_KEY'] = 'top-secret!'

# Flask-Mail configuration

# Celery configuration
# app.config['CELERY_BROKER_URL'] = 'amqp://localhost'
# app.config['CELERY_RESULT_BACKEND'] = 'amqp'

# celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
# celery.conf.update(app.config)

import sqlite3

def connect():
    conn = sqlite3.connect(os.path.join(os.environ["HOME"], '.ChernMachine/Storage/impressions.db') )
    return conn

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

        tarname = request.form["tarname"]
        storage_path = os.path.join(os.environ["HOME"], ".ChernMachine/Storage")
        request.files[tarname].save(os.path.join("/tmp", tarname))

        tar = tarfile.open(os.path.join("/tmp", tarname),"r")
        for ti in tar:
            tar.extract(ti, os.path.join(storage_path, tarname[:-7]))
        tar.close()

        # Seems to be useless
        #conn = connect()
        #c = conn.cursor()
        #c.execute('''CREATE TABLE IF NOT EXISTS IMPRESSIONS
        #(ID           TEXT    NOT NULL,
        #STATUS          TEXT     NOT NULL,
        #REPOSITORY        TEXT);''')
        #c.execute("INSERT INTO IMPRESSIONS (ID,STATUS,REPOSITORY) VALUES (?, 'new', 'hehe')", (tarname[:-7],));

        #conn.commit()
        #conn.close()

@app.route("/download/<filename>", methods=['GET'])
def download_file(filename):
    directory = os.getcwd()+"/data"  # 假设在当前目录
    return send_from_directory(directory, filename, as_attachment=True)

@app.route("/test", methods=['GET'])
def test():
    return "Good"

@app.route("/status/<impression>", methods=['GET'])
def status(impression):
    path = os.path.join(os.environ["HOME"], ".ChernMachine/Storage", impression)
    job = VJob(path)
    if job.job_type() == "image":
        return VImage(path).status()
    if job.job_type() == "container":
        return VContainer(path).status()
    if os.path.exists(path):
        return "submitted"
    return "unsubmitted"

@app.route("/serverstatus", methods=['GET'])
def serverstatus():
    return "ok"


@app.route("/outputs/<impression>", methods=['GET'])
def outputs(impression):
    path = os.path.join(os.environ["HOME"], ".ChernMachine/Storage", impression)
    job = VJob(path)
    if job.job_type() == "container":
        return " ".join(VContainer(path).outputs())
    return ""

@app.route("/getfile/<impression>/<filename>", methods=['GET'])
def get_file(impression, filename):
    path = os.path.join(os.environ["HOME"], ".ChernMachine/Storage", impression)
    job = VJob(path)
    if job.job_type() == "container":
        return VContainer(path).get_file(filename)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        conn = connect()
        c = conn.cursor()
        cursor = c.execute("SELECT ID, STATUS from IMPRESSIONS")
        impressions = []
        for row in cursor:
            impression = {}
            impression["id"] = row[0]
            impression["status"] = row[1]
            impression["size"] = "unknown"
            impressions.append(impression)
        conn.commit()
        conn.close()

        return render_template('index.html', impressions=impressions)
        return out

    return redirect(url_for('index'))


def start():
    daemon_path = os.path.join(os.environ["HOME"], ".ChernMachine/daemon")
    print("Trying to start runner")
    with daemon.DaemonContext(
        working_directory="/",
        pidfile=pidfile.TimeoutPIDLockFile(daemon_path + "/server.pid"),
        stderr=open(daemon_path + "/server.log", "w+"),
        ):
        app.run(
                host='127.0.0.1',
                port= 3315,
                )

def stop():
    if status() == "stop":
        return
    daemon_path = os.path.join(os.environ["HOME"], ".ChernMachine/daemon")
    subprocess.call("kill {}".format(open(daemon_path + "/server.pid").read()), shell=True)

def status():
    pass
