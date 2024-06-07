from django import forms
from datetime import date

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-lg fs-6', 'placeholder': 'Nombre de Usuario'}), max_length=150)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg fs-6', 'placeholder': 'Contraseña'}), max_length=128)

class TipoTurnoForm(forms.Form):
    dias = forms.CharField(widget=forms.TextInput())
    hora_entrada = forms.CharField(widget=forms.TimeInput())
    hora_salida = forms.CharField(widget=forms.TimeInput())
    formato =  forms.CharField(widget=forms.DateTimeInput())

class HorarioForm(forms.Form):
    tipo_turno = forms.ChoiceField(widget=forms.Select(), choices=[])
    nombre =  forms.CharField(widget=forms.TextInput())

    def __init__(self, *args, **kwargs):
        if len(kwargs) > 0:
            tipos_turnos = kwargs.pop('tipos_turnos')
            super(HorarioForm, self).__init__(*args, **kwargs)
            self.fields['tipo_turno'].choices = tipos_turnos

class GrupoForm(forms.Form):
    nombre =  forms.CharField(widget=forms.TextInput())
    nivel =  forms.ChoiceField(widget=forms.Select(), choices=[(str(i), str(i)) for i in range(1, 13)])
    cupo_maximo =  forms.CharField(widget=forms.NumberInput())
    horario =  forms.ChoiceField(widget=forms.Select(), choices=[])
    profesor =  forms.ChoiceField(widget=forms.Select(), choices=[])
    
    def __init__(self, *args, **kwargs):
        if len(kwargs) > 0:
            horarios = kwargs.pop('horarios')
            profesores = kwargs.pop('profesores')
            super(GrupoForm, self).__init__(*args, **kwargs)
            self.fields['horario'].choices = horarios
            self.fields['profesor'].choices = profesores
        

class AlumnoForm(forms.Form):
    email =  forms.CharField(widget=forms.TextInput())
    nombres =  forms.CharField(widget=forms.TextInput())
    apellidos = forms.CharField(widget=forms.TextInput())
    activo =  forms.CharField(widget=forms.CheckboxInput())
    telefono =  forms.CharField(widget=forms.TextInput())
    grupo =  forms.ChoiceField(widget=forms.Select(), choices=[])

    def __init__(self, *args, **kwargs):
        if len(kwargs) > 0:
            grupos = kwargs.pop('grupos')
            super(AlumnoForm, self).__init__(*args, **kwargs)
            self.fields['grupo'].choices = grupos


class PagoForm(forms.Form):     
    fecha = forms.DateField(initial=date.today(), widget=forms.TextInput(attrs={'class': 'form-control', 'type':'date'}))
    monto =  forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Cordobas'}))    
    alumno =  forms.ChoiceField(widget=forms.Select(), choices=[])     
    tipo_pago = forms.ChoiceField(widget=forms.Select(), choices=[])     
    solvencia_mes = forms.BooleanField(required=False, widget=forms.CheckboxInput())          

    def __init__(self, *args, **kwargs):        
        if len(kwargs) > 0:             
            tipos_pagos = kwargs.pop('tipos_pagos')             
            alumnos = kwargs.pop('alumnos')             
            super(PagoForm, self).__init__(*args, **kwargs)         
            self.fields['tipo_pago'].choices = tipos_pagos             
            self.fields['alumno'].choices = alumnos
            
class ProfesorForm(forms.Form):
    nombres = forms.CharField(widget=forms.TextInput())
    apellidos = forms.CharField(widget=forms.TextInput())
    estudios = forms.CharField(widget=forms.TextInput())
    experiencia = forms.IntegerField(widget=forms.NumberInput())
    
class TipoPagoForm(forms.Form):
    nombre = forms.CharField(widget=forms.TextInput())
