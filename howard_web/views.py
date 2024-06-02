from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, TipoTurnoForm
from django.contrib.auth import authenticate, login
from .models import TipoTurno

# Create your views here.
# login endpoint
def signin(request):
    if request.method == "POST":
        login_form = LoginForm(request.POST)
        is_valid = login_form.is_valid()
        if is_valid:
            username = login_form.cleaned_data["username"]
            password = login_form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect("dashboard")

    # returning dashboard if user is already logged into the system
    if request.method == 'GET' and request.user.is_authenticated:
        return redirect("dashboard")

    # returning login form
    new_login_form = LoginForm()
    return render(request, "login/index.html", {'form': new_login_form})

# dashboard endpoint
@login_required(login_url='signin')
def dashboard(request):
    return render(request, "dashboard/index.html")

# tipo turno endpoints
@login_required(login_url='signin')
def tipo_turno(request,id=None):
    if request.method == 'GET':
        # obteniendo todos los tipos turnos de la base de datos
        tipos_turnos = TipoTurno.objects.all()
        if id:
            tipo_turno = TipoTurno.objects.get(id=id)
            edit_tipo_turno_form = TipoTurnoForm(initial={'dias': tipo_turno.dias, 'hora_entrada': tipo_turno.hora_entrada,'hora_salida': tipo_turno.hora_salida,
                                                          'formato': tipo_turno.formato})
            return render(request, "crud/tipoTurno.html", {'tipos_turnos': tipos_turnos, 'form': edit_tipo_turno_form})
        else:
            new_tipo_turno_form = TipoTurnoForm()
            return render(request, "crud/tipoTurno.html", {'tipos_turnos': tipos_turnos, 'form': new_tipo_turno_form})
    if request.method == 'POST':                               
        tipo_turno_form = TipoTurnoForm(request.POST) 
        is_valid = tipo_turno_form.is_valid()
        if is_valid:
            dias = tipo_turno_form.cleaned_data["dias"]
            hora_entrada = tipo_turno_form.cleaned_data["hora_entrada"]
            hora_salida = tipo_turno_form.cleaned_data["hora_salida"]
            formato = tipo_turno_form.cleaned_data["formato"]
            if id:
                tipo_turno = get_object_or_404(TipoTurno, id=id)
                tipo_turno.dias = dias
                tipo_turno.hora_entrada = hora_entrada
                tipo_turno.hora_salida = hora_salida
                tipo_turno.formato = formato
                tipo_turno.save()
            else:
                new_tipo_turno = TipoTurno(dias=dias, hora_entrada=hora_entrada, hora_salida=hora_salida, formato=formato)
                new_tipo_turno.save()
            return redirect("tipo_turno")

@login_required(login_url='signin')
def tipo_turno_delete(request,id):
    tipo_turno = TipoTurno.objects.get(id=id)
    tipo_turno.delete()
    return redirect("tipo_turno")

#def tipo_turno_buscar(request):