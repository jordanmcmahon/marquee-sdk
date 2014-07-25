from .config import DEPLOY_LOCK_PATH

import pipes
import subprocess

class DeployLock(object):
    def __init__(self, host):
        self.host = host
        self.path = pipes.quote(DEPLOY_LOCK_PATH)

    def lock(self):
        cmd  = ['ssh', self.host, 'date > {0}'.format(self.path)]
        proc = subprocess.Popen(cmd)
        proc.wait()
        return proc.returncode == 0

    def unlock(self):
        cmd = ['ssh', self.host, 'rm {0}'.format(self.path)]
        proc.wait()
        return proc.returncode == 0
