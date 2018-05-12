""" """
import click
import os
import Chern
from Chern.kernel import VProject
from ChernMachine.kernel.VContainer import VContainer
from ChernMachine.kernel.VJob import VJob
from ChernMachine.kernel.VImage import VImage

from Chern.kernel.ChernDaemon import start as daemon_start
from Chern.kernel.ChernDaemon import stop as daemon_stop
from Chern.utils import csys
from Chern.kernel.ChernDatabase import ChernDatabase

from ChernMachine.register import register as machine_register

from ChernMachine.server import start as server_start
from ChernMachine.server import stop as server_stop
from ChernMachine.server import status as server_status

from ChernMachine.runner import start as runner_start
from ChernMachine.runner import stop as runner_stop
from ChernMachine.runner import status as runner_status

@click.group()
@click.pass_context
def cli(ctx):
    """ Chern command only is equal to `Chern ipython`
    """
    pass

@cli.command()
def register():
    """ Register the running machine
    """
    machine_register()

def connections():
    pass

# ------ Server ------ #
@cli.group()
def server():
    pass

@server.command()
def start():
    server_start()

@server.command()
def stop():
    server_stop()

@server.command()
def status():
    server_status()

# ------ Runner ------ #
@cli.group()
def runner():
    pass

@runner.command()
def start():
    runner_start()

@runner.command()
def stop():
    runner_stop()

@runner.command()
def status():
    runner_status()

@cli.command()
@click.argument("path")
def execute(path):
    # job = create_job_instance(path)
    job = VJob(path)
    if job.is_zombie():
        return
    print(job.job_type())
    if job.job_type() == "container":
        job = VContainer(path)
    else:
        job = VImage(path)
    job.execute()

@cli.command()
@click.argument("impression")
@click.argument("path")
def feed(impression, path):
    from ChernMachine.feeder import feed as cli_feed
    cli_feed(impression, path)

# Main
def main():
    cli()

