from django.core.management.base import BaseCommand
from cataliticos.models import ProductoChatarra
import csv
import os
from django.conf import settings
from django.core.files import File

class Command(BaseCommand):
    help = 'Carga imágenes faltantes para productos chatarra desde un CSV mapping.'

    def add_arguments(self, parser):
        parser.add_argument('--csv', type=str, default='imagenes_faltantes.csv', help='Ruta al archivo CSV mapping (codigo,nombre_archivo)')
        parser.add_argument('--src', type=str, default=os.path.join(settings.BASE_DIR, 'static', 'catalogo_chatarra', 'imagenes_faltantes'), help='Carpeta origen de imágenes')

    def handle(self, *args, **options):
        csv_path = options['csv']
        src_folder = options['src']
        media_folder = os.path.join(settings.MEDIA_ROOT, 'chatarra')
        if not os.path.exists(media_folder):
            os.makedirs(media_folder)
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                codigo = row['codigo']
                nombre_archivo = row['nombre_archivo']
                producto = ProductoChatarra.objects.filter(codigo=codigo).first()
                if not producto:
                    self.stdout.write(self.style.WARNING(f'Producto con código {codigo} no encontrado.'))
                    continue
                src_path = os.path.join(src_folder, nombre_archivo)
                if not os.path.exists(src_path):
                    self.stdout.write(self.style.ERROR(f'Imagen {src_path} no existe.'))
                    continue
                dest_path = os.path.join(media_folder, nombre_archivo)
                # Copiar imagen si no existe en destino
                if not os.path.exists(dest_path):
                    with open(src_path, 'rb') as fsrc, open(dest_path, 'wb') as fdst:
                        fdst.write(fsrc.read())
                # Actualizar campo imagen
                producto.imagen.name = f'chatarra/{nombre_archivo}'
                producto.save()
                self.stdout.write(self.style.SUCCESS(f'Imagen cargada y asignada para producto {codigo}'))
        self.stdout.write(self.style.SUCCESS('Proceso finalizado.'))
