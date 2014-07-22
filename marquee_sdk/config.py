from os.path import dirname, expanduser, join

SDK_DIR                 = dirname(__file__)
DIGITAL_OCEAN_CONFIG    = join(SDK_DIR, '.digitalocean')
TEMPLATE_DIR            = join(SDK_DIR, 'scaffolding')
PUB_KEY                 = join(expanduser('~'), '.ssh', 'id_rsa.pub')
PROVIDERS               = ['digitalocean',]

class FakeSectionHead(object):
    def __init__(self, fp):
        self.fp = fp
        self.sechead = '[config]\n'
    def readline(self):
        if self.sechead:
            try: return self.sechead
            finally: self.sechead = None
        else: return self.fp.readline()
