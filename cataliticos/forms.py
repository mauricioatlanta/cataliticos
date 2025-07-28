from django import forms
from .models import Catalitico, Cliente, CompraCatalitico, DetalleCatalitico, Region, Ciudad

class CataliticoForm(forms.ModelForm):
    class Meta:
        model = Catalitico
        fields = [
            'codigo', 'descripcion', 'proveedor',
            'valor_compra', 'valor_venta', 'cantidad', 'vendido',
            'imagen_principal', 'imagen2', 'imagen3', 'imagen4'
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Código único del catalítico',
                'style': 'text-transform: uppercase;'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Descripción del catalítico',
                'rows': 2
            }),
            'proveedor': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            }),
            'valor_compra': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Valor de compra',
                'min': '0',
                'step': '0.01'
            }),
            'valor_venta': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Valor de venta',
                'min': '0',
                'step': '0.01'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'min': '1',
            }),
            'vendido': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-green-600',
            }),
        }
        labels = {
            'codigo': 'Código *',
            'descripcion': 'Descripción',
            'proveedor': 'Proveedor',
            'valor_compra': 'Valor de compra *',
            'valor_venta': 'Valor de venta',
            'cantidad': 'Cantidad',
            'vendido': '¿Vendido?',
            'imagen_principal': 'Imagen Principal',
            'imagen2': 'Imagen 2',
            'imagen3': 'Imagen 3',
            'imagen4': 'Imagen 4',
        }
    
    def clean_codigo(self):
        """Validación personalizada para el código"""
        codigo = self.cleaned_data.get('codigo')
        if codigo:
            # Convertir a mayúsculas y limpiar espacios
            codigo = codigo.strip().upper()
            
            # Verificar si ya existe (excluyendo la instancia actual en caso de edición)
            queryset = Catalitico.objects.filter(codigo=codigo)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise forms.ValidationError(f'Ya existe un catalítico con el código "{codigo}". Los códigos deben ser únicos.')
            
            return codigo
        return codigo
    
    def clean_valor(self):
        """Validación para el valor"""
        valor = self.cleaned_data.get('valor')
        if valor is not None and valor < 0:
            raise forms.ValidationError('El valor no puede ser negativo.')
        return valor

class ClienteForm(forms.ModelForm):
    nueva_ciudad = forms.CharField(
        required=False,
        label="Agregar nueva ciudad",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Si la ciudad no existe, escríbela aquí'
        })
    )

    class Meta:
        model = Cliente
        fields = [
            'nombre', 'apellido', 'rut', 'telefono',
            'correo', 'direccion', 'region', 'ciudad'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre (requerido)'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido (opcional)'
            }),
            'rut': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'RUT (opcional)'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono (opcional)'
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Correo electrónico (opcional)'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección (opcional)'
            }),
            'region': forms.Select(attrs={
                'class': 'form-control',
            }),
            'ciudad': forms.Select(attrs={
                'class': 'form-control',
            }),
        }
        labels = {
            'nombre': 'Nombre *',
            'apellido': 'Apellido',
            'rut': 'RUT',
            'telefono': 'Teléfono',
            'correo': 'Correo Electrónico',
            'direccion': 'Dirección',
            'region': 'Región',
            'ciudad': 'Ciudad',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['region'].queryset = Region.objects.all().order_by('nombre')
        self.fields['ciudad'].queryset = Ciudad.objects.none()
        if 'region' in self.data:
            try:
                region_id = int(self.data.get('region'))
                self.fields['ciudad'].queryset = Ciudad.objects.filter(region_id=region_id).order_by('nombre')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.region:
            self.fields['ciudad'].queryset = Ciudad.objects.filter(region=self.instance.region).order_by('nombre')

    def clean(self):
        cleaned_data = super().clean()
        nueva_ciudad = cleaned_data.get('nueva_ciudad')
        region = cleaned_data.get('region')
        if nueva_ciudad and region:
            ciudad, created = Ciudad.objects.get_or_create(nombre=nueva_ciudad.strip(), region=region)
            cleaned_data['ciudad'] = ciudad
        return cleaned_data

class CompraForm(forms.ModelForm):
    class Meta:
        model = CompraCatalitico
        fields = [
            'cliente_nombre', 'cliente_apellido', 'cliente_rut', 
            'cliente_telefono', 'region', 'ciudad'
        ]
        widgets = {
            'cliente_nombre': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900',
                'placeholder': 'Nombre del cliente'
            }),
            'cliente_apellido': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900',
                'placeholder': 'Apellido del cliente'
            }),
            'cliente_rut': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900',
                'placeholder': 'RUT del cliente (opcional)'
            }),
            'cliente_telefono': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900',
                'placeholder': 'Teléfono del cliente'
            }),
            'region': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900',
                'placeholder': 'Región'
            }),
            'ciudad': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900',
                'placeholder': 'Ciudad'
            }),
        }
        labels = {
            'cliente_nombre': 'Nombre del Cliente',
            'cliente_apellido': 'Apellido del Cliente',
            'cliente_rut': 'RUT del Cliente (opcional)',
            'cliente_telefono': 'Teléfono',
            'region': 'Región',
            'ciudad': 'Ciudad',
        }

class DetalleCataliticoForm(forms.ModelForm):
    # Campo personalizado para el código del catalítico
    codigo_catalitico = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'style': 'color: #111 !important; background-color: #fff !important;',
            'placeholder': 'Ingresa el código (presiona Enter para buscar precio)'
        }),
        label='Código del Catalítico'
    )
    
    class Meta:
        model = DetalleCatalitico
        fields = ['cantidad', 'precio_unitario']  # Excluir catalitico ya que usamos codigo_catalitico
        widgets = {
            'cantidad': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'style': 'color: #111 !important; background-color: #fff !important;',
                'min': '1'
            }),
            'precio_unitario': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'style': 'color: #111 !important; background-color: #fff !important;',
                'min': '0'
            }),
        }
        labels = {
            'cantidad': 'Cantidad',
            'precio_unitario': 'Precio Unitario',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.catalitico:
            self.fields['codigo_catalitico'].initial = self.instance.catalitico.codigo
    
    def save(self, commit=True):
        # Buscar o crear el catalítico basado en el código
        codigo = self.cleaned_data.get('codigo_catalitico')
        if codigo:
            try:
                catalitico = Catalitico.objects.get(codigo=codigo)
                self.instance.catalitico = catalitico
            except Catalitico.DoesNotExist:
                # Si no existe, lo creamos con valores predeterminados
                catalitico = Catalitico.objects.create(
                    codigo=codigo,
                    descripcion=f"Catalítico {codigo}",
                    valor=0,
                    valor_actual=0
                )
                self.instance.catalitico = catalitico
        
        if commit:
            self.instance.save()
        return self.instance

# Formset para manejar múltiples detalles
DetalleCataliticoFormSet = forms.inlineformset_factory(
    CompraCatalitico, 
    DetalleCatalitico, 
    form=DetalleCataliticoForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)
