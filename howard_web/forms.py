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