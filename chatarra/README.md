# Módulo Chatarra Electrónica

Este módulo permite gestionar, mostrar y exportar un catálogo de productos de chatarra electrónica en Django.

## Instalación
1. Copia la carpeta `chatarra/` y el script `cargar_productos_chatarra.py` a tu proyecto Django.
2. Instala los requisitos:
   ```bash
   pip install -r chatarra/requirements.txt
   ```
3. Agrega `'chatarra'` a `INSTALLED_APPS` en tu `settings.py`.
4. Incluye las rutas en tu `urls.py` principal:
   ```python
   path('chatarra-electronica/', include('chatarra.urls')),
   ```
5. Ejecuta las migraciones:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
6. Carga productos usando el script o el admin.

## Funcionalidades
- Catálogo web con filtro, búsqueda y paginación
- Exportación a JSON y CSV
- API REST con filtros avanzados
- Subida de imágenes
- WhatsApp directo por producto

## Contacto
Para soporte o personalización, escribe a contacto@tudominio.cl
