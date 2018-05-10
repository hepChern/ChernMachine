import daemon
import tarfile
from daemon import pidfile
import subprocess
from flask import Flask
from flask import request
from flask import send_from_directory
import os

app = Flask(__name__)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        tarname = request.form["tarname"]
        storage_path = os.path.join(os.environ["HOME"], ".ChernMachine/Storage")
        request.files[tarname].save(os.path.join("/tmp", tarname))

        tar = tarfile.open(os.path.join("/tmp", tarname),"r")
        for ti in tar:
            tar.extract(ti, os.path.join(storage_path, tarname.rstrip("tar.gz")))
        tar.close()

@app.route("/download/<filename>", methods=['GET'])
def download_file(filename):
    directory = os.getcwd()+"/data"  # 假设在当前目录
    return send_from_directory(directory, filename, as_attachment=True)

@app.route("/test", methods=['GET'])
def test():
    return "Good"

def start():
    daemon_path = os.path.join(os.environ["HOME"], ".ChernMachine/daemon")
    with daemon.DaemonContext(
        working_directory="/",
        pidfile=pidfile.TimeoutPIDLockFile(daemon_path + "/server.pid"),
        stderr=open(daemon_path + "/server.log", "w+"),
        ):
        app.run()

def stop():
    if status() == "stop":
        return
    daemon_path = os.path.join(os.environ["HOME"], ".ChernMachine/daemon")
    subprocess.call("kill {}".format(open(daemon_path + "/server.pid").read()), shell=True)

def status():
    pass
