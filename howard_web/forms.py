from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-lg fs-6', 'placeholder': 'Nombre de Usuario'}), max_length=150)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg fs-6', 'placeholder': 'Contraseña'}), max_length=128)

class AlumnoForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

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

## Forms agregados necesitan verificacion
class GrupoForm(forms.Form):
    nombre =  forms.CharField(widget=forms.TextInput())
    nivel =  forms.CharField(widget=forms.TextInput())
    cupo_maximo =  forms.CharField(widget=forms.TextInput())
    horario =  forms.CharField(widget=forms.TextInput())
    profesor =  forms.CharField(widget=forms.TextInput())

class AlumnoForm(forms.Form):
    email =  forms.CharField(widget=forms.TextInput())
    nombre =  forms.CharField(widget=forms.TextInput())
    apellidos = forms.CharField(widget=forms.TextInput())
    activo =  forms.CharField(widget=forms.TextInput())
    telefono =  forms.CharField(widget=forms.TextInput())
    grupo =  forms.CharField(widget=forms.TextInput())

class PagoForm(forms.Form):
    fecha =  forms.CharField(widget=forms.TextInput())
    monto =  forms.CharField(widget=forms.TextInput())
    alumno =  forms.CharField(widget=forms.TextInput())
    tipo_pago =  forms.CharField(widget=forms.TextInput())
    solvencia_mes =  forms.CharField(widget=forms.TextInput())

