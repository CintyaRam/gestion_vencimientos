from django.contrib import admin
from .models import Articulo, Departamento, Lote


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('numero_departamento',)
    search_fields = ('numero_departamento',)

@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ('numero_lote', 'articulo', 'fecha_vencimiento', 'responsable_registro', 'activo')
    list_filter = ('articulo__departamento', 'activo', 'fecha_vencimiento', 'articulo', 'responsable_registro')
    search_fields = ('numero_lote', 'articulo__nombre')


@admin.register(Articulo)
class ArticuloAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'departamento', 'activo')
    list_filter = ('departamento', 'activo')
    search_fields = ('nombre', 'descripcion')