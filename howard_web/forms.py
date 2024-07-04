from django import forms
from datetime import date
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import PasswordChangeForm



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
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    nombres = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres'}))
    apellidos = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}))
    activo = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    telefono = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefono'}))
    grupo = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}), choices=[])

    def __init__(self, *args, **kwargs):
        if 'grupos' in kwargs:
            grupos = kwargs.pop('grupos')
            super(AlumnoForm, self).__init__(*args, **kwargs)
            self.fields['grupo'].choices = grupos
        else:
            super(AlumnoForm, self).__init__(*args, **kwargs)

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





class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(CustomPasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})

class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        new_password_confirm = cleaned_data.get('new_password_confirm')

        if new_password and new_password != new_password_confirm:
            self.add_error('new_password_confirm', 'Las contraseñas no coinciden')

        if new_password:
            try:
                validate_password(new_password)
            except forms.ValidationError as e:
                self.add_error('new_password', e)
        
        return cleaned_data
    
class ProfilePictureForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['profile_picture']

    def __init__(self, *args, **kwargs):
        super(ProfilePictureForm, self).__init__(*args, **kwargs)
        self.fields['profile_picture'].widget.attrs.update({'class': 'form-control-file'})

            
class UserRegisterForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'profile_picture']
    
    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['profile_picture'].widget.attrs.update({'class': 'form-control-file'})

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        validate_password(password2)
        return password2
