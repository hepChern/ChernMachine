#!/usr/bin/python3
"""
Chern machine runner
"""
import daemon
import time
from daemon import pidfile
import os
import sys
import subprocess
from Chern.utils import csys
from Chern.utils import metadata
from ChernMachine.ChernDatabase import ChernDatabase
from ChernMachine.kernel.VImage import VImage
from ChernMachine.kernel.VContainer import VContainer
from ChernMachine.kernel.VJob import VJob

cherndb = ChernDatabase.instance()

def check_status():
    pending_jobs = cherndb.jobs("pending")

def execute():
    running_jobs = cherndb.jobs("running")
    if len(running_jobs) > 3:
        return

    waitting_jobs = cherndb.jobs("submitted")
    # print("List {0}".format(waitting_jobs), file=sys.stderr)
    for job in waitting_jobs:
        print("Running {0}".format(job), file=sys.stderr)
        if job.satisfied():
            print("chern_machine execute {}".format(job.path), file=sys.stderr)
            # FIXME Make sure the job will not be executed many times
            status_file = metadata.ConfigFile(os.path.join(job.path, "status.json"))
            status_file.write_variable("status", "locked")
            subprocess.Popen("chern_machine execute {}".format(job.path), shell=True)

def status():
    daemon_path = csys.daemon_path()
    pid_file = os.path.join(os.environ["HOME"], ".ChernMachine", "daemon/runner.pid")
    if os.path.exists(pid_file):
        return "started"
        pid = open(pid_file).read().decode().strip()
    else:
        return "stopped"

def start():
    pid_file = os.path.join(os.environ["HOME"], ".ChernMachine", "daemon/runner.pid")
    log_file = os.path.join(os.environ["HOME"], ".ChernMachine", "daemon/runner.log")
    with daemon.DaemonContext(
        working_directory="/",
        pidfile=pidfile.TimeoutPIDLockFile(pid_file),
        stderr=open(log_file, "w+"),
        ):
        while True:
            time.sleep(1)
            try:
                execute()
            except Exception as e:
                print(e, file=sys.stderr)

def stop():
    if status() == "stopped":
        return
    pid_file = os.path.join(os.environ["HOME"], ".ChernMachine", "daemon/runner.pid")
    subprocess.call("kill {}".format(open(pid_file).read()), shell=True)
