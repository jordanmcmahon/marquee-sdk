from flask              import Flask, render_template, abort, redirect
from flask.ext.cache    import Cache

from .template_helpers  import *

import os
import settings

template_folder = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../', 'templates')
)

def inject_publication():
    return dict(publication=loadPublication())

def create_app():
    app = Flask(
        __name__,
        template_folder = template_folder,
        static_url_path = '/static',
        static_folder   = '../static',
    )

    # Configure app based on .env file
    app.config.from_object(settings)

    # Add various items to the template globals
    app.jinja_env.globals.update({
            'ENVIRONMENT'       : settings.ENVIRONMENT,
            'DEBUG'             : settings.DEBUG,
            'READER_TOKEN'      : settings.CONTENT_API_TOKEN,
            'CONTENT_API_ROOT'  : settings.CONTENT_API_ROOT,
            'staticURL'         : staticURL,
            'mediaURL'          : mediaURL,
        })

    app.jinja_env.filters.update({
            'toItemSize'        : toItemSize,
            'renderBlock'       : renderBlock,
            'contentPreview'    : contentPreview,
            'renderCover'       : renderCover,
            'asModel'           : asModel,
            'slugify'           : slugify,
            'cgiEscape'         : cgiEscape,
        })

    return app

app = create_app()
cache = Cache(app, config={
    'CACHE_TYPE'        : 'memcached',
})