# cataliticos/management/commands/actualizar_valores.py

import requests
from django.core.management.base import BaseCommand
from cataliticos.models import Catalitico

class Command(BaseCommand):
    help = 'Actualiza el valor ajustado de cada catalítico usando precios de metales'

    def handle(self, *args, **kwargs):
        API_KEY = '27abd101e5bb2d9b1edd6691587b5aab'
        url = 'https://api.metalpriceapi.com/v1/latest'
        params = {
            'api_key': API_KEY,
            'base': 'USD',
            'symbols': 'XPT,XPD'
        }

        # Valor fijo de rodio (actualizado manualmente dos veces al mes)
        rodio_usd = 5600.00

        try:
            response = requests.get(url, params=params)
            data = response.json()

            if data.get('success') and 'rates' in data:
                platino_raw = data['rates'].get('XPT')
                paladio_raw = data['rates'].get('XPD')

                precio_platino = round(1 / platino_raw, 2) if platino_raw else None
                precio_paladio = round(1 / paladio_raw, 2) if paladio_raw else None

                if not (precio_platino and precio_paladio):
                    self.stderr.write("❌ Error: precios de platino o paladio inválidos.")
                    return

                # Índice promedio usando los 3 metales
                indice = (precio_platino + precio_paladio + rodio_usd) / 3000

                cataliticos = Catalitico.objects.all()
                for c in cataliticos:
                    nuevo_valor = round(c.valor_base * indice, 2)
                    c.valor_ajustado = nuevo_valor
                    c.save()

                self.stdout.write(self.style.SUCCESS(
                    f"✅ {cataliticos.count()} catalíticos actualizados con índice {indice:.3f}"))

            else:
                self.stderr.write("❌ No se pudieron obtener las tasas desde la API.")
                print(data)

        except Exception as e:
            self.stderr.write(f"❌ Error al consultar API: {e}")
