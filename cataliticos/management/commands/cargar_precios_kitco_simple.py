import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from django.core.management.base import BaseCommand
from cataliticos.models import PrecioMetal

class Command(BaseCommand):
    help = "Scrapea Kitco con Selenium y regex sin espera estricta"

    def handle(self, *args, **options):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        self.stdout.write("🟡 Abriendo Kitco...")
        driver = webdriver.Chrome(options=options)
        driver.get("https://www.kitco.com/price/precious-metals")
        time.sleep(10)  # Espera más larga

        html = driver.page_source
        driver.quit()

        print("🔍 HTML INICIAL (1000 caracteres):")
        print(html[:1000])

        def extraer_variacion(texto, metal):
            pattern = rf"{metal}\s*(\d+\.\d+)[\s\S]*?\((\d+\.\d+)%\)"
            match = re.search(pattern, texto, re.IGNORECASE)
            if match:
                return float(match.group(2))
            return None

        platino_var = extraer_variacion(html, "Platinum")
        paladio_var = extraer_variacion(html, "Palladium")
        rodio_var = extraer_variacion(html, "Rhodium")

        if not any([platino_var, paladio_var, rodio_var]):
            self.stderr.write("❌ No se encontraron datos válidos. Revisa el HTML impreso arriba.")
            return

        PrecioMetal.objects.create(
            platino=platino_var,
            paladio=paladio_var,
            rodio=rodio_var
        )

        resumen = []
        if platino_var is not None: resumen.append(f"Pt {platino_var:.2f}%")
        if paladio_var is not None: resumen.append(f"Pd {paladio_var:.2f}%")
        if rodio_var is not None: resumen.append(f"Rh {rodio_var:.2f}%")

        self.stdout.write(self.style.SUCCESS("✔️ Variaciones guardadas: " + ", ".join(resumen)))
