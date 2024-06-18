from django.db import models

# Create your models here.
class TipoTurno(models.Model):
    dias = models.CharField(max_length=50)
    hora_entrada = models.CharField(max_length=10)
    hora_salida = models.CharField(max_length=10)
    formato = models.CharField(max_length=20)

    class Meta:
        db_table = "TipoTurno"
        verbose_name = "Tipo de turno"
        verbose_name_plural = "Tipos de turnos"

    def __str__(self):
        return f"{self.dias} ({self.hora_entrada} - {self.hora_salida})"

class Profesor(models.Model):
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    estudios = models.CharField(max_length=100)
    experiencia = models.IntegerField()

    class Meta:
        db_table = "Profesor"
        verbose_name = "Profesor"
        verbose_name_plural = "Profesores"

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

class Horario(models.Model):
    tipo_turno = models.ForeignKey(TipoTurno, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    
    class Meta:
        db_table = "Horario"
        verbose_name = "Horario"
        verbose_name_plural = "Horarios"
        
    def __str__(self):
        return self.nombre

class Grupo(models.Model):
    nombre = models.CharField(max_length=100)
    nivel = models.CharField(max_length=100)
    cupo_maximo = models.IntegerField()
    horario = models.ForeignKey(Horario, on_delete=models.CASCADE)
    profesor = models.ForeignKey(Profesor, on_delete=models.CASCADE, verbose_name= "Profesor")
    
    class Meta:
        db_table = "Grupo"
        verbose_name = "Grupo"
        verbose_name_plural = "Grupos"
        
    def __str__(self):
        return f"{self.nombre} - Nivel {self.nivel}"

class Alumno(models.Model):
    email = models.EmailField()
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)
    telefono = models.CharField(max_length=15)
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE)
    
    class Meta:
        db_table = "Alumno"
        verbose_name = "Alumno"
        verbose_name_plural = "Alumnos"
        
    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

class TipoPago(models.Model): 
    nombre = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        db_table = "TipoPago"
        verbose_name = "Tipo de pago"
        verbose_name_plural = "Tipo de pagos"
        
class Pago(models.Model):
    fecha = models.DateField()
    monto = models.IntegerField()
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    tipo_pago = models.ForeignKey(TipoPago, on_delete=models.CASCADE)
    solvencia_mes = models.BooleanField()
    
    class Meta:
        db_table = "Pago"
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"

    def __str__(self):
        return f"Pago de {self.monto} de {self.alumno} el {self.fecha}"
