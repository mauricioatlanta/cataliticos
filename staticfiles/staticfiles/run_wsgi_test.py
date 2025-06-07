import os
import sys

# Aseguramos que Python vea la raíz del proyecto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configura el módulo de settings de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cataliticos_project.settings')

# Intenta cargar la app WSGI
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

print("✅ WSGI cargado correctamente:", application)
