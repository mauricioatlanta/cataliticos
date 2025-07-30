import os
import django
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cataliticos_project.settings')
django.setup()

from cataliticos.models import ProductoChatarra

ruta_img = os.path.join('cataliticos', 'static', 'catalogo_chatarra', 'imagenes')

productos = {
    "MEMORIA":              ("HIG0008", "memoria"),
    "MEMORIA 2":            ("HIG0008", "memoria"),
    "MEMORIA 3":            ("HIG0008", "memoria"),
    "placa dorada":         ("HIG0008", "memoria"),
    "placa madre A":        ("PMC0001-A", "placa"),
    "placa madre D":        ("PMC0004-D", "placa"),
    "placa notebook":       ("PMC0013", "placa"),
    "CAFE 300":             ("PTV0001", "placa"),
    "liviana":              ("PVE0004", "placa"),
    "disco duro":           ("HDI0001", "disco"),
    "HD 800":               ("HDI0001", "disco"),
    "fuente_de_poder":      ("SCR0004", "fuente"),
    "FUENTES 300":          ("SCR0004", "fuente"),
    "CELULAR SIN BATERIA":  ("CEL0001", "celular"),
    "fiber cpu":            ("HIG0020", "procesador"),
    "basic Fiber CPU":      ("HIG0020", "procesador"),
    "Ball Grid Array CPU":  ("HIG0020", "procesador"),
    "High-End Server CPU":  ("HIG0020", "procesador"),
    "CDROM":                ("SCR0020", "cdrom"),
}

for archivo in os.listdir(ruta_img):
    if archivo.lower().endswith(('.jpg', '.jpeg', '.png')):
        nombre_base = os.path.splitext(archivo)[0].strip()
        codigo, categoria = productos.get(nombre_base.upper(), ("SN", "otros"))

        producto, creado = ProductoChatarra.objects.get_or_create(
            codigo=codigo,
            defaults={
                "nombre": nombre_base.replace("_", " ").title(),
                "precio_kg": 1000,
                "categoria": categoria,
            }
        )

        if not producto.imagen:
            with open(os.path.join(ruta_img, archivo), 'rb') as f:
                producto.imagen.save(archivo, File(f), save=True)
