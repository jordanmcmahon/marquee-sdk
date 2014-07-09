from flask              import Flask, render_template, abort, redirect
from flask.ext.cache    import Cache

from .views             import (PublicationView, loadPublication)
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

    # Automatically inject stuff into the context
    app.context_processor(inject_publication)

    # Add various items to the template globals
    app.jinja_env.globals.update({
        'ENVIRONMENT'       : settings.ENVIRONMENT,
        'DEBUG'             : settings.DEBUG,
        'READER_TOKEN'      : settings.CONTENT_API_TOKEN,
        'CONTENT_API_ROOT'  : settings.CONTENT_API_ROOT,
    })
    app.jinja_env.globals.update(staticURL=staticURL)
    app.jinja_env.globals.update(mediaURL=mediaURL)

    app.jinja_env.filters['toItemSize']     = toItemSize
    app.jinja_env.filters['renderBlock']    = renderBlock
    app.jinja_env.filters['contentPreview'] = contentPreview
    app.jinja_env.filters['renderCover']    = renderCover
    app.jinja_env.filters['asModel']        = asModel
    app.jinja_env.filters['slugify']        = slugify

    # Register views and routes
    PublicationView.register(app, route_base='/')

    # Activate hyperdrive if enabled
    if settings.HYPERDRIVE:
        from hyperdrive.main import hyperdrive
        app.register_blueprint(hyperdrive, url_prefix="/_hyperdrive")

    return app

app = create_app()
cache = Cache(app, config={
    'CACHE_TYPE'        : 'memcached',
})
