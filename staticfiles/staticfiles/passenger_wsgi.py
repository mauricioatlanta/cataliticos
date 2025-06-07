import sys
import os

# Ajusta la ruta a tu proyecto
project_path = '/home/cat76477/public_html/cataliticos'
sys.path.insert(0, project_path)
sys.path.insert(0, os.path.join(project_path, 'cataliticos_project'))

# Establece el m¨®dulo de configuraci¨®n
os.environ['DJANGO_SETTINGS_MODULE'] = 'cataliticos_project.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
