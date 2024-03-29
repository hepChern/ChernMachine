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
from Chern.utils.metadata import ConfigFile
import sys
from celery import Celery
from logging import getLogger
import logging


app = Flask(__name__)

# logging.basicConfig(level=logging.DEBUG)
logger = getLogger("ChernMachineLogger")
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('[%(asctime)s][%(levelname)s] - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

app.config['SECRET_KEY'] = 'top-secret!'

# Celery configuration
app.config['CELERY_BROKER_URL'] = 'amqp://localhost'
app.config['CELERY_RESULT_BACKEND'] = 'rpc://'

celeryapp = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celeryapp.conf.update(app.config)

import sqlite3

def connect():
    conn = sqlite3.connect(os.path.join(os.environ["HOME"], '.ChernMachine/Storage/impressions.db') )
    return conn

@celeryapp.task
def task_exec_impression(impression_uuid, machine_uuid):
    job_path = os.path.join(os.environ["HOME"], ".ChernMachine/Storage", impression_uuid)
    job = VJob(path, machine_uuid)
    if job.job_type() == "image":
        job = VImage(job_path, machine_uuid)
    if job.job_type() == "container":
        job = VContainer(job_path, machine_uuid)
    return job.run()

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

        config = request.form['config']
        logger.info(config)
        request.files[config].save(os.path.join(storage_path, tarname[:-7], config))
    # FIXME should check whether the upload is successful or not
    return ""

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
    directory = os.path.join(os.getcwd(), "data")  # 假设在当前目录
    return send_from_directory(directory, filename, as_attachment=True)

@app.route("/status/<impression>", methods=['GET'])
def status(impression):
    path = os.path.join(os.environ["HOME"], ".ChernMachine/Storage", impression)
    runner_config_path = os.path.join(os.environ["HOME"], ".ChernMachine/", "config.json")
    runner_config_file = ConfigFile(runner_config_path)
    runners = runner_config_file.read_variable("runners", [])
    runner_id = runner_config_file.read_variable("runner_id", {})
    config_path = os.path.join(os.environ["HOME"], ".ChernMachine/", "runner_config.json")
    config_file = ConfigFile(config_path)
    machine_id = config_file.read_variable("machine_id", "")

    runners.insert(0, "local")
    runner_id["local"] = machine_id

    logger.info(runners)
    logger.info(runner_id)

    object_type = ConfigFile(os.path.join(os.environ["HOME"], ".ChernMachine/Storage", impression, "config.json")).read_variable("object_type", "")
    logger.info(object_type)

    for machine in runners:
        machine_id = runner_id[machine]
        job_path = os.path.join(os.environ["HOME"], ".ChernMachine/", impression)

        if object_type == "":
            return "unsubmitted"

        if object_type == "algorithm":
            image = VImage(job_path, machine_id)
            runid = image.runid()
            if runid != "":
                results = task_exec_impression.AsyncResult(runid)
                image.update_status(results.status)
            status = image.status()
            return status
        if object_type == "task":
            logger.info("container")
            return VContainer(job_path, machine_id).status()
        if os.path.exists(job_path):
            return "submitted"
    return "unsubmitted"

@app.route("/serverstatus", methods=['GET'])
def serverstatus():
    return "ok"

@app.route("/run/<impression>/<machine>", methods=['GET'])
def run(impression, machine):
    # We need to save the run id to the id of job
    task = task_exec_impression(impression, machine).apply_async()
    VJob(impression, machine).set_runid(task.id)
    return task.id

@app.route("/register_machine/<machine>/<machine_id>", methods=['GET'])
def register_machine(machine, machine_id):
    config_path = os.path.join(os.environ["HOME"], ".ChernMachine/", "config.json")
    config_file = ConfigFile(config_path)
    runners = config_file.read_variable("runners", [])
    runner_id = config_file.read_variable("runner_id", {})
    runners.append(machine)
    runner_id[machine] = machine_id
    config_file.write_variable("runners", runners)
    config_file.write_variable("runner_id", runner_id)

@app.route("/machine_id/<machine>", methods=["GET"])
def machine_id(machine):
    # print some debug information
    if (machine == "local"):
        config_path = os.path.join(os.environ["HOME"], ".ChernMachine/", "runner_config.json")
        config_file = ConfigFile(config_path)
        machine_id = config_file.read_variable("machine_id", "")
        return machine_id
    else:
        config_path = os.path.join(os.environ["HOME"], ".ChernMachine/", "runner_config.json")
        config_file = ConfigFile(config_path)
        runner_id = config_file.read_variable("runner_id", {})
        return runner_id[machine]

# @app.route("/runstatus/<impression>", method=['GET'])
# def runstatus(impression):
#     #task_id = get_run_id(impression)
#     # long_task.AsyncResult(task_id)
#     #return statu0s
#     return ""

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

    return redirect(url_for('index'))

def server_start():
    daemon_path = os.path.join(os.environ["HOME"], ".ChernMachine/daemon")
    print("Trying to start server")

    # with daemon.DaemonContext(
    #     pidfile=pidfile.TimeoutPIDLockFile(daemon_path + "/server.pid"),
    #     stderr=open(daemon_path + "/server.log", "w+"),
    #     ):
    app.run(
        host='127.0.0.1',
        port= 3315,
        debug=True,
        )

def stop():
    if status() == "stop":
        return
    daemon_path = os.path.join(os.environ["HOME"], ".ChernMachine/daemon")
    subprocess.call("kill {}".format(open(daemon_path + "/server.pid").read()), shell=True)
    subprocess.call("kill {}".format(open(daemon_path + "/runner.pid").read()), shell=True)

def status():
    pass
