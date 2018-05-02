""" """
import click
import os
import Chern
from Chern.kernel import VProject
from Chern.kernel.ChernDaemon import start as daemon_start
from Chern.kernel.ChernDaemon import stop as daemon_stop
from Chern.utils import csys
from Chern.kernel.ChernDatabase import ChernDatabase

@click.group()
@click.pass_context
def cli(ctx):
    """ Chern command only is equal to `Chern ipython`
    """
    if is_first_time():
        start_first_time()
    if ctx.invoked_subcommand is None:
        try:
            start_chern_ipython()
        except:
            print("Fail to start ipython")

def register():
    """ Register the running machine
    """

def connections():

def

