import json
import os

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))

# Load .marquee-runtime configuration into os environs
try:
    RUNTIME_CONFIG = json.load(file(os.path.join(PROJECT_DIR, '.marquee-runtime')))
except IOError:
    from marquee_sdk.config import RUNTIME_CONFIG
for key, value in RUNTIME_CONFIG.iteritems():
    os.environ[key.upper()] = value

# App config
PORT                    = asInt('port', 5000)
HOST                    = RUNTIME_CONFIG.get('runtime_host', '127.0.0.1')
DEBUG                   = RUNTIME_CONFIG.get('debug', False)
ENVIRONMENT             = RUNTIME_CONFIG.get('environment', 'production')

REDIS_URL               = os.environ.get('REDIS_URL')
SECRET_KEY              = os.environ['SECRET_KEY']
STATIC_URL              = os.environ['STATIC_URL']

# Content API config
CONTENT_API_TOKEN       = os.environ['CONTENT_API_TOKEN']
CONTENT_API_ROOT        = os.environ['CONTENT_API_ROOT']
CACHE_SOFT_EXPIRY       = int(os.environ['CACHE_SOFT_EXPIRY'])  # minutes
PUBLICATION_SHORT_NAME  = os.environ['PUBLICATION_SHORT_NAME']
PUBLICATION_NAME        = os.environ.get('PUBLICATION_NAME', u'')

ELASTIC_SEARCH_URL      = os.environ.get('ELASTIC_SEARCH_URL', "127.0.01:9200")
ELASTIC_SEARCH_USER     = os.environ.get('ELASTIC_SEARCH_USER', None)
ELASTIC_SEARCH_PASSWORD = os.environ.get('ELASTIC_SEARCH_PASSWORD', None)
