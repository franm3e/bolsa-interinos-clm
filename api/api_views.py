from datetime import datetime, timedelta

import django_filters
from django.contrib.postgres.lookups import Unaccent
from django.db.models import Count, Sum, IntegerField, Max, Avg, Q, Value
from django.db.models.functions import Cast, Concat
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Cuerpo, Provincia, Registro, Especialidad, Noticia, Version, Plaza
from api.serializers import CuerpoSerializer, ProvinciaSerializer, NoticiaSerializer, EspecialidadSerializer, \
    RegistroSerializer, RegistroPersonaSerializer, UltimaActualizacionSerializer, OrdenEspecialidadProvinciaSerializer, \
    GraficaResumenSerializer, UltimaVersionAppSerializer, PlazaSerializer, FechasPlazasSerializer, \
    FechasRegistrosSerializer, \
    FuncionSerializer, ProvinciasPlazasSerializer, DetallesInterinoSerializer, PlazasSerializer
from rest_framework import filters
from django.db.models import F


class CuerpoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Cuerpo.objects.none()
    serializer_class = CuerpoSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['codigo']

    def get_queryset(self):
        fecha = self.request.query_params.get('fecha')

        if fecha:
            especialidades = Registro.objects.filter(fecha=fecha).values_list('especialidad', flat=True).distinct()
            return Cuerpo.objects.filter(especialidad__in=especialidades).distinct()

        return Cuerpo.objects.all()


class ProvinciaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Provincia.objects.all()
    serializer_class = ProvinciaSerializer


class RegistroViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RegistroSerializer

    def get_queryset(self):
        nombre = self.request.query_params.get('nombre')
        apellidos = self.request.query_params.get('apellidos')
        dni = self.request.query_params.get('dni')

        if nombre and apellidos and dni:
            return Registro.objects.filter(nombre=nombre, apellidos=apellidos, dni=dni).order_by('-fecha', 'especialidad')[:1]

        return Registro.objects.all()


class EspecialidadViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EspecialidadSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['cuerpo', 'id']

    def get_queryset(self):
        fecha = self.request.query_params.get('fecha')
        cuerpo = self.request.query_params.get('cuerpo')

        if fecha:
            if cuerpo:
                especialidades = Registro.objects.filter(fecha=fecha, especialidad__cuerpo__codigo=cuerpo).values_list('especialidad', flat=True).distinct()
                return Especialidad.objects.filter(id__in=especialidades).distinct()

            return Especialidad.objects.filter(id__in=Registro.objects.filter(fecha=fecha).values_list('especialidad', flat=True).distinct()).distinct()
        elif cuerpo:
            if cuerpo:
                return Registro.objects.filter(especialidad__cuerpo__codigo=cuerpo).values_list('especialidad', flat=True).distinct()

        return Especialidad.objects.all()


class RegistroPersonaViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RegistroPersonaSerializer

    def get_queryset(self):
        params = self.request.query_params
        search = params.get('search')

        if not all([search]):
            return Registro.objects.none()

        return Registro.objects.annotate(
            nombre_unaccent=Unaccent("nombre"),
            apellidos_unaccent=Unaccent("apellidos"),
            nombre_completo=Concat("nombre", Value(" "), "apellidos"),
            nombre_completo_unaccent=Unaccent(Concat("nombre", Value(" "), "apellidos")),
        ).filter(Q(nombre_unaccent__icontains=search) | Q(apellidos_unaccent__icontains=search) | Q(nombre_completo_unaccent__icontains=search)).distinct("nombre", "apellidos", "dni")


class RegistroInterinosViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Registro.objects.select_related('especialidad', 'especialidad__cuerpo', 'plaza', 'plaza__centro', 'plaza__centro__provincia', 'plaza__funcion', 'plaza__funcion__especialidad', 'plaza__funcion__especialidad__cuerpo').order_by(F('orden').asc(nulls_first=True))
    serializer_class = RegistroSerializer
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend
    ]
    filterset_fields = {
        'especialidad': ['exact'],
        'fecha': ['exact'],
        'dni': ['exact'],
    }
    search_fields = ['nombre', 'apellidos', 'provincias']


class UltimaActualizacionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Registro.objects.values("fecha").annotate(dcount=Count("fecha")).order_by("-fecha")[:2]
    serializer_class = UltimaActualizacionSerializer


class OrdenEspecialidadProvinciaViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrdenEspecialidadProvinciaSerializer

    def get_queryset(self):
        response = []
        response_aux = []

        params = self.request.query_params
        nombre = params.get('nombre')
        apellidos = params.get('apellidos')
        dni = params.get('dni')
        especialidad = params.get('especialidad')
        fecha = params.get('fecha')

        if not all([nombre, apellidos, dni, especialidad, fecha]):
            return []

        registro_model = Registro.objects
        registro_object = registro_model.filter(fecha=fecha)
        total_bolsa_general = registro_object.filter(fecha=fecha, orden_bolsa__regex=r'^\d+$').annotate(orden_bolsa_int=Cast('orden_bolsa', IntegerField())).aggregate(Max('orden_bolsa_int'))['orden_bolsa_int__max']

        registro_actual = registro_object.filter(
            dni=dni,
            nombre=nombre,
            apellidos=apellidos,
            especialidad=especialidad
        ).first()

        if not registro_actual:
            return []

        posicion_general_especialidad = total_general_especialidad = None
        if not registro_actual.adjudicado:
            object_general_especialidad = registro_model.filter(fecha=registro_actual.fecha, especialidad=especialidad)
            total_general_especialidad = object_general_especialidad.count()
            posicion_general_especialidad = object_general_especialidad.filter(orden__lte=registro_actual.orden).count()

            provincias_codigos = [p.strip() for p in registro_actual.provincias.split(",")]
            for codigo in provincias_codigos:
                provincia = Provincia.objects.filter(codigo=codigo).values("nombre_codigo", "nombre", "codigo").first()
                if not provincia:
                    continue

                posicion_object = registro_model.filter(
                    fecha=registro_actual.fecha,
                    especialidad=especialidad,
                    provincias__contains=codigo,
                    orden__lte=registro_actual.orden
                )
                posicion = posicion_object.count()
                posicion_solo_provincia = posicion_object.filter(provincias=codigo).exclude(id=registro_actual.id).count()

                qs_fecha_estimada = registro_model.filter(
                    especialidad_id=especialidad,
                    adjudicado=True,
                    plaza__funcion__especialidad_id=F('especialidad_id'),
                    provincias__contains=codigo
                ).values('fecha').annotate(count=Count('id')).order_by('-fecha')
                qs_aggregate_media = qs_fecha_estimada.aggregate(media=Avg('count'))['media']

                fecha_estimada_provincia = None
                if qs_aggregate_media is not None and posicion is not None:
                    fecha_estimada_provincia = self.calcular_fecha_estimada_llamamiento(posicion, qs_aggregate_media, fecha)

                posicion_idioma_provincia = {
                    'ingles': {
                        'posicion': posicion_object.filter(ingles=True).exclude(id=registro_actual.id).count(),
                        'habilitado': registro_actual.ingles
                    },
                    'frances': {
                        'posicion': posicion_object.filter(frances=True).exclude(id=registro_actual.id).count(),
                        'habilitado': registro_actual.frances
                    },
                    'italiano': {
                        'posicion': posicion_object.filter(italiano=True).exclude(id=registro_actual.id).count(),
                        'habilitado': registro_actual.italiano
                    },
                    'aleman': {
                        'posicion': posicion_object.filter(aleman=True).exclude(id=registro_actual.id).count(),
                        'habilitado': registro_actual.aleman
                    }
                }

                registro_anterior = registro_model.filter(
                    dni=dni,
                    nombre=nombre,
                    apellidos=apellidos,
                    especialidad=especialidad,
                    adjudicado=False
                ).filter(fecha__lt=fecha).order_by('-fecha').first()

                alteracion = None
                if registro_anterior:
                    ultima_posicion = registro_model.filter(
                        fecha=registro_anterior.fecha,
                        especialidad=especialidad,
                        provincias__contains=codigo,
                        orden__lte=registro_anterior.orden
                    ).count()
                    if ultima_posicion:
                        alteracion = posicion - ultima_posicion

                response_aux.append({
                    "provincia": provincia,
                    "posicion": posicion,
                    "posicion_solo_provincia": posicion_solo_provincia,
                    "posicion_idioma_provincia": posicion_idioma_provincia,
                    "alteracion": alteracion,
                    "fecha_estimada": fecha_estimada_provincia and fecha_estimada_provincia.strftime("%d/%m/%Y")
                })

        response.append(
            {
                'posicion_bolsa_general': registro_actual.orden_bolsa,
                'total_bolsa_general': total_bolsa_general,
                'posicion_general_especialidad': posicion_general_especialidad,
                'total_general_especialidad': total_general_especialidad,
                'posicion_provincias': response_aux,
                'plaza': registro_actual.plaza
            }
        )

        return response

    def calcular_fecha_estimada_llamamiento(self, posicion, media, fecha):
        meses_validos = {9, 10, 11, 12, 1, 2, 3, 4, 5}
        fecha_base = datetime.strptime(fecha, "%Y-%m-%d").date()
        semanas_necesarias = posicion/media

        semanas_contadas = 0
        fecha_actual = fecha_base
        while semanas_contadas < semanas_necesarias:
            fecha_actual += timedelta(days=7)
            if fecha_actual.month in meses_validos:
                semanas_contadas += 1

        return fecha_actual


class EspecialidadesRegistroViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = []
    serializer_class = EspecialidadSerializer

    def get_queryset(self):
        nombre = self.request.query_params.get('nombre')
        dni = self.request.query_params.get('dni')
        apellidos = self.request.query_params.get('apellidos')
        fecha = self.request.query_params.get('fecha')

        if nombre and apellidos and dni and fecha:
            especialidades_raw = Registro.objects.filter(
                dni=dni,
                nombre=nombre,
                apellidos=apellidos,
                fecha=fecha).values('especialidad__id', 'especialidad__codigo', 'especialidad__nombre').distinct()

            return [
                {'id': e['especialidad__id'], 'codigo': e['especialidad__codigo'], 'nombre': e['especialidad__nombre']}
                for e in especialidades_raw
            ]


class GraficaResumenViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = []
    serializer_class = GraficaResumenSerializer

    def get_queryset(self):
        response = []
        nombre = self.request.query_params.get('nombre')
        dni = self.request.query_params.get('dni')
        apellidos = self.request.query_params.get('apellidos')
        especialidad = self.request.query_params.get('especialidad')

        if nombre and apellidos and dni and especialidad:
            registro = Registro.objects.filter(dni=dni, nombre=nombre, apellidos=apellidos, especialidad__codigo=especialidad).order_by("fecha")

            json = {
                'type': 'line',
                'data': {
                    'datasets': []
                },
                'options': {
                    'interaction': {
                        'intersect': False,
                        'mode': 'index',
                    },
                    'scales': {
                        'x': {
                            'display': True,
                            'type': 'time',
                            'parser': 'YYYY-MM-DD',
                            'ticks': {
                                'source': 'data'
                            },
                            'time': {
                                'displayFormats': {
                                    'day': 'DD/MM/YYYY'
                                },
                                'unit': 'day'
                            }
                        },
                        'y': {
                            'ticks': {
                                'precision': 0
                            },
                        }
                    }
                }
            }

            datasets_data = {
                2: [],
                13: [],
                16: [],
                19: [],
                45: []
            }

            fechas_list = registro.values_list("fecha", "provincias", "orden").order_by("fecha")

            for fecha in fechas_list:
                provincias = fecha[1].split(",")

                for provincia in provincias:
                    datasets_data[int(provincia)].append({
                        'x': fecha[0],
                        'y': len(list(Registro.objects.filter(fecha=fecha[0], especialidad=especialidad, provincias__contains=provincia, orden__lte=fecha[2])))
                    })

            for provincia in Provincia.objects.all():
                if provincia.codigo in datasets_data.keys() and len(datasets_data[provincia.codigo]) > 0:
                    json['data']['datasets'].append(
                        {
                            'label': provincia.nombre_codigo,
                            'data': datasets_data[provincia.codigo],
                            'borderWidth': 1,
                            'pointRadius': 5,
                            'pointHoverRadius': 6
                        }
                    )

            response.append(json)

        return response


class NoticiaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Noticia.objects.order_by("-fecha_creacion")
    serializer_class = NoticiaSerializer


class UltimaVersionAppViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        response = []
        plataforma = self.request.query_params.get('plataforma')

        if plataforma:
            response = Version.objects.filter(plataforma__iexact=plataforma).order_by("-codigo")[:1]

        return response

    serializer_class = UltimaVersionAppSerializer


class PlazasViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PlazaSerializer

    def get_queryset(self):
        fecha = self.request.query_params.get('fecha')
        funciones = self.request.query_params.get('funciones')
        provincias = self.request.query_params.get('provincias')

        if not fecha:
            return Plaza.objects.none()

        plazas = Plaza.objects.select_related(
            'funcion',
            'funcion__especialidad',
            'funcion__especialidad__cuerpo',
            'centro',
            'centro__provincia'
        ).filter(fecha=fecha)

        if funciones:
            funciones_array = funciones.split(',')
            plazas = plazas.filter(funcion__codigo__in=funciones_array)

        if provincias:
            provincias_array = provincias.split(',')
            plazas = plazas.filter(centro__provincia__codigo__in=provincias_array)

        return plazas.order_by('centro__provincia__nombre', 'centro__localidad')

    def list(self, request, *args, **kwargs):
        fecha_param = request.query_params.get('fecha')
        if not fecha_param:
            return Response({"plazas": [], "total_ceses": 0})

        fecha_param = datetime.strptime(fecha_param, "%Y-%m-%d").date()

        plazas_queryset = self.get_queryset()
        plazas_serializadas = PlazaSerializer(plazas_queryset, many=True).data

        fecha_anterior = Plaza.objects.filter(fecha__lt=fecha_param).aggregate(
            max_fecha=Max('fecha')
        )['max_fecha']

        if fecha_anterior:
            total_ceses = Plaza.objects.filter(
                fecha_fin__gte=fecha_anterior,
                fecha_fin__lt=fecha_param,
                funcion__especialidad_id=F('registro__especialidad_id')
            ).distinct().count()
        else:
            total_ceses = Plaza.objects.filter(fecha_fin__lte=fecha_param).count()

        response = {
            "plazas": plazas_serializadas,
            "total_ceses": total_ceses
        }

        return Response(response)


class FechasPlazasViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Plaza.objects.all().values('fecha').annotate(total_plazas=Count('fecha_creacion')).order_by('-fecha')
    serializer_class = FechasPlazasSerializer


class FechasRegistrosViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FechasRegistrosSerializer

    def get_queryset(self):
        dni = self.request.query_params.get('dni')
        nombre = self.request.query_params.get('nombre')
        apellidos = self.request.query_params.get('apellidos')

        if nombre and apellidos and dni:
            return Registro.objects.filter(
                dni=dni,
                nombre=nombre,
                apellidos=apellidos
            ).values('fecha', 'adjudicado').distinct().order_by('-fecha')
        else:
            fechas = Registro.objects.values('fecha').distinct().order_by('-fecha')
            for f in fechas:
                f['adjudicado'] = None
            return fechas


class FuncionesPlazasViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FuncionSerializer

    def get_queryset(self):
        response = []
        fecha = self.request.query_params.get('fecha')
        provincias = self.request.query_params.get('provincias')

        response = Plaza.objects.filter(fecha=fecha)
        if provincias:
            provincias_array = provincias.split(',')
            response = response.filter(centro__provincia__codigo__in=provincias_array)

        response = response.order_by('funcion__nombre').distinct('funcion__nombre').values(nombre=F('funcion__nombre'), codigo=F('funcion__codigo'))

        return response


class ProvinciasPlazasViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProvinciasPlazasSerializer

    def get_queryset(self):
        response = []
        fecha = self.request.query_params.get('fecha')

        if fecha:
            date_parts = fecha.split("-")
            response = (
                Plaza.objects.all()
                .filter(fecha=fecha)
                .exclude(centro__provincia__isnull=True)
                .values(nombre=F('centro__provincia__nombre'), codigo=F('centro__provincia__codigo'))
                .annotate(total_plazas=Count('nombre'))
                .order_by('centro__provincia__nombre')
            )

        return response


class DetallesInterinoViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        response = []
        fecha = self.request.query_params.get('fecha')

        if fecha:
            date_parts = fecha.split("-")
            response = (Plaza.objects.all()
                        .filter(fecha_creacion__year=date_parts[0], fecha_creacion__month=date_parts[1], fecha_creacion__day=date_parts[2])
                        .exclude(centro__provincia__isnull=True)
                        .values(nombre=F('centro__provincia__nombre'), codigo=F('centro__provincia__codigo'))
                        .annotate(total_plazas=Count('nombre'))
                        .order_by('centro__provincia__nombre')
                        )

        return response

    serializer_class = DetallesInterinoSerializer
