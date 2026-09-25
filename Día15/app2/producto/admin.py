from django.contrib import admin
from .models import Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo_barra', 'descripcion', 'precio_costo', 'precio_venta', 'iva', 'stock', 'unidad_medida')
    list_filter = ('iva', 'unidad_medida')
    search_fields = ('codigo_barra', 'descripcion')
    ordering = ('descripcion',)
