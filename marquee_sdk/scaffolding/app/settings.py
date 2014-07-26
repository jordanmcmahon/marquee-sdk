from marquee_sdk.config import MARQUEE_API_DEFAULTS as DEFAULTS

from uuid import uuid4

import json
import os

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))

# Load .marquee-runtime configuration into os environs
try:
    RUNTIME_CONFIG = json.load(file(os.path.join(PROJECT_DIR, '.marquee-runtime')))
except IOError:
    RUNTIME_CONFIG = {}
for key, value in RUNTIME_CONFIG.iteritems():
    os.environ[key.upper()] = value

# App config
HOST                    = os.environ.get('RUNTIME_HOST', '127.0.0.1')
PORT                    = os.environ.get('RUNTIME_PORT', 5000)
DEBUG                   = os.environ.get('DEBUG', False)
REDIS_URL               = os.environ.get('REDIS_URL', 'http://127.0.0.1')
SECRET_KEY              = os.environ.get('SECRET_KEY', uuid4().hex)
STATIC_URL              = os.environ.get('STATIC_URL', '/static/')
ELASTIC_SEARCH_URL      = os.environ.get('ELASTIC_SEARCH_URL', "127.0.01:9200")
ELASTIC_SEARCH_USER     = os.environ.get('ELASTIC_SEARCH_USER', None)
ELASTIC_SEARCH_PASSWORD = os.environ.get('ELASTIC_SEARCH_PASSWORD', None)

# Marquee API config
MARQUEE_TOKEN           = os.environs.get('MARQUEE_TOKEN'       , DEFAULTS['marquee_token'])
PUBLICATION_SLUG        = os.environs.get('PUBLICATION_SLUG'    , DEFAULTS['publication_slug'])
MARQUEE_API_ROOT        = os.environs.get('MARQUEE_API_ROOT'    , DEFAULTS['marquee_api_root'])
LIB_CDN_ROOT            = os.environs.get('LIB_CDN_ROOT'        , DEFAULTS['lib_cdn_root'])
ASSET_CDN_ROOT          = os.environs.get('ASSET_CDN_ROOT'      , DEFAULTS['asset_cdn_root'])
CACHE_SOFT_EXIPIRY      = int(os.environ.get('CACHE_SOFT_EXPIRY', DEFAULTS['cache_soft_expiry']))
