from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView, RedirectView
from rest_framework.routers import DefaultRouter
from api import api_views, web_views

router = DefaultRouter()
router.register(r'cuerpos', api_views.CuerpoViewSet, basename="cuerpos")
router.register(r'especialidades', api_views.EspecialidadViewSet, basename="especialidades")
router.register(r'registros', api_views.RegistroViewSet, basename="registros")
router.register(r'provincias', api_views.ProvinciaViewSet, basename="provincias")
router.register(r'noticias', api_views.NoticiaViewSet, basename="noticias")
router.register(r'registro-persona', api_views.RegistroPersonaViewSet, basename="registro-persona")
router.register(r'registro-interinos', api_views.RegistroInterinosViewSet, basename="registro-interinos")
router.register(r'ultima-actualizacion', api_views.UltimaActualizacionViewSet, basename="ultima-actualizacion")
router.register(r'orden-especialidad-provincia', api_views.OrdenEspecialidadProvinciaViewSet, basename="orden-especialidad-provincia")
router.register(r'especialidades-registro', api_views.EspecialidadesRegistroViewSet, basename="especialidades-registro")
router.register(r'grafica-resumen', api_views.GraficaResumenViewSet, basename="grafica-resumen")
router.register(r'ultima-version-app', api_views.UltimaVersionAppViewSet, basename="ultima-version-app")
router.register(r'plazas', api_views.PlazasViewSet, basename="plazas")
router.register(r'fechas-plazas', api_views.FechasPlazasViewSet, basename="fechas-plazas")
router.register(r'fechas-registros', api_views.FechasRegistrosViewSet, basename="fechas-registros")
router.register(r'funciones-plazas', api_views.FuncionesPlazasViewSet, basename="funciones-plazas")
router.register(r'provincias-plazas', api_views.ProvinciasPlazasViewSet, basename="provincias-plazas")
router.register(r'detalles-interino', api_views.DetallesInterinoViewSet, basename="detalles-interino")


urlpatterns = [
    path('', web_views.index, name="index"),
    path('detalle-interino', web_views.detalle_interino, name="detalle-interino"),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('plazas/', web_views.plazas, name="plazas"),
    path('no-disponibles/', web_views.no_disponibles, name="no-disponibles"),
    path('noticias/', web_views.noticias, name="noticias"),
    path('noticias/<str:categoria>/', web_views.noticias, name="noticias"),
    path('noticias/<str:categoria>/<slug:slug>/', web_views.noticias_detalle, name="noticias-detalle"),
    path('politica-privacidad', web_views.politica_privacidad, name="politica-privacidad"),
    path('app-ads.txt', TemplateView.as_view(template_name="app-ads.txt", content_type="text/plain")),
    path('ads.txt', TemplateView.as_view(template_name="ads.txt", content_type="text/plain")),
    path('favicon.ico', RedirectView.as_view(url='/staticfiles/images/favicon.ico')),
]
