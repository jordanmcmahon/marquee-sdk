import os
import sys

sys.path.insert(0, '/srv/{{ project_name }}/')

from app.main import app as application
from app import views
