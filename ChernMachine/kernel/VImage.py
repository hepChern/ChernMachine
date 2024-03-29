import os, sys
import json
import subprocess
from Chern.utils import csys
from Chern.utils import metadata
from ChernMachine.kernel.VJob import VJob
from Chern.kernel.VImpression import VImpression
"""
This should have someting
A image can be determined uniquely by the ?
"""
import logging
class VImage(VJob):
    def __init__(self, path, machine_id):
        super(VImage, self).__init__(path, machine_id)

    def run(self):
        self.prepare()
        self.build()

    def build(self):
        """
        Build the image to change the status of the Algorithm to builded.
        It will create a unique VImage object and the md5 of the VImage will be saved.
        """
        """
            What to do:
            first: copy all the files to a temporary file directory and next
            write a docker file
            then, you should build the docker file
        """
        # if (machine is the local machine): build the image
        os.chdir(self.run_path)
        
        stdout = open("docker.stdout", "wb")
        stderr = open("docker.stderr", "wb")
        ps = subprocess.open("docker build .", shell=True,
                              stdout=stdout, stderr=stderr)
        ps.wait()
        stdout.close()
        stderr.close()

        # Key output message:
        stderr = open("docker.stderr", "r")
        info = stderr.read()
        print(info)
        print(type(info))
        shastart = info.rfind("sha256:")
        shacode = info[shastart+7:shastart+71]
        # This shacode should be saved in the status.json file
        self.config_file.write_variable("sha_code", shacode)

    def prepare(self):
        impression = VImpression(self.impression)
        csys.copy_tree(impression.path, self.run_path)

    def inspect(self):
        ps = subprocess.Popen("docker inspect {0}".format(self.image_id().decode()), shell=True, stdout=subprocess.PIPE)
        info = ps.communicate()
        json_info = json.loads(info[0])
        return json_info[0]


    def is_locked(self):
        status_file = metadata.ConfigFile(os.path.join(self.path, "status.json"))
        status = status_file.read_variable("status")
        return status == "locked"

    
    def image_id(self):
        dirs = csys.list_dir(self.path)
        for run in dirs:
            if run.startswith("run."):
                config_file = metadata.ConfigFile(os.path.join(self.path, run, "status.json"))
                status = config_file.read_variable("status", "submitted")
                if status == "built":
                    return config_file.read_variable("image_id")
        return ""

    def machine_storage(self):
        config_file = metadata.ConfigFile(os.path.join(os.environ["HOME"], ".ChernMachine/config.json"))
        machine_id = config_file.read_variable("machine_id")
        return "run." + machine_id

    
    def satisfied(self):
        return True

    