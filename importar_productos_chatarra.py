import os
import csv
import django
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cataliticos_project.settings')
django.setup()

from cataliticos.models import ProductoChatarra

csv_path = os.path.join('cataliticos', 'static', 'catalogo_chatarra', 'catalogo_chatarra.csv')
img_base = os.path.join('cataliticos', 'static', 'catalogo_chatarra', 'imagenes')

with open(csv_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        producto, created = ProductoChatarra.objects.get_or_create(
            codigo=row["Código"],
            defaults={
                "nombre": row["Nombre"],
                "precio_kg": int(row["Precio Compra CLP"]),
            }
        )
        # Asocia imagen si existe
        img_filename = row.get("Imagen")
        if img_filename:
            img_path = os.path.join(img_base, img_filename)
            if os.path.exists(img_path):
                # Generar nombre de imagen más claro: codigo_nombre_original
                nombre_limpio = row["Nombre"].replace(" ", "_").replace("/", "-")
                nuevo_nombre = f"{row['Código']}_{nombre_limpio}_{img_filename}"
                with open(img_path, 'rb') as f:
                    producto.imagen.save(nuevo_nombre, File(f), save=True)
