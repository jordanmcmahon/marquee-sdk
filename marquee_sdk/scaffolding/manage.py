from flask                      import Flask
from flask.ext.script           import Manager, Server

from app                        import settings
from app.template_helpers       import staticURL

from app.context_processors     import *
from app.views                  import *

# Create and configure app
app = Flask(__name__)
app.config.from_object(settings)

# Add custom data to the application context
app.context_processor(inject_publication)

# Register routes
PublicationView.register(app, route_base='/')

# Load template helpers and extensions
app.jinja_env.globals.update(staticURL=staticURL)

# Set up manager
manager = Manager(app)
manager.add_command('runserver', Server())

# Main application loop
if __name__ == '__main__':
    manager.run()
