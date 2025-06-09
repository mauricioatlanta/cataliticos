from django import template

register = template.Library()

@register.filter
def recibo_whatsapp(compra):
    mensaje = f"📄 Recibo de compra Atlanta Reciclajes\n👤 Cliente: {compra.cliente_nombre}"
    for detalle in compra.detalles.all():
        mensaje += f"\n🔧 {detalle.catalitico.codigo} - ${detalle.precio_unitario:,}"
    mensaje += f"\n💰 Total: ${compra.total():,}\n✅ ¡Gracias por preferirnos!"
    return mensaje
