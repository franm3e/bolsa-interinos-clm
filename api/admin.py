from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin

from api.models import *


class CuerpoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'fecha_creacion', 'fecha_modificacion']
    list_display_links = ('codigo', 'nombre')
    search_fields = ['nombre', 'codigo']
    ordering = ['codigo']


class EspecialidadAdmin(admin.ModelAdmin):
    list_display = ['id', 'codigo', 'cuerpo', 'nombre', 'fecha_creacion', 'fecha_modificacion']
    list_display_links = ['id', 'nombre']
    search_fields = ['nombre', 'codigo']
    ordering = ['cuerpo', 'codigo']
    list_filter = ["cuerpo"]


class RegistroAdmin(admin.ModelAdmin):
    list_display = ['id', 'fecha', 'especialidad', 'orden', 'nombre', 'apellidos', 'provincias', 'fecha_modificacion', 'fecha_creacion']
    list_display_links = ['id', 'nombre', 'apellidos']
    ordering = ['-fecha', 'especialidad__cuerpo__codigo', 'especialidad_id', 'orden']
    list_filter = ['especialidad__cuerpo', 'error']

    def save_model(self, request, obj, form, change):
        old_obj = None
        if obj.dni and obj.nombre and obj.apellidos:
            old_obj = Registro.objects.get(id=obj.id)

        super().save_model(request, obj, form, change)

        if change and old_obj and obj.adjudicado != old_obj.adjudicado and obj.adjudicado:
            afectados = Registro.objects.filter(orden__gte=obj.orden).exclude(pk=obj.pk)

            for afectado in afectados:
                afectado.orden -= 1
                afectado.save(update_fields=["orden"])

            obj.orden = None
            obj.save(update_fields=["orden"])


class ProvinciaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'fecha_creacion', 'fecha_modificacion')
    list_display_links = ['codigo', 'nombre']
    ordering = ['nombre']


class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_creacion', 'fecha_modificacion')
    list_display_links = ['nombre']
    ordering = ['nombre']


class NoticiaAdmin(admin.ModelAdmin):
    list_display = ('id', 'categoria', 'titulo', 'fecha_creacion', 'fecha_modificacion')
    list_display_links = ['titulo']
    prepopulated_fields = {"slug": ["titulo"]}
    ordering = ['-fecha_creacion']


class VersionAdmin(admin.ModelAdmin):
    list_display = ('id', 'version', 'codigo', 'mejoras', 'plataforma', 'fecha_creacion', 'fecha_modificacion')
    list_display_links = ['version', 'codigo']
    ordering = ['plataforma', 'version']
    list_filter = ["plataforma"]


class PlazaAdmin(admin.ModelAdmin):
    list_display = ('id', 'funcion', 'centro', 'puesto', 'jornada', 'competencia', 'programa', 'fecha_creacion', 'fecha_modificacion', 'error')
    list_display_links = ['id']
    ordering = ['fecha_creacion', 'funcion']
    list_filter = ['error', 'funcion', 'centro', 'jornada']


class CentroAdmin(OSMGeoAdmin):
    list_display = ('codigo', 'nombre', 'localidad', 'provincia', 'fecha_creacion', 'fecha_modificacion', 'telefono', 'movil')
    list_display_links = ['codigo', 'nombre']
    ordering = ['codigo']
    list_filter = ['provincia', 'localidad']
    search_fields = ['nombre']


class FuncionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'especialidad', 'fecha_creacion', 'fecha_modificacion')
    list_display_links = ['codigo', 'nombre']
    ordering = ['especialidad', 'codigo']
    list_filter = ['especialidad']
    search_fields = ['nombre']


class ProgramaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'fecha_creacion', 'fecha_modificacion')
    list_display_links = ['codigo', 'nombre']
    ordering = ['codigo']
    search_fields = ['nombre']


admin.site.register(Cuerpo, CuerpoAdmin)
admin.site.register(Especialidad, EspecialidadAdmin)
admin.site.register(Registro, RegistroAdmin)
admin.site.register(Provincia, ProvinciaAdmin)
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Noticia, NoticiaAdmin)
admin.site.register(Version, VersionAdmin)
admin.site.register(Programa, ProgramaAdmin)
admin.site.register(Funcion, FuncionAdmin)
admin.site.register(Centro, CentroAdmin)
admin.site.register(Plaza, PlazaAdmin)
