import requests
from django.core.management.base import BaseCommand
from cataliticos.models import PrecioMetal

API_KEY = "goldapi-43fm8jl19mbrh93i3-io"
API_URL = "https://www.goldapi.io/api"

METALES = {
    "platino": "XPT",
    "paladio": "XPD",
    "rodio": "XRH"  # ⚠️ si no existe, se omite
}

class Command(BaseCommand):
    help = "Actualiza los precios de metales desde GoldAPI"

    def handle(self, *args, **kwargs):
        headers = {
            "x-access-token": API_KEY,
            "Content-Type": "application/json"
        }

        for nombre, simbolo in METALES.items():
            url = f"{API_URL}/{simbolo}/EUR"
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                precio = data.get("price")
                if precio:
                    obj, creado = PrecioMetal.objects.update_or_create(
                        nombre__iexact=nombre,
                        defaults={"valor_eur_gramo": precio}
                    )
                    self.stdout.write(self.style.SUCCESS(f"{nombre.title()} actualizado: {precio} EUR/GR"))
                else:
                    self.stdout.write(self.style.WARNING(f"No se encontró precio para {nombre}"))
            else:
                self.stdout.write(self.style.ERROR(f"Error {response.status_code} para {nombre}"))
