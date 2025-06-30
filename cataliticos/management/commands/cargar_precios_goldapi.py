import requests
from django.core.management.base import BaseCommand
from cataliticos.models import PrecioMetal
from datetime import date

API_KEY = "goldapi-43fm8jl19mbrh93i3-io"
API_URL = "https://www.goldapi.io/api"

METALES = {
    "platino": "XPT",
    "paladio": "XPD",
    "rodio": "XRH"  # si no existe en GoldAPI, eliminar
}

class Command(BaseCommand):
    help = "Actualiza los precios de metales desde GoldAPI"

    def handle(self, *args, **kwargs):
        headers = {
            "x-access-token": API_KEY,
            "Content-Type": "application/json"
        }

        precios = {}
        errores = []

        for campo, simbolo in METALES.items():
            url = f"{API_URL}/{simbolo}/EUR"
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                precio = data.get("price")
                if precio:
                    precios[campo] = precio
                    self.stdout.write(self.style.SUCCESS(f"{campo.title()}: {precio} EUR/GR"))
                else:
                    errores.append(campo)
            else:
                errores.append(campo)

        if precios:
            PrecioMetal.objects.create(fecha=date.today(), **precios)
            self.stdout.write(self.style.SUCCESS("Precios guardados exitosamente."))

        if errores:
            self.stdout.write(self.style.WARNING(f"Errores en: {', '.join(errores)}"))
