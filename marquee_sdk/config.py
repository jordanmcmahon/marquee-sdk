from os.path    import dirname, expanduser, join
from uuid       import uuid4


SDK_DIR                 = dirname(__file__)



DIGITAL_OCEAN_CONFIG    = join(SDK_DIR, '.digitalocean')
SLACK_CONFIG            = join(SDK_DIR, '.slack')
TEMPLATE_DIR            = join(SDK_DIR, 'scaffolding')
DEPLOY_LOCK_PATH        = join('/', 'tmp', 'deploy.lock')
PUB_KEY                 = join(expanduser('~'), '.ssh', 'id_rsa.pub')
PROVIDERS               = ['digitalocean',]
SERVICES                = ['slack', 'digitalocean']
RUNTIME_CONFIG          = {
    'marquee_token'     : 'r0_35d6671277c356e582c07f490121483dc05d6a40',
    'cache_soft_expiry' : 10,
    'content_api_root'  : 'marquee.by/content/',
    'lib_cdn_root'      : 'marquee-cdn.net',
    'asset_cdn_root'    : 'assets.marquee-cdn.net/',
    'static_url'        : '/static/',
    'secret_key'        : uuid4().hex,
}

MARQUEE_API_DEFAULTS = {
    'marquee_token'     : 'r0_35d6671277c356e582c07f490121483dc05d6a40',
    'publication_slug'  : 'gutenberg',
    'api_root'          : 'marquee.by/content',
    'lib_cdn_root'      : 'marquee-cdn.net',
    'asset_cdn_root'    : 'assets.marquee-cdn.net',
    'cache_soft_expiry' : 10,
}

class FakeSectionHead(object):
    def __init__(self, fp):
        self.fp = fp
        self.sechead = '[config]\n'
    def readline(self):
        if self.sechead:
            try: return self.sechead
            finally: self.sechead = None
        else: return self.fp.readline()
