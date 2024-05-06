from django.contrib import admin
from .models import TipoPago, TipoTurno, Alumno, Profesor, Horario, Grupo, Pago

# Register your models here.

admin.site.site_header = "Howard Bilingual School"
admin.site.site_title = "Howard"
admin.site.index_title = "Home"

class GrupoInLine(admin.TabularInline):
    model = Grupo
    extra = 1
    
class AlumnoInLine(admin.TabularInline):
    model = Alumno
    extra = 1
    
class PagoInLine(admin.TabularInline):
    model = Pago
    extra = 1    

class HorarioInLine(admin.TabularInline):
    model = Horario
    extra = 1    
     
@admin.register(TipoPago)
class TipoPagoAdmin(admin.ModelAdmin): 
    fields = ["nombre"]
    list_display = ["nombre"]
    inlines = [PagoInLine]
        
@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    fields = ["nombres", "apellidos", "estudios", "experiencia"]
    list_display = ["nombres", "apellidos", "estudios", "experiencia"]
    inlines = [GrupoInLine]
    
@admin.register(TipoTurno)
class TipoTurnoAdmin(admin.ModelAdmin):
    fields = ["dias", "hora_entrada" , "hora_salida", "formato"]
    list_display = ["dias", "hora_entrada" , "hora_salida", "formato"]
    inlines = [HorarioInLine]
@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    fields = ["tipo_turno", "nombre"]
    list_display = ["tipo_turno", "nombre"]
    inlines = [GrupoInLine]
    
@admin.register(Grupo)
class GrupoAdmin(admin.ModelAdmin):
    fields = ["nombre", "nivel", "cupo_maximo", "horario","profesor"]
    list_display = ["nombre", "nivel", "cupo_maximo", "horario","profesor"]  
    inlines = [AlumnoInLine]
      
@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    fields = ["email", "nombres", "apellidos", "activo", "telefono","grupo"]
    list_display = ["email", "nombres", "apellidos", "activo", "telefono","grupo"]
    inlines = [PagoInLine]
@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    fields = ["fecha", "monto", "alumno", "tipo_pago", "solvencia_mes"]  
    list_display = ["fecha", "monto", "alumno", "tipo_pago", "solvencia_mes"]  
