from django import forms
from datetime import date

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg fs-6', 'placeholder': 'Nombre de Usuario'}),
        max_length=150
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg fs-6', 'placeholder': 'Contraseña'}),
        max_length=128
    )

class HorarioForm(forms.Form):
    tipo_turno = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=[]
    )
    nombre = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'})
    )

    def __init__(self, *args, **kwargs):
        tipos_turnos = kwargs.pop('tipos_turnos', [])
        super(HorarioForm, self).__init__(*args, **kwargs)
        self.fields['tipo_turno'].choices = tipos_turnos

class GrupoForm(forms.Form):
    nombre = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'})
    )
    nivel = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=[(str(i), str(i)) for i in range(1, 13)]
    )
    cupo_maximo = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cupo Máximo'})
    )
    horario = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=[]
    )
    profesor = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=[]
    )

    def __init__(self, *args, **kwargs):
        horarios = kwargs.pop('horarios', [])
        profesores = kwargs.pop('profesores', [])
        super(GrupoForm, self).__init__(*args, **kwargs)
        self.fields['horario'].choices = horarios
        self.fields['profesor'].choices = profesores

class AlumnoForm(forms.Form):
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    nombres = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres'})
    )
    apellidos = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'})
    )
    activo = forms.BooleanField(
        required=False, 
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    telefono = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefono'})
    )
    grupo = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=[]
    )

    def __init__(self, *args, **kwargs):
        grupos = kwargs.pop('grupos', [])
        super(AlumnoForm, self).__init__(*args, **kwargs)
        self.fields['grupo'].choices = grupos

class PagoForm(forms.Form):
    fecha = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    monto = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Monto'})
    )
    alumno = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=[]
    )
    tipo_pago = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=[]
    )
    solvencia_mes = forms.BooleanField(
        required=False, 
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def __init__(self, *args, **kwargs):
        tipos_pagos = kwargs.pop('tipos_pagos', [])
        alumnos = kwargs.pop('alumnos', [])
        super(PagoForm, self).__init__(*args, **kwargs)
        self.fields['tipo_pago'].choices = tipos_pagos
        self.fields['alumno'].choices = alumnos

class ProfesorForm(forms.Form):
    nombres = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres'})
    )
    apellidos = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'})
    )
    estudios = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Estudios'})
    )
    experiencia = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Experiencia'})
    )

class TipoTurnoForm(forms.Form):
    dias = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Días'})
    )
    hora_entrada = forms.CharField(
        widget=forms.TimeInput(attrs={'class': 'form-control', 'placeholder': 'Hora de Entrada'})
    )
    hora_salida = forms.CharField(
        widget=forms.TimeInput(attrs={'class': 'form-control', 'placeholder': 'Hora de Salida'})
    )
    formato = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Formato'})
    )

class TipoPagoForm(forms.Form):
    nombre = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'})
    )
