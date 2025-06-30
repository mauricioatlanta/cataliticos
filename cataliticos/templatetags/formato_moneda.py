from django import template

register = template.Library()

@register.filter
def formato_pesos(value):
    """
    Formatea un número como moneda chilena: $40.000
    """
    if value is None:
        return "$0"
    
    try:
        # Convertir a entero
        valor_int = int(float(value))
        # Formatear con puntos como separadores de miles
        valor_formateado = f"{valor_int:,}".replace(",", ".")
        return f"${valor_formateado}"
    except (ValueError, TypeError):
        return "$0"

@register.filter
def formato_pesos_sin_signo(value):
    """
    Formatea un número como moneda chilena sin el signo $: 40.000
    """
    if value is None:
        return "0"
    
    try:
        # Convertir a entero
        valor_int = int(float(value))
        # Formatear con puntos como separadores de miles
        valor_formateado = f"{valor_int:,}".replace(",", ".")
        return valor_formateado
    except (ValueError, TypeError):
        return "0"
