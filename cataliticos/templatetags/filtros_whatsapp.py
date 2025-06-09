from django import template
register = template.Library()

@register.filter
def recibo_whatsapp(compra):
    return f"""📄 *Recibo de compra - Atlanta Reciclajes*%0A👤 Cliente: {compra.cliente_nombre} {compra.cliente_apellido}%0A💰 Total: ${compra.total():,}%0A✅ ¡Gracias por preferirnos!"""