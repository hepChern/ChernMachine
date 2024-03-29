import os
from Chern.utils import utils
from Chern.utils import csys
from Chern.utils import metadata
from logging import getLogger

class VJob(object):
    """ Virtual class of the objects, including VVolume, VImage, VContainer
    """

    def __init__(self, path, machine_id):
        """ Initialize the project the only **information** of a object instance
        """
        self.path = csys.strip_path_string(path)
        self.mathine_id = machine_id
        self.run_path = os.path.join(path, machine_id, "run")
        self.config_file = metadata.ConfigFile(
            os.path.join(self.path, machine_id, "config.json")
            )

    def __str__(self):
        """ Define the behavior of print(vobject)
        """
        return self.path

    def __repr__(self):
        """ Define the behavior of print(vobject)
        """
        return self.path

    def relative_path(self, path):
        """ Return a path relative to the path of this object
        """
        return os.path.relpath(path, self.path)

    def job_type(self):
        """ Return the type of the object under a specific path.
        If path is left blank, return the type of the object itself.
        """
        return self.config_file.read_variable("object_type", "")

    def is_zombie(self):
        return self.job_type() == ""

    def set_runid(self, runid):
        self.config_file.write_variable("runid", runid)

    def runid(self):
        return self.config_file.read_variable("runid", "")

    """ Let's consider when to update the status later
    """
    def status(self):
        logger = getLogger("ChernMachineLogger")
        config_file = metadata.ConfigFile(os.path.join(self.path, "status.json"))
        logger.info(self.path)
        status = config_file.read_variable("status", "submitted")
        if status != "submitted":
            return status
        return "submitted"

    def update_status(self, status):
        self.config_file.write_variable("status", status)

    def error(self):
        if os.path.exists(self.path+"/error"):
            f = open(self.path+"/error")
            error = f.read()
            f.close()
            return error
        else:
            return ""

    def append_error(self, message):
        with open(self.path+"/error", "w") as f:
            f.write(message)
            f.write("\n")
