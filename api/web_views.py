from django.http import HttpResponseBadRequest
from django.shortcuts import render
from api.models import Noticia, Plaza
from django.conf import settings


def index(request):
    version = request.GET.get('version', '')
    cuerpo = request.GET.get('cuerpo', '')
    especialidad = request.GET.get('especialidad', '')
    fecha = request.GET.get('fecha', '')

    if version == '2024/25':
        return render(request, "index.html", {'api_base_url': settings.API_BASE_URL, 'cuerpo': cuerpo, 'especialidad': especialidad, 'fecha': fecha})
    else:
        return HttpResponseBadRequest("Versión de la APP Bolsa Educación Interinos CLM no válida.")


def detalle_interino(request):
    nombre = request.GET.get('nombre', '')
    apellidos = request.GET.get('apellidos', '')
    dni = request.GET.get('dni', '')
    cuerpo = request.GET.get('cuerpo', '')
    especialidad = request.GET.get('especialidad', '')
    fecha = request.GET.get('fecha', '')

    return render(request, "detalle-interino.html", {'api_base_url': settings.API_BASE_URL, 'nombre': nombre, 'apellidos': apellidos, 'dni': dni, 'cuerpo': cuerpo, 'especialidad': especialidad, 'fecha': fecha})


def politica_privacidad(request):
    return render(request, "politica-privacidad.html", {})


def noticias(request, categoria=None):
    noticias_list = Noticia.objects.all().order_by("-fecha_creacion")
    return render(request, "noticias.html", {'noticias': noticias_list})


def plazas(request):
    return render(request, "plazas.html", {'api_base_url': settings.API_BASE_URL})


def noticias_detalle(request, categoria=None, slug=None):
    noticia = Noticia.objects.all().filter(slug=slug)[0]

    return render(request, "noticias-detalle.html", {"noticia": noticia})


def no_disponibles(request, categoria=None, slug=None):
    return render(request, "no-disponibles.html", {'api_base_url': settings.API_BASE_URL})
