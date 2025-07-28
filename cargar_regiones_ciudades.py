
from cataliticos.models import Region, Ciudad

# Script para poblar regiones y ciudades de Chile en la base de datos Django

# Lista de regiones y ciudades principales (puedes expandirla según necesidad)
regiones_ciudades = {
    "Arica y Parinacota": ["Arica", "Putre"],
    "Tarapacá": ["Iquique", "Alto Hospicio", "Pozo Almonte"],
    "Antofagasta": ["Antofagasta", "Calama", "Tocopilla", "Mejillones"],
    "Atacama": ["Copiapó", "Vallenar", "Caldera", "Chañaral"],
    "Coquimbo": ["La Serena", "Coquimbo", "Ovalle", "Illapel"],
    "Valparaíso": ["Valparaíso", "Viña del Mar", "Quilpué", "San Antonio", "Quillota"],
    "Metropolitana de Santiago": ["Santiago", "Puente Alto", "Maipú", "La Florida", "Las Condes", "San Bernardo", "Peñalolén", "Pudahuel", "Ñuñoa", "La Pintana", "Quilicura", "Lo Barnechea", "El Bosque", "Recoleta", "Macul", "Independencia", "Cerrillos", "Conchalí", "La Reina", "Providencia", "Renca", "San Miguel", "Pedro Aguirre Cerda", "Lo Espejo", "Estación Central", "San Joaquín", "La Cisterna", "Lo Prado", "San Ramón", "Huechuraba", "Cerro Navia", "Vitacura"],
    "O'Higgins": ["Rancagua", "San Fernando", "Rengo", "Santa Cruz"],
    "Maule": ["Talca", "Curicó", "Linares", "Cauquenes"],
    "Ñuble": ["Chillán", "San Carlos", "Bulnes"],
    "Biobío": ["Concepción", "Talcahuano", "Coronel", "Los Ángeles", "San Pedro de la Paz", "Hualpén", "Chiguayante", "Lota", "Tomé", "Penco"],
    "La Araucanía": ["Temuco", "Angol", "Villarrica", "Padre Las Casas"],
    "Los Ríos": ["Valdivia", "La Unión", "Río Bueno"],
    "Los Lagos": ["Puerto Montt", "Osorno", "Castro", "Puerto Varas"],
    "Aysén": ["Coyhaique", "Puerto Aysén", "Chile Chico"],
    "Magallanes": ["Punta Arenas", "Puerto Natales", "Porvenir"]
}

def poblar():
    for region_nombre, ciudades in regiones_ciudades.items():
        region, _ = Region.objects.get_or_create(nombre=region_nombre)
        for ciudad_nombre in ciudades:
            Ciudad.objects.get_or_create(nombre=ciudad_nombre, region=region)
    print("Regiones y ciudades cargadas correctamente.")

if __name__ == "__main__":
    poblar()
