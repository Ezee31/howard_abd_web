from django.http import HttpResponse
from django.db import models
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, TipoTurnoForm, HorarioForm, ProfesorForm, TipoPagoForm, GrupoForm, AlumnoForm, PagoForm
from django.contrib.auth import authenticate, login
from .models import TipoTurno, Horario, TipoPago, Profesor, Grupo, Alumno, Pago
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.template.loader import render_to_string


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
def tipo_turno(request, id=None):
    if request.method == 'GET':
        search_query = request.GET.get('search', '')
        page = request.GET.get('page', 1)  # captura la pagina en la que se encuentra
        
        if search_query:
            tipos_turnos = TipoTurno.objects.filter(
                models.Q(dias__icontains=search_query) |
                models.Q(hora_entrada__icontains=search_query) |
                models.Q(hora_salida__icontains=search_query) |
                models.Q(formato__icontains=search_query)
            )
        else:
            tipos_turnos = TipoTurno.objects.all()
        
        paginator = Paginator(tipos_turnos, 10)  # Mostrar 10 tipos de turnos por página
        tipos_turnos_page = paginator.get_page(page)
        
        if id:
            tipo_turno = TipoTurno.objects.get(id=id)
            edit_tipo_turno_form = TipoTurnoForm(initial={
                'dias': tipo_turno.dias, 
                'hora_entrada': tipo_turno.hora_entrada,
                'hora_salida': tipo_turno.hora_salida,
                'formato': tipo_turno.formato
            })
            return render(request, "crud/tipoTurno.html", {'tipos_turnos': tipos_turnos_page, 'form': edit_tipo_turno_form})
        else:
            new_tipo_turno_form = TipoTurnoForm()
            return render(request, "crud/tipoTurno.html", {'tipos_turnos': tipos_turnos_page, 'form': new_tipo_turno_form})

    if request.method == 'POST':
        tipo_turno_form = TipoTurnoForm(request.POST)
        if tipo_turno_form.is_valid():
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
                # Registrar la actualización
                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(TipoTurno).pk,
                    object_id=tipo_turno.pk,
                    object_repr=str(tipo_turno),
                    action_flag=CHANGE,
                    change_message=f'Updated {tipo_turno}'
                )
            else:
                new_tipo_turno = TipoTurno(
                    dias=dias, 
                    hora_entrada=hora_entrada,
                    hora_salida=hora_salida,
                    formato=formato
                )
                new_tipo_turno.save()
                # Registrar la creación
                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(TipoTurno).pk,
                    object_id=new_tipo_turno.pk,
                    object_repr=str(new_tipo_turno),
                    action_flag=ADDITION,
                    change_message=f'Added {new_tipo_turno}'
                )
            return redirect("tipo_turno")


@login_required(login_url='signin')
def tipo_turno_delete(request, id):
    tipo_turno = TipoTurno.objects.get(id=id)
    LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=ContentType.objects.get_for_model(TipoTurno).pk,
        object_id=tipo_turno.pk,
        object_repr=str(tipo_turno),
        action_flag=DELETION,
        change_message=f'Deleted {tipo_turno}'
    )
    tipo_turno.delete()
    return redirect("tipo_turno")



# horario endpoint
@login_required(login_url='signin')
def horario(request, id=None):
    tipos_turnos = TipoTurno.objects.all().values_list('id', 'dias')
    
    if request.method == 'GET':
        search_query = request.GET.get('search', '')
        page = request.GET.get('page', 1)  # captura la pagina en la que se encuentra
        
        if search_query:
            horarios = Horario.objects.filter(
                models.Q(nombre__icontains=search_query) |
                models.Q(tipo_turno__dias__icontains=search_query)
            )
        else:
            horarios = Horario.objects.all()
        
        paginator = Paginator(horarios, 10)  # Mostrar 10 horarios por página
        horarios_page = paginator.get_page(page)
        
        if id:
            horario = Horario.objects.get(id=id)
            edit_horario_form = HorarioForm(initial={
                'nombre': horario.nombre,
                'tipo_turno': horario.tipo_turno.id
            }, tipos_turnos=tipos_turnos)
            return render(request, "crud/horario.html", {'horarios': horarios_page, 'form': edit_horario_form})
        else:
            new_horario_form = HorarioForm(tipos_turnos=tipos_turnos)
            return render(request, "crud/horario.html", {'horarios': horarios_page, 'form': new_horario_form})

    if request.method == 'POST':
        horario_form = HorarioForm(request.POST, tipos_turnos=tipos_turnos)
        if horario_form.is_valid():
            nombre = horario_form.cleaned_data["nombre"]
            tipo_turno_id = horario_form.cleaned_data["tipo_turno"]
            tipo_turno = TipoTurno.objects.get(id=int(tipo_turno_id))
            if id:
                horario = get_object_or_404(Horario, id=id)
                horario.nombre = nombre
                horario.tipo_turno = tipo_turno
                horario.save()
                # Registrar la actualización
                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(Horario).pk,
                    object_id=horario.pk,
                    object_repr=str(horario),
                    action_flag=CHANGE,
                    change_message=f'Updated {horario}'
                )
            else:
                new_horario = Horario(
                    nombre=nombre,
                    tipo_turno=tipo_turno
                )
                new_horario.save()
                # Registrar la creación
                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(Horario).pk,
                    object_id=new_horario.pk,
                    object_repr=str(new_horario),
                    action_flag=ADDITION,
                    change_message=f'Added {new_horario}'
                )
            return redirect("horario")

@login_required(login_url='signin')
def horario_delete(request, id):
    horario = Horario.objects.get(id=id)
    LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=ContentType.objects.get_for_model(Horario).pk,
        object_id=horario.pk,
        object_repr=str(horario),
        action_flag=DELETION,
        change_message=f'Deleted {horario}'
    )
    horario.delete()
    return redirect("horario")

# profesor endpoints
@login_required(login_url='signin')
def profesor(request):
    profesores = Profesor.objects.all()
    if request.method == 'GET':
        search_query = request.GET.get('search', '')
        page = request.GET.get('page', 1)

        if search_query:
            profesores = Profesor.objects.filter(
                models.Q(nombres__icontains=search_query) |
                models.Q(apellidos__icontains=search_query)
            )
        else:
            profesores = Profesor.objects.all()

        paginator = Paginator(profesores, 10)
        profesores_page = paginator.get_page(page)

        new_profesor_form = ProfesorForm()
        return render(request, "crud/profesor.html", {'profesores': profesores_page, 'form': new_profesor_form})

    elif request.method == 'POST':
        form = ProfesorForm(request.POST)
        if form.is_valid():
            new_profesor = Profesor(
                nombres=form.cleaned_data["nombres"],
                apellidos=form.cleaned_data["apellidos"],
                estudios=form.cleaned_data["estudios"],
                experiencia=form.cleaned_data["experiencia"]
            )
            new_profesor.save()
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(Profesor).pk,
                object_id=new_profesor.pk,
                object_repr=str(new_profesor),
                action_flag=ADDITION,
                change_message=f'Added {new_profesor}'
            )
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'errors': form.errors}, status=400)

@login_required(login_url='signin')
def profesor_add(request):
    if request.method == 'GET':
        form = ProfesorForm()
        return render(request, 'crud/partials/profesor_form.html', {'form': form})

    if request.method == 'POST':
        form = ProfesorForm(request.POST)
        if form.is_valid():
            new_profesor = Profesor(
                nombres=form.cleaned_data["nombres"],
                apellidos=form.cleaned_data["apellidos"],
                estudios=form.cleaned_data["estudios"],
                experiencia=form.cleaned_data["experiencia"]
            )
            new_profesor.save()
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(Profesor).pk,
                object_id=new_profesor.pk,
                object_repr=str(new_profesor),
                action_flag=ADDITION,
                change_message=f'Added {new_profesor}'
            )
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'errors': form.errors}, status=400)

@login_required(login_url='signin')
def profesor_edit(request, id):
    profesor = get_object_or_404(Profesor, id=id)
    if request.method == 'GET':
        form = ProfesorForm(initial={
            'nombres': profesor.nombres,
            'apellidos': profesor.apellidos,
            'estudios': profesor.estudios,
            'experiencia': profesor.experiencia
        })
        return render(request, 'crud/partials/profesor_form.html', {'form': form, 'profesor_id': id})

    if request.method == 'POST':
        form = ProfesorForm(request.POST)
        if form.is_valid():
            profesor.nombres = form.cleaned_data["nombres"]
            profesor.apellidos = form.cleaned_data["apellidos"]
            profesor.estudios = form.cleaned_data["estudios"]
            profesor.experiencia = form.cleaned_data["experiencia"]
            profesor.save()
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(Profesor).pk,
                object_id=profesor.pk,
                object_repr=str(profesor),
                action_flag=CHANGE,
                change_message=f'Updated {profesor}'
            )
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'errors': form.errors}, status=400)

@login_required(login_url='signin')
def profesor_delete(request, id):
    profesor = Profesor.objects.get(id=id)
    LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=ContentType.objects.get_for_model(Profesor).pk,
        object_id=profesor.pk,
        object_repr=str(profesor),
        action_flag=DELETION,
        change_message=f'Deleted {profesor}'
    )
    profesor.delete()
    return redirect('profesor')
    

# tipopago endpoints
@login_required(login_url='signin')
def tipo_pago(request):
    tipos_pagos = TipoPago.objects.all()
    if request.method == 'GET':
        search_query = request.GET.get('search', '')
        page = request.GET.get('page', 1)

        if search_query:
            tipos_pagos = TipoPago.objects.filter(
                models.Q(nombre__icontains=search_query)
            )
        else:
            tipos_pagos = TipoPago.objects.all()

        paginator = Paginator(tipos_pagos, 10)
        tipos_pagos_page = paginator.get_page(page)

        new_tipo_pago_form = TipoPagoForm()
        return render(request, "crud/tipoPago.html", {'tipos_pagos': tipos_pagos_page, 'form': new_tipo_pago_form})

    elif request.method == 'POST':
        tipo_pago_form = TipoPagoForm(request.POST)
        if tipo_pago_form.is_valid():
            new_tipo_pago = TipoPago(
                nombre=tipo_pago_form.cleaned_data["nombre"]
            )
            new_tipo_pago.save()
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(TipoPago).pk,
                object_id=new_tipo_pago.pk,
                object_repr=str(new_tipo_pago),
                action_flag=ADDITION,
                change_message=f'Added {new_tipo_pago}'
            )
            return redirect("tipo_pago")
        else:
            return render(request, "crud/tipoPago.html", {'form': tipo_pago_form})

@login_required(login_url='signin')
def tipo_pago_add(request):
    if request.method == 'GET':
        form = TipoPagoForm()
        return render(request, 'crud/partials/tipo_pago_form.html', {'form': form})

    if request.method == 'POST':
        form = TipoPagoForm(request.POST)
        if form.is_valid():
            new_tipo_pago = TipoPago(
                nombre=form.cleaned_data["nombre"]
            )
            new_tipo_pago.save()
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(TipoPago).pk,
                object_id=new_tipo_pago.pk,
                object_repr=str(new_tipo_pago),
                action_flag=ADDITION,
                change_message=f'Added {new_tipo_pago}'
            )
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'errors': form.errors}, status=400)

@login_required(login_url='signin')
def tipo_pago_edit(request, id):
    tipo_pago = get_object_or_404(TipoPago, id=id)
    if request.method == 'GET':
        form = TipoPagoForm(initial={
            'nombre': tipo_pago.nombre,
        })
        return render(request, 'crud/partials/tipo_pago_form.html', {'form': form})

    if request.method == 'POST':
        form = TipoPagoForm(request.POST)
        if form.is_valid():
            tipo_pago.nombre = form.cleaned_data["nombre"]
            tipo_pago.save()
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(TipoPago).pk,
                object_id=tipo_pago.pk,
                object_repr=str(tipo_pago),
                action_flag=CHANGE,
                change_message=f'Updated {tipo_pago}'
            )
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'errors': form.errors}, status=400)

@login_required(login_url='signin')
def tipo_pago_delete(request, id):
    tipo_pago = TipoPago.objects.get(id=id)
    LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=ContentType.objects.get_for_model(TipoPago).pk,
        object_id=tipo_pago.pk,
        object_repr=str(tipo_pago),
        action_flag=DELETION,
        change_message=f'Deleted {tipo_pago}'
    )
    tipo_pago.delete()
    return redirect('tipo_pago')


# grupo endpoint 
@login_required(login_url='signin')
def grupo(request, id=None):
    horarios = Horario.objects.all().values_list('id','nombre')
    profesores = Profesor.objects.all().values_list('id','nombres')
    
    if request.method == 'GET':
        search_query = request.GET.get('search', '')
        page = request.GET.get('page', 1)
        
        if search_query:
            grupos = Grupo.objects.filter(
                models.Q(nombre__icontains=search_query) |
                models.Q(nivel__icontains=search_query) |
                models.Q(profesor__nombres__icontains=search_query) |
                models.Q(horario__nombre__icontains=search_query)
            )
        else:
            grupos = Grupo.objects.all()
        
        paginator = Paginator(grupos, 10)  # Mostrar 10 grupos por página
        grupos_page = paginator.get_page(page)
        
        if id:
            grupo = Grupo.objects.get(id=id)
            edit_grupo_form = GrupoForm(initial={
                'nombre': grupo.nombre, 
                'nivel': grupo.nivel,
                'cupo_maximo': grupo.cupo_maximo,
                'horario': grupo.horario.id,
                'profesor': grupo.profesor.id
            }, horarios=horarios, profesores=profesores)
            return render(request, "crud/grupo.html", {'grupos': grupos_page, 'form': edit_grupo_form})
        else:
            new_grupo_form = GrupoForm(horarios=horarios, profesores=profesores)
            return render(request, "crud/grupo.html", {'grupos': grupos_page, 'form': new_grupo_form})

    if request.method == 'POST':
        grupo_form = GrupoForm(request.POST, horarios=horarios, profesores=profesores)
        if grupo_form.is_valid():
            nombre = grupo_form.cleaned_data["nombre"]
            nivel = grupo_form.cleaned_data["nivel"]
            cupo_maximo = grupo_form.cleaned_data["cupo_maximo"]
            horario_id = grupo_form.cleaned_data["horario"]
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
                # Registrar la actualización
                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(Grupo).pk,
                    object_id=grupo.pk,
                    object_repr=str(grupo),
                    action_flag=CHANGE,
                    change_message=f'Updated {grupo}'
                )
            else:
                new_grupo = Grupo(
                    nombre=nombre, 
                    nivel=nivel,
                    cupo_maximo=cupo_maximo,
                    horario=horario,
                    profesor=profesor
                )
                new_grupo.save()
                # Registrar la creación
                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(Grupo).pk,
                    object_id=new_grupo.pk,
                    object_repr=str(new_grupo),
                    action_flag=ADDITION,
                    change_message=f'Added {new_grupo}'
                )
            return redirect("grupo")

@login_required(login_url='signin')
def grupo_delete(request, id):
    grupo = Grupo.objects.get(id=id)
    LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=ContentType.objects.get_for_model(Grupo).pk,
        object_id=grupo.pk,
        object_repr=str(grupo),
        action_flag=DELETION,
        change_message=f'Deleted {grupo}'
    )
    grupo.delete()
    return redirect("grupo")

# alumno endpoints
@login_required(login_url='signin')
def alumno(request, id=None):
    grupos = Grupo.objects.all().values_list('id', 'nombre')
    
    if request.method == 'GET':
        search_query = request.GET.get('search', '')
        page = request.GET.get('page', 1)  # captura la página en la que se encuentra

        if search_query:
            alumnos = Alumno.objects.filter(
                models.Q(nombres__icontains=search_query) |
                models.Q(apellidos__icontains=search_query) |
                models.Q(email__icontains=search_query) |
                models.Q(grupo__nombre__icontains=search_query)
            )
        else:
            alumnos = Alumno.objects.all()

        # paginado
        paginator = Paginator(alumnos, 10)  # Mostrar 10 alumnos por página
        alumnos_page = paginator.get_page(page)

        if id:
            alumno = Alumno.objects.get(id=id)
            edit_alumno_form = AlumnoForm(initial={
                'nombres': alumno.nombres,
                'email': alumno.email,
                'apellidos': alumno.apellidos,
                'activo': alumno.activo,
                'telefono': alumno.telefono,
                'grupo': alumno.grupo.id
            }, grupos=grupos)
            return render(request, "crud/alumno.html", {'alumnos': alumnos_page, 'form': edit_alumno_form})
        else:
            new_alumno_form = AlumnoForm(grupos=grupos)
            return render(request, "crud/alumno.html", {'alumnos': alumnos_page, 'form': new_alumno_form})

    elif request.method == 'POST':
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
                # Registrar la actualización
                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(Alumno).pk,
                    object_id=alumno.pk,
                    object_repr=str(alumno),
                    action_flag=CHANGE,
                    change_message=f'Updated {alumno}'
                )
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
                # Registrar la creación
                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(Alumno).pk,
                    object_id=new_alumno.pk,
                    object_repr=str(new_alumno),
                    action_flag=ADDITION,
                    change_message=f'Added {new_alumno}'
                )
            return redirect("alumno")
        else:
            return render(request, "crud/alumno.html", {'form': alumno_form})

@login_required(login_url='signin')
def alumno_add(request):
    grupos = Grupo.objects.all().values_list('id', 'nombre')
    if request.method == 'GET':
        form = AlumnoForm(grupos=grupos)
        return render(request, 'crud/partials/alumno_form.html', {'form': form})

    if request.method == 'POST':
        form = AlumnoForm(request.POST, grupos=grupos)
        if form.is_valid():
            new_alumno = Alumno(
                nombres=form.cleaned_data["nombres"],
                email=form.cleaned_data["email"],
                apellidos=form.cleaned_data["apellidos"],
                activo=form.cleaned_data["activo"],
                telefono=form.cleaned_data["telefono"],
                grupo=Grupo.objects.get(id=int(form.cleaned_data["grupo"]))
            )
            new_alumno.save()
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(Alumno).pk,
                object_id=new_alumno.pk,
                object_repr=str(new_alumno),
                action_flag=ADDITION,
                change_message=f'Added {new_alumno}'
            )
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'errors': form.errors}, status=400)

@login_required(login_url='signin')
def alumno_edit(request, id):
    grupos = Grupo.objects.all().values_list('id', 'nombre')
    alumno = get_object_or_404(Alumno, id=id)
    if request.method == 'GET':
        form = AlumnoForm(initial={
            'nombres': alumno.nombres,
            'email': alumno.email,
            'apellidos': alumno.apellidos,
            'activo': alumno.activo,
            'telefono': alumno.telefono,
            'grupo': alumno.grupo.id
        }, grupos=grupos)
        return render(request, 'crud/partials/alumno_form.html', {'form': form})

    if request.method == 'POST':
        form = AlumnoForm(request.POST, grupos=grupos)
        if form.is_valid():
            alumno.nombres = form.cleaned_data["nombres"]
            alumno.email = form.cleaned_data["email"]
            alumno.apellidos = form.cleaned_data["apellidos"]
            alumno.activo = form.cleaned_data["activo"]
            alumno.telefono = form.cleaned_data["telefono"]
            alumno.grupo = Grupo.objects.get(id=int(form.cleaned_data["grupo"]))
            alumno.save()
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(Alumno).pk,
                object_id=alumno.pk,
                object_repr=str(alumno),
                action_flag=CHANGE,
                change_message=f'Updated {alumno}'
            )
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'errors': form.errors}, status=400)

@login_required(login_url='signin')
def alumno_delete(request, id):
    alumno = Alumno.objects.get(id=id)
    # Registrar la eliminación
    LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=ContentType.objects.get_for_model(Alumno).pk,
        object_id=alumno.pk,
        object_repr=str(alumno),
        action_flag=DELETION,
        change_message=f'Deleted {alumno}'
    )
    alumno.delete()
    return redirect('alumno')

# pago endpoints
@login_required(login_url='signin')
def pago(request, id=None):
    alumnos = Alumno.objects.all().values_list('id', 'nombres')
    tipos_pagos = TipoPago.objects.all().values_list('id', 'nombre')

    if request.method == 'GET':
        search_query = request.GET.get('search', '')
        page = request.GET.get('page', 1)

        if search_query:
            pagos = Pago.objects.filter(
                models.Q(alumno__nombres__icontains=search_query) |
                models.Q(monto__icontains=search_query) |
                models.Q(tipo_pago__nombre__icontains=search_query)
            )
        else:
            pagos = Pago.objects.all()

        paginator = Paginator(pagos, 10)
        pagos_page = paginator.get_page(page)

        if id:
            pago = Pago.objects.get(id=id)
            edit_pago_form = PagoForm(initial={
                'fecha': pago.fecha,
                'monto': pago.monto,
                'alumno': pago.alumno.id,
                'tipo_pago': pago.tipo_pago.id,
                'solvencia_mes': pago.solvencia_mes
            }, alumnos=alumnos, tipos_pagos=tipos_pagos)
            return render(request, "crud/pago.html", {'pagos': pagos_page, 'form': edit_pago_form})
        else:
            new_pago_form = PagoForm(alumnos=alumnos, tipos_pagos=tipos_pagos)
            return render(request, "crud/pago.html", {'pagos': pagos_page, 'form': new_pago_form})

    elif request.method == 'POST':
        pago_form = PagoForm(request.POST, alumnos=alumnos, tipos_pagos=tipos_pagos)
        if pago_form.is_valid():
            fecha = pago_form.cleaned_data["fecha"]
            monto = pago_form.cleaned_data["monto"]
            alumno_id = pago_form.cleaned_data["alumno"]
            tipo_pago_id = pago_form.cleaned_data["tipo_pago"]
            solvencia_mes = pago_form.cleaned_data["solvencia_mes"]
            alumno = Alumno.objects.get(id=int(alumno_id))
            tipo_pago = TipoPago.objects.get(id=int(tipo_pago_id))
            if id:
                pago = get_object_or_404(Pago, id=id)
                pago.fecha = fecha
                pago.monto = monto
                pago.alumno = alumno
                pago.tipo_pago = tipo_pago
                pago.solvencia_mes = solvencia_mes
                pago.save()
                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(Pago).pk,
                    object_id=pago.pk,
                    object_repr=str(pago),
                    action_flag=CHANGE,
                    change_message=f'Updated {pago}'
                )
            else:
                new_pago = Pago(
                    fecha=fecha,
                    monto=monto,
                    alumno=alumno,
                    tipo_pago=tipo_pago,
                    solvencia_mes=solvencia_mes
                )
                new_pago.save()
                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(Pago).pk,
                    object_id=new_pago.pk,
                    object_repr=str(new_pago),
                    action_flag=ADDITION,
                    change_message=f'Added {new_pago}'
                )
            return redirect("pago")
        else:
            if id:
                return render(request, "crud/pago.html", {'form': pago_form, 'pago': pago})
            else:
                return render(request, "crud/pago.html", {'form': pago_form})

@login_required(login_url='signin')
def pago_add(request):
    alumnos = Alumno.objects.all().values_list('id', 'nombres')
    tipos_pagos = TipoPago.objects.all().values_list('id', 'nombre')
    if request.method == 'GET':
        form = PagoForm(alumnos=alumnos, tipos_pagos=tipos_pagos)
        return render(request, 'crud/partials/pago_form.html', {'form': form})

    if request.method == 'POST':
        form = PagoForm(request.POST, alumnos=alumnos, tipos_pagos=tipos_pagos)
        if form.is_valid():
            new_pago = Pago(
                fecha=form.cleaned_data["fecha"],
                monto=form.cleaned_data["monto"],
                alumno=Alumno.objects.get(id=int(form.cleaned_data["alumno"])),
                tipo_pago=TipoPago.objects.get(id=int(form.cleaned_data["tipo_pago"])),
                solvencia_mes=form.cleaned_data["solvencia_mes"]
            )
            new_pago.save()
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(Pago).pk,
                object_id=new_pago.pk,
                object_repr=str(new_pago),
                action_flag=ADDITION,
                change_message=f'Added {new_pago}'
            )
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'errors': form.errors}, status=400)

@login_required(login_url='signin')
def pago_edit(request, id):
    alumnos = Alumno.objects.all().values_list('id', 'nombres')
    tipos_pagos = TipoPago.objects.all().values_list('id', 'nombre')
    pago = get_object_or_404(Pago, id=id)
    if request.method == 'GET':
        form = PagoForm(initial={
            'fecha': pago.fecha,
            'monto': pago.monto,
            'alumno': pago.alumno.id,
            'tipo_pago': pago.tipo_pago.id,
            'solvencia_mes': pago.solvencia_mes
        }, alumnos=alumnos, tipos_pagos=tipos_pagos)
        return render(request, 'crud/partials/pago_form.html', {'form': form})

    if request.method == 'POST':
        form = PagoForm(request.POST, alumnos=alumnos, tipos_pagos=tipos_pagos)
        if form.is_valid():
            pago.fecha = form.cleaned_data["fecha"]
            pago.monto = form.cleaned_data["monto"]
            pago.alumno = Alumno.objects.get(id=int(form.cleaned_data["alumno"]))
            pago.tipo_pago = TipoPago.objects.get(id=int(form.cleaned_data["tipo_pago"]))
            pago.solvencia_mes = form.cleaned_data["solvencia_mes"]
            pago.save()
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(Pago).pk,
                object_id=pago.pk,
                object_repr=str(pago),
                action_flag=CHANGE,
                change_message=f'Updated {pago}'
            )
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'errors': form.errors}, status=400)

        
@login_required(login_url='signin')
def pago_delete(request, id):
    pago = Pago.objects.get(id=id)
    LogEntry.objects.log_action(
        user_id=request.user.pk,
        content_type_id=ContentType.objects.get_for_model(Pago).pk,
        object_id=pago.pk,
        object_repr=str(pago),
        action_flag=DELETION,
        change_message=f'Deleted {pago}'
    )
    pago.delete()
    return redirect("pago")

# reportes endpoints
@login_required(login_url='signin')
def reportes(request):
    search_query = request.GET.get('search', '')
    page = request.GET.get('page', 1) # Captura la página en la que se encuentra
    page_size = request.GET.get('page_size', 10)

    try:
        page = int(page)
    except ValueError:
        page = 1

    try:
        page_size = int(page_size)
    except ValueError:
        page_size = 10

    logs = LogEntry.objects.select_related('content_type', 'user').all().order_by('-action_time')
    total_alumnos = Alumno.objects.count()
    total_profesores = Profesor.objects.count()
    total_grupos = Grupo.objects.count()
    total_pagos = Pago.objects.count()
    pagos_por_mes = Pago.objects.values('fecha__month').annotate(total=models.Sum('monto')).order_by('fecha__month')

    if search_query:
        logs = logs.filter(
            models.Q(user__username__icontains=search_query) |
            models.Q(content_type__model__icontains=search_query) |
            models.Q(object_repr__icontains=search_query)
        )

    paginator = Paginator(logs, page_size)  # Mostrar `page_size` logs por página
    try:
        logs_page = paginator.page(page)
    except PageNotAnInteger:
        logs_page = paginator.page(1)
    except EmptyPage:
        logs_page = paginator.page(paginator.num_pages)

    context = {
        'logs': logs_page,
        'total_alumnos': total_alumnos,
        'total_profesores': total_profesores,
        'total_grupos': total_grupos,
        'total_pagos': total_pagos,
        'pagos_por_mes': pagos_por_mes,
        'ADDITION': ADDITION,
        'CHANGE': CHANGE,
        'DELETION': DELETION,
    }
    return render(request, 'utilidades/reportes.html', context)