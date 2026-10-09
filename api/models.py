from ckeditor.fields import RichTextField
from django.contrib.gis.db import models


class Cuerpo(models.Model):
    codigo = models.PositiveSmallIntegerField(primary_key=True)
    nombre = models.CharField(max_length=255)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['codigo']
        verbose_name = 'Cuerpo'
        verbose_name_plural = 'Cuerpos'

    def __str__(self):
        return f"{self.codigo}"


class Especialidad(models.Model):
    codigo = models.PositiveSmallIntegerField()
    nombre = models.CharField(max_length=255)
    cuerpo = models.ForeignKey(
        Cuerpo,
        on_delete=models.PROTECT,
        blank=False
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['codigo']
        verbose_name = 'Especialidad'
        verbose_name_plural = 'Especialidades'

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Provincia(models.Model):
    codigo = models.PositiveSmallIntegerField(primary_key=True)
    nombre = models.CharField(max_length=255)
    nombre_codigo = models.CharField(max_length=2, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre}"

    class Meta:
        ordering = ['codigo']
        verbose_name = 'Provincia'
        verbose_name_plural = 'Provincias'


class Categoria(models.Model):
    nombre = models.CharField(max_length=225)
    codigo = models.CharField(max_length=255)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre}"

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'


class Noticia(models.Model):
    titulo = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, null=True, blank=True)
    resumen = models.TextField(blank=True)
    cuerpo = RichTextField()
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        blank=False
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    mostrar_imagen = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Noticia'
        verbose_name_plural = 'Noticias'
        ordering = ['id']

    def __str__(self):
        return f"{self.titulo}"


class Version(models.Model):
    version = models.CharField(max_length=255)
    codigo = models.IntegerField()
    mejoras = models.TextField()
    plataforma = models.CharField(max_length=255, choices=[('ANDROID', 'Android'), ('IOS', 'iOS')], blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.version} - ({self.codigo})"

    class Meta:
        verbose_name = 'Versión'
        verbose_name_plural = 'Versiones'


class Centro(models.Model):
    codigo = models.IntegerField()
    nombre = models.CharField(max_length=255, null=True, blank=True)
    localidad = models.CharField(max_length=255, null=True, blank=True)
    provincia = models.ForeignKey(
        Provincia,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    telefono = models.CharField(max_length=20, null=True, blank=True)
    movil = models.CharField(max_length=20, null=True, blank=True)
    # coordinates = models.PointField(srid=4326, null=True, blank=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Centro'
        verbose_name_plural = 'Centros'

    def __str__(self):
        return f"{self.nombre}"


class Programa(models.Model):
    codigo = models.IntegerField()
    nombre = models.CharField(max_length=255, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Programa'
        verbose_name_plural = 'Programas'

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Funcion(models.Model):
    codigo = models.IntegerField()
    nombre = models.CharField(max_length=255, null=True, blank=True)
    especialidad = models.ForeignKey(
        Especialidad,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Función'
        verbose_name_plural = 'Funciones'

    def __str__(self):
        return f"{self.nombre}"


class Plaza(models.Model):
    funcion = models.ForeignKey(
        Funcion,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    centro = models.ForeignKey(
        Centro,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    puesto = models.CharField(max_length=255, null=True, blank=True)
    jornada = models.CharField(max_length=255, null=True, blank=True)
    competencia = models.CharField(max_length=255, null=True, blank=True)
    programa = models.ForeignKey(
        Programa,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    fecha = models.DateField(null=True)
    fecha_creacion = models.DateTimeField(null=True, auto_now_add=True)
    fecha_modificacion = models.DateTimeField(null=True, auto_now=True)
    error = models.BooleanField(default=False)
    id_plaza = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'Plaza'
        verbose_name_plural = 'Plazas'


class Registro(models.Model):
    orden = models.PositiveSmallIntegerField(null=True)
    dni = models.CharField(max_length=255)
    nombre = models.CharField(max_length=255, null=True, blank=True)
    apellidos = models.CharField(max_length=255, null=True, blank=True)
    tipo_bolsa = models.CharField(max_length=255, blank=True)
    orden_bolsa = models.CharField(max_length=255, blank=True)
    provincias = models.CharField(max_length=255, blank=True)
    especialidad = models.ForeignKey(
        Especialidad,
        on_delete=models.PROTECT,
        blank=False
    )
    ingles = models.BooleanField()
    frances = models.BooleanField()
    aleman = models.BooleanField()
    italiano = models.BooleanField()
    fecha = models.DateField(db_index=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    error = models.BooleanField(default=False)
    adjudicado = models.BooleanField(default=False)
    plaza = models.ForeignKey(
        Plaza,
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Registro'
        verbose_name_plural = 'Registros'


class Acceso(models.Model):
    codigo = models.IntegerField()
    nombre = models.CharField(max_length=255, null=True, blank=True)
    especialidad = models.ForeignKey(
        Especialidad,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tipo de Acceso'
        verbose_name_plural = 'Tipos de Acceso'

    def __str__(self):
        return f"{self.nombre}"


class RegistroBolsaGeneral(models.Model):
    orden = models.PositiveSmallIntegerField()
    dni = models.CharField(max_length=255)
    nombre = models.CharField(max_length=255, blank=True)
    apellidos = models.CharField(max_length=255, blank=True)
    acceso = models.ForeignKey(
        Acceso,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    orden_bolsa = models.CharField(max_length=255, blank=True)
    puntos = models.DecimalField(max_digits=6, decimal_places=4)
    puntos_ado1_experiencia = models.DecimalField(max_digits=5, decimal_places=4)
    puntos_ado2_examen = models.DecimalField(max_digits=5, decimal_places=4)
    puntos_ado3_formacion = models.DecimalField(max_digits=5, decimal_places=4)
    tipo_bolsa = models.CharField(max_length=255, blank=True)
    ingles = models.BooleanField()
    frances = models.BooleanField()
    aleman = models.BooleanField()
    italiano = models.BooleanField()
    lengua_signos = models.BooleanField()
    especialidades = models.ForeignKey(
        Especialidad,
        on_delete=models.PROTECT,
        blank=False
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    disponible = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Registro Bolsa General'
        verbose_name_plural = 'Registros Bolsa General'