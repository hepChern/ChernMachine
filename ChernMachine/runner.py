#!/usr/bin/python3
"""
Chern machine runner
With celery, the only usage of this runner is to start the celery worker
"""
import daemon
# import time
from daemon import pidfile
import os
import sys
import subprocess
# from Chern.utils import csys
# from Chern.utils import metadata
from ChernMachine.ChernDatabase import ChernDatabase
# from ChernMachine.kernel.VImage import VImage
# from ChernMachine.kernel.VContainer import VContainer
# from ChernMachine.kernel.VJob import VJob
from .server import celeryapp

cherndb = ChernDatabase.instance()

"""
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
            subprocess.Popen("chern_machine execute {}".format(job.path), shell=True)
            while (job.status() == "submitted"):
                pass
"""

def status():
    pid_file = os.path.join(os.environ["HOME"], ".ChernMachine", "daemon/runner.pid")
    if os.path.exists(pid_file):
        return "started"
    else:
        return "stopped"

def start():
    runner = celeryapp.Worker()
    runner.start()

def stop():
    if status() == "stopped":
        return
    pid_file = os.path.join(os.environ["HOME"], ".ChernMachine", "daemon/runner.pid")
    subprocess.call("kill {}".format(open(pid_file).read()), shell=True)
