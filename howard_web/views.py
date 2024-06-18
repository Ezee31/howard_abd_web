from django.http import HttpResponse
from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, TipoTurnoForm, HorarioForm, ProfesorForm, TipoPagoForm, GrupoForm, AlumnoForm, PagoForm
from django.contrib.auth import authenticate, login
from .models import TipoTurno, Horario, TipoPago, Profesor, Grupo, Alumno, Pago

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
    return render(request, "home.html")

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

# horario endpoint
@login_required(login_url='signin')
def horario(request, id=None):
    # obteniendo tipos turnos
    tipos_turnos = TipoTurno.objects.all().values_list('id', 'dias')

    if request.method == 'GET':
        #obteniendo todos los horarios de la base de datos
        horarios =  Horario.objects.all()
        if id: 
            horario = Horario.objects.get(id=id)
            edit_horario_form = HorarioForm(initial={'nombre': horario.nombre,
                                                     'tipo_turno': horario.tipo_turno}, tipos_turnos=tipos_turnos)
            return render(request, "crud/horario.html", {'horarios': horarios,
                                                         'form': edit_horario_form})
        else:
            new_horario_form = HorarioForm(tipos_turnos=tipos_turnos)
            return render(request, "crud/horario.html", {'horarios': horarios,
                                                         'form': new_horario_form})
    if request.method == 'POST':
        horario_form = HorarioForm(request.POST, tipos_turnos=tipos_turnos)
        is_valid = horario_form.is_valid()
        if is_valid:
            nombre = horario_form.cleaned_data["nombre"]
            tipo_turno_id = horario_form.cleaned_data["tipo_turno"]
            tipo_turno = TipoTurno.objects.get(id=int(tipo_turno_id))
            if id:
                horario = get_object_or_404(Horario, id=id)
                horario.nombre = nombre
                horario.tipo_turno = tipo_turno
                horario.save()
            else:
                new_horario = Horario(nombre=nombre, tipo_turno=tipo_turno)
                new_horario.save()
            return redirect("horario")

@login_required(login_url='signin')
def horario_delete(request,id):
    horario = Horario.objects.get(id=id)
    horario.delete()
    return redirect("horario")

# profesor endpoints
@login_required(login_url='signin')
def profesor(request, id=None):
    if request.method == 'GET':
        profesores = Profesor.objects.all()
        if id:
            profesor = Profesor.objects.get(id=id)
            edit_profesor_form = ProfesorForm(initial={'nombres': profesor.nombres, 'apellidos': profesor.apellidos, 'estudios': profesor.estudios, 'experiencia': profesor.experiencia})
            return render(request, "crud/profesor.html", {'profesores': profesores, 'form': edit_profesor_form})
        else:
            new_profesor_form = ProfesorForm()
            return render(request, "crud/profesor.html", {'profesores': profesores, 'form': new_profesor_form})
        
    if request.method == 'POST':
        profesor_form = ProfesorForm(request.POST)
        if profesor_form.is_valid():
            nombres = profesor_form.cleaned_data["nombres"]
            apellidos = profesor_form.cleaned_data["apellidos"]
            estudios = profesor_form.cleaned_data["estudios"]
            experiencia = profesor_form.cleaned_data["experiencia"]
            if id:
                profesor = get_object_or_404(Profesor, id=id)
                profesor.nombres = nombres
                profesor.apellidos = apellidos
                profesor.estudios = estudios
                profesor.experiencia = experiencia
                profesor.save()
            else:
                new_profesor = Profesor(nombres= nombres, apellidos= apellidos, estudios= estudios, experiencia= experiencia)
                new_profesor.save()
            return redirect("profesor")
  
@login_required(login_url='signin')      
def profesor_delete(request, id):
    profesor = get_object_or_404(Profesor, id=id)
    profesor.delete()
    return redirect("profesor")

# tipopago endpoints
@login_required(login_url='signin')
def tipo_pago(request, id=None):
    if request.method == 'GET':
        tipos_pago = TipoPago.objects.all()
        if id:
            tipo_pago = TipoPago.objects.get(id=id)
            edit_tipo_pago_form = TipoPagoForm(initial={'nombre': tipo_pago.nombre})
            return render(request, "crud/tipoPago.html", {'tipos_pago': tipos_pago, 'form': edit_tipo_pago_form})
        else:
            new_tipo_pago_form = TipoPagoForm()
            return render(request, "crud/tipoPago.html", {'tipos_pago': tipos_pago, 'form': new_tipo_pago_form})
        
    if request.method == 'POST':
        tipo_pago_form = TipoPagoForm(request.POST)
        if tipo_pago_form.is_valid():
            nombre = tipo_pago_form.cleaned_data["nombre"]
            if id:
                tipo_pago = get_object_or_404(TipoPago, id=id)
                tipo_pago.nombre = nombre
                tipo_pago.save()
            else:
                new_tipo_pago = TipoPago(nombre=nombre)
                new_tipo_pago.save()
            return redirect("tipo_pago")
        
@login_required(login_url='signin')
def tipo_pago_delete(request, id):
    tipo_pago = get_object_or_404(TipoPago, id=id)
    tipo_pago.delete()
    return redirect("tipo_pago")

# grupo endpoint 
@login_required(login_url='signin')
def grupo(request, id=None):
    # obteniendo horario
    horarios = Horario.objects.all().values_list('id','nombre')
    # obteniendo profesores
    profesores = Profesor.objects.all().values_list('id','nombres')
    
    if request.method == 'GET':
        search_query = request.GET.get('search','')
        if search_query:
            grupos = Grupo.objects.filter(
                models.Q(nombre__icontains=search_query) |
                models.Q(nivel__icontains=search_query) |
                models.Q(horario__nombre__icontains=search_query) |
                models.Q(profesor__nombres__icontains=search_query)
            )
        else: 
            grupos = Grupo.objects.all()    

        if id:
            grupo = Grupo.objects.get(id=id)
            edit_grupo_form = GrupoForm(initial={'nombre': grupo.nombre, 'nivel': grupo.nivel,
                                                 'cupo_maximo': grupo.cupo_maximo , 'horario': grupo.horario,
                                                 'profesor': grupo.profesor}, profesores=profesores, horarios=horarios)
            return render(request, "crud/grupo.html", {'grupos': grupos, 'form': edit_grupo_form})
        else:
            new_grupo_form =  GrupoForm(horarios = horarios, profesores = profesores)
            return render(request, "crud/grupo.html", {'grupos': grupos, 'form': new_grupo_form})
    if request.method == 'POST':
        grupo_form = GrupoForm(request.POST, horarios = horarios, profesores = profesores)
        is_valid = grupo_form.is_valid()
        if is_valid:
            nombre = grupo_form.cleaned_data["nombre"]
            nivel = grupo_form.cleaned_data["nivel"]
            cupo_maximo = grupo_form.cleaned_data["cupo_maximo"]
            horario_id  = grupo_form.cleaned_data["horario"]
            horario = Horario.objects.get(id=int(horario_id))
            profesor_id = grupo_form.cleaned_data["profesor"]
            profesor = Profesor.objects.get(id=int(profesor_id))
            if id:
                grupo = get_object_or_404(Grupo, id=id)
                grupo.nombre = nombre
                grupo.nivel = nivel
                grupo.cupo_maximo = cupo_maximo
                grupo.horario = horario
                grupo.profesor = profesor
                grupo.save()
            else:
                new_grupo = Grupo(nombre=nombre, nivel = nivel, cupo_maximo =cupo_maximo,
                                  horario = horario, profesor = profesor)
                new_grupo.save()
            return redirect("grupo")
@login_required(login_url='signin')
def grupo_delete(request,id):
    grupo = Grupo.objects.get(id=id)
    grupo.delete()
    return redirect("grupo")

# alumno endpoints
@login_required(login_url='signin')
def alumno(request, id=None):
    # Obteniendo los datos de grupos
    grupos = Grupo.objects.all().values_list('id', 'nombre')

    if request.method == 'GET':
        # Obteniendo todos los alumnos de la base de datos
        search_query = request.GET.get('search', '')
        if search_query:
            alumnos = Alumno.objects.filter(
                models.Q(nombres__icontains=search_query) |
                models.Q(apellidos__icontains=search_query) |
                models.Q(email__icontains=search_query) |
                models.Q(grupo__nombre__icontains=search_query)
            )
        else:
            alumnos = Alumno.objects.all()

        if id:
            alumno = Alumno.objects.get(id=id)
            edit_alumno_form = AlumnoForm(initial={
                'nombres': alumno.nombres,
                'email': alumno.email,
                'apellidos': alumno.apellidos,
                'activo': alumno.activo,
                'telefono': alumno.telefono,
                'grupo': alumno.grupo
            }, grupos=grupos)
            return render(request, "crud/alumno.html", {'alumnos': alumnos, 'form': edit_alumno_form})
        else:
            new_alumno_form = AlumnoForm(grupos=grupos)
            return render(request, "crud/alumno.html", {'alumnos': alumnos, 'form': new_alumno_form})

    if request.method == 'POST':
        alumno_form = AlumnoForm(request.POST, grupos=grupos)
        if alumno_form.is_valid():
            nombres = alumno_form.cleaned_data["nombres"]
            email = alumno_form.cleaned_data["email"]
            apellidos = alumno_form.cleaned_data["apellidos"]
            activo = alumno_form.cleaned_data["activo"]
            telefono = alumno_form.cleaned_data["telefono"]
            grupo_id = alumno_form.cleaned_data["grupo"]
            grupo = Grupo.objects.get(id=int(grupo_id))
            if id:
                alumno = get_object_or_404(Alumno, id=id)
                alumno.nombres = nombres
                alumno.email = email
                alumno.apellidos = apellidos
                alumno.activo = activo
                alumno.telefono = telefono
                alumno.grupo = grupo
                alumno.save()
            else:
                new_alumno = Alumno(
                    nombres=nombres,
                    email=email,
                    apellidos=apellidos,
                    activo=activo,
                    telefono=telefono,
                    grupo=grupo
                )
                new_alumno.save()
            return redirect("alumno")

#alumno delete
@login_required(login_url='signin')
def alumno_delete(request,id):
    alumno = Alumno.objects.get(id=id)
    alumno.delete()
    return redirect('alumno')

#pago endpoints
@login_required(login_url='signin')
def pago(request, id=None):
    #obteniendo tipos pagos, alumnos
    tipos_pagos = TipoPago.objects.all().values_list('id', 'nombre')
    alumnos = Alumno.objects.all().values_list('id', 'nombres')
    
    if request.method == 'GET':
        #obteniendo todos los pagos de la base de datos
        pagos = Pago.objects.all()
        if id:
            pago = Pago.objects.get(id=id)
            edit_pago_form = PagoForm(initial={'fecha': pago.fecha, 'monto': pago.monto, 'alumno': pago.alumno, 
                                               'tipo_pago': pago.tipo_pago, 'solvencia_mes': pago.solvencia_mes}
                                               ,tipos_pagos=tipos_pagos, alumnos = alumnos)
            return render(request, "crud/pago.html",{'pagos': pagos, 'form': edit_pago_form})
        else:
            new_pago_form = PagoForm(tipos_pagos = tipos_pagos, alumnos = alumnos)
            return render(request, "crud/pago.html", {'pagos': pagos, 'form': new_pago_form})
    if request.method == 'POST':
        pago_form = PagoForm(request.POST, tipos_pagos = tipos_pagos, alumnos = alumnos)
        is_valid = pago_form.is_valid()
        if is_valid:
            fecha = pago_form.cleaned_data["fecha"]
            monto = pago_form.cleaned_data["monto"]
            tipo_pago_id = pago_form.cleaned_data["tipo_pago"]
            tipo_pago = TipoPago.objects.get(id=int(tipo_pago_id))
            alumno_id = pago_form.cleaned_data["alumno"]
            alumno = Alumno.objects.get(id=int(alumno_id))
            solvencia_mes = pago_form.cleaned_data["solvencia_mes"]
        if id:
            pago = get_object_or_404(Pago, id=id)
            pago.fecha = fecha
            pago.monto = monto
            pago.alumno = alumno
            pago.solvencia_mes = solvencia_mes
            pago.save()
        else:
            new_pago = Pago(fecha=fecha, monto=monto,tipo_pago=tipo_pago,
                            alumno=alumno,solvencia_mes=solvencia_mes)
            new_pago.save()
        return redirect("pago")

#alumno delete
@login_required(login_url='signin')
def pago_delete(request,id):
    pago = Pago.objects.get(id=id)
    pago.delete()
    return redirect("pago")