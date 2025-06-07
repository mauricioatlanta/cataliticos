import os
from django.core.wsgi import get_wsgi_application
import traceback

print("=== DEBUG WSGI.PY ===")
print("Working dir:", os.getcwd())
print("DJANGO_SETTINGS_MODULE:", os.environ.get('DJANGO_SETTINGS_MODULE'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cataliticos_project.settings')

try:
    application = get_wsgi_application()
    print("✅ WSGIHandler loaded")
except Exception as e:
    print("❌ Error en get_wsgi_application:")
    traceback.print_exc()
    raise
