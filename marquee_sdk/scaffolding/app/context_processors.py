from app.utils import loadPublication

# Context processors inject data into the template context

def inject_publication():
    return dict(publication=loadPublication())