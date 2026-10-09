from rest_framework import serializers

from api.models import Cuerpo, Especialidad, Registro, Provincia, Noticia, Categoria, Version, Plaza, Funcion, Programa, Centro


class CuerpoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuerpo
        fields = ['codigo', 'nombre']


class EspecialidadSerializer(serializers.ModelSerializer):
    cuerpo = CuerpoSerializer(read_only=True)

    class Meta:
        model = Especialidad
        fields = ['codigo', 'nombre', 'cuerpo', 'id']


class ProvinciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provincia
        fields = ['codigo', 'nombre', 'nombre_codigo']


class UltimaActualizacionSerializer(serializers.Serializer):
    fecha = serializers.CharField(max_length=200)


class RegistroPersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registro
        fields = ['nombre', 'apellidos', 'dni']


class GraficaResumenSerializer(serializers.Serializer):
    type = serializers.JSONField()
    data = serializers.JSONField()
    options = serializers.JSONField()


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['nombre', 'codigo']


class NoticiaSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)

    class Meta:
        model = Noticia
        fields = '__all__'


class UltimaVersionAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = Version
        fields = '__all__'


class FuncionSerializer(serializers.ModelSerializer):
    especialidad = EspecialidadSerializer()

    class Meta:
        model = Funcion
        fields = ['codigo', 'nombre', 'especialidad']


class CentroSerializer(serializers.ModelSerializer):
    provincia = ProvinciaSerializer(read_only=True)

    class Meta:
        model = Centro
        fields = ['nombre', 'localidad', 'provincia', 'telefono', 'movil']


class ProgramaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Programa
        fields = ['codigo', 'nombre']


class FechasPlazasSerializer(serializers.Serializer):
    fecha = serializers.DateField()
    total_plazas = serializers.IntegerField()

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['fecha'] = instance['fecha'].strftime('%d/%m/%Y')

        return rep


class PlazaSerializer(serializers.ModelSerializer):
    funcion = FuncionSerializer()
    centro = CentroSerializer()

    class Meta:
        model = Plaza
        fields = ['puesto', 'jornada', 'fecha_inicio', 'fecha_fin', 'funcion', 'centro']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['fecha_inicio'] = instance.fecha_inicio.strftime('%d/%m/%Y') if instance.fecha_inicio else None
        rep['fecha_fin'] = instance.fecha_fin.strftime('%d/%m/%Y') if instance.fecha_fin else None
        return rep


class PlazasSerializer(serializers.Serializer):
    plazas = PlazaSerializer(many=True)
    total_ceses = serializers.IntegerField()


class OrdenEspecialidadProvinciaSerializer(serializers.Serializer):
    posicion_bolsa_general = serializers.IntegerField()
    total_bolsa_general = serializers.IntegerField()
    posicion_general_especialidad = serializers.IntegerField()
    total_general_especialidad = serializers.IntegerField()
    posicion_provincias = serializers.JSONField()
    plaza = PlazaSerializer(read_only=True)


class FechasRegistrosSerializer(serializers.Serializer):
    fecha = serializers.DateField()
    adjudicado = serializers.BooleanField()

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['fecha'] = instance['fecha'].strftime('%d/%m/%Y')

        return rep


class RegistroSerializer(serializers.ModelSerializer):
    plaza = PlazaSerializer(read_only=True)
    especialidad = EspecialidadSerializer(read_only=True)

    class Meta:
        model = Registro
        fields = '__all__'


class FuncionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Funcion
        fields = ['codigo', 'nombre']


class ProvinciasPlazasSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=200)
    codigo = serializers.IntegerField()
    total_plazas = serializers.IntegerField()


class DetallesInterinoSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=200)
    codigo = serializers.IntegerField()
    total_plazas = serializers.IntegerField()