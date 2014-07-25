from .config    import SLACK_CONFIG
from .utils     import load_config

import os

class SlackClient(object):
    def __init__(self):
        if not os.path.exists(SLACK_CONFIG):
            raise IOError
        slack_config    = load_config(SLACK_CONFIG)
        self.channel    = slack_config['channel']
        self.token      = slack_config['token']
        self.endpoint   = slack_config['endpoint']

    def notify(message):
        print message
        return True
