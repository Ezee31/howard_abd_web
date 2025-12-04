from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, TipoTurnoForm, HorarioForm, ProfesorForm, TipoPagoForm, GrupoForm, AlumnoForm, PagoForm
from django.contrib.auth import authenticate, login
from .models import TipoTurno, Horario, TipoPago, Profesor, Grupo, Alumno, Pago
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, JsonResponse
from .forms import UserUpdateForm, UserRegisterForm
from django.contrib.auth import update_session_auth_hash
from .forms import ProfilePictureForm, CustomPasswordChangeForm
from django.contrib import messages
from .utils import agregar_icono_tipo_pago
from json import dumps
from datetime import date, timedelta
from num2words import num2words

# Imports para PDF (ReportLab)
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.db.models import Sum, Avg, Count

# Importación de Servicios de IA
from .ai_service import (
    predecir_ingresos_prophet, 
    analizar_matricula_prophet, 
    segmentar_clientes_kmeans, 
    predecir_desercion_logistica, 
    optimizar_cupos, 
    analizar_riesgo_morosidad
)

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

    if request.method == 'GET' and request.user.is_authenticated:
        return redirect("dashboard")

    new_login_form = LoginForm()
    return render(request, "login/index.html", {'form': new_login_form})

# 1. DASHBOARD ORIGINAL (Solo muestra el Home con logos)
@login_required(login_url='signin')
def dashboard(request):
    # Renderiza la página de inicio con el logo
    return render(request, "home.html")

# 2. VISTA PARA IA (Panel de Inteligencia Artificial)
@login_required(login_url='signin')
def ia_dashboard(request):
    total_alumnos = Alumno.objects.filter(activo=True).count()
    
    # 1. Ingresos (Prophet)
    monto_predicho, mes_predicho, precision = predecir_ingresos_prophet()
    
    # 2. Estacionalidad
    pico_matricula, bajo_matricula = analizar_matricula_prophet()
    
    # 3. Clustering de Clientes
    clustering_data = segmentar_clientes_kmeans()
    
    # 4. Deserción (Churn)
    lista_riesgo_desercion = predecir_desercion_logistica()
    
    # 5. Cupos
    lista_cupos = optimizar_cupos()
    
    # 6. Riesgo Morosidad
    riesgo_mes, riesgo_detalle = analizar_riesgo_morosidad()

    # Estado general
    if monto_predicho > 0:
        estado_ia = "Activo (Multi-Modelo)"
        color_estado = "success"
    else:
        estado_ia = "Datos Insuficientes"
        color_estado = "warning"

    context = {
        'total_alumnos': total_alumnos,
        'prediccion_ingresos': monto_predicho,
        'mes_prediccion': mes_predicho,
        'precision_modelo': precision,
        'estado_ia': estado_ia,
        'color_estado': color_estado,
        'pico_matricula': pico_matricula,
        'bajo_matricula': bajo_matricula,
        'clustering': clustering_data,
        'riesgo_desercion': lista_riesgo_desercion,
        'cupos': lista_cupos,
        'riesgo_mes': riesgo_mes,
        'riesgo_detalle': riesgo_detalle,
    }
    return render(request, "ia_dashboard.html", context)

# tipo turno endpoints
@login_required(login_url='signin')
def tipo_turno(request):
    tipos_turnos = TipoTurno.objects.all()
    if request.method == 'GET':
        search_query = request.GET.get('search', '')
        page = request.GET.get('page', 1)
        
        if search_query:
            tipos_turnos = TipoTurno.objects.filter(
                models.Q(dias__icontains=search_query) |
                models.Q(hora_entrada__icontains=search_query) |
                models.Q(hora_salida__icontains=search_query) |
                models.Q(formato__icontains=search_query)
            )
        else:
            tipos_turnos = TipoTurno.objects.all()
        
        paginator = Paginator(tipos_turnos, 10)
        tipos_turnos_page = paginator.get_page(page)

        new_tipo_turno_form = TipoTurnoForm()
        return render(request, "crud/tipoTurno.html", {'tipos_turnos': tipos_turnos_page, 'form': new_tipo_turno_form})

    elif request.method == 'POST':
        form = TipoTurnoForm(request.POST)
        if form.is_valid():
            new_tipo_turno = TipoTurno(    
                dias = form.cleaned_data["dias"],
                hora_entrada = form.cleaned_data["hora_entrada"],
                hora_salida = form.cleaned_data["hora_salida"],
                formato = form.cleaned_data["formato"]
            )
            new_tipo_turno.save()
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(TipoTurno).pk,
                object_id=new_tipo_turno.pk,
                object_repr=str(new_tipo_turno),
                action_flag=ADDITION,
                change_message=f'Added {new_tipo_turno}'
            )
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': form.errors}, status=400)
        
@login_required(login_url='signin')
def tipo_turno_add(request):
    if request.method == 'GET':
        form = TipoTurnoForm()
        return render(request, 'crud/partials/tipo_turno_form.html', {'form': form})
    
    if request.method == 'POST':
        form = TipoTurnoForm(request.POST)
        if form.is_valid():
            new_tipo_turno = TipoTurno(
                dias=form.cleaned_data["dias"],
                hora_entrada=form.cleaned_data["hora_entrada"],
                hora_salida=form.cleaned_data["hora_salida"],
                formato=form.cleaned_data["formato"]
            )
            new_tipo_turno.save()
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(TipoTurno).pk,
                object_id=new_tipo_turno.pk,
                object_repr=str(new_tipo_turno),
                action_flag=ADDITION,
                change_message=f'Added {new_tipo_turno}'
            )
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'errors': form.errors}, status=400)

@login_required(login_url='signin')
def tipo_turno_edit(request, id):
    tipo_turno = get_object_or_404(TipoTurno, id=id)
    if request.method == 'GET':
        form = TipoTurnoForm(initial={
                'dias': tipo_turno.dias, 
                'hora_entrada': tipo_turno.hora_entrada,
                'hora_salida': tipo_turno.hora_salida,
                'formato': tipo_turno.formato
        })
        return render(request, 'crud/partials/tipo_turno_form.html', {'form': form, 'tipo_turno_id': id})
    
    if request.method == 'POST':
        form = TipoTurnoForm(request.POST)
        if form.is_valid():
            tipo_turno.dias = form.cleaned_data["dias"]
            tipo_turno.hora_entrada = form.cleaned_data["hora_entrada"]
            tipo_turno.hora_salida = form.cleaned_data["hora_salida"]
            tipo_turno.formato = form.cleaned_data["formato"]
            tipo_turno.save()
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(TipoTurno).pk,
                object_id=tipo_turno.pk,
                object_repr=str(tipo_turno),
                action_flag=CHANGE,
                change_message=f'Updated {tipo_turno}'
            )
            return JsonResponse({'success': True})
        else: 
            return JsonResponse({'errors': form.errors}, status=400)

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
        page = request.GET.get('page', 1)
        
        if search_query:
            horarios = Horario.objects.filter(
                models.Q(nombre__icontains=search_query) |
                models.Q(tipo_turno__dias__icontains=search_query)
            )
        else:
            horarios = Horario.objects.all()
        
        paginator = Paginator(horarios, 10)
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

    elif request.method == 'POST':
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
                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(Horario).pk,
                    object_id=new_horario.pk,
                    object_repr=str(new_horario),
                    action_flag=ADDITION,
                    change_message=f'Added {new_horario}'
                )
            return redirect("horario")
        else:
            if id:
                return render(request, "crud/horario.html", {'form': horario_form, 'horario': horario})
            else:
                return render(request, "crud/horario.html", {'form': horario_form})

@login_required(login_url='signin')
def horario_add(request):
    tipos_turnos = TipoTurno.objects.all().values_list('id', 'dias')
    if request.method == 'GET':
        form = HorarioForm(tipos_turnos = tipos_turnos)
        return render(request, 'crud/partials/horario_form.html', {'form': form})
    
    if request.method == 'POST':
        form = HorarioForm(request.POST, tipos_turnos=tipos_turnos)
        if form.is_valid():
            new_horario = Horario(
                nombre=form.cleaned_data["nombre"],
                tipo_turno=TipoTurno.objects.get(id=int(form.cleaned_data["tipo_turno"]))
            )
            new_horario.save()
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(Horario).pk,
                object_id=new_horario.pk,
                object_repr=str(new_horario),
                action_flag=ADDITION,
                change_message=f'Added {new_horario}'
            )
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'errors': form.errors}, status=400)

@login_required(login_url='signin')
def horario_edit(request, id):
    tipos_turnos = TipoTurno.objects.all().values_list('id','dias')
    horario= get_object_or_404(Horario, id=id)
    if request.method == 'GET':
        form = HorarioForm(initial={
            'nombre': horario.nombre,
            'tipo_turno': horario.tipo_turno.id,
        }, tipos_turnos=tipos_turnos)
        return render(request, 'crud/partials/horario_form.html', {'form': form})
    
    if request.method == 'POST':
        form = HorarioForm(request.POST, tipos_turnos=tipos_turnos)
        if form.is_valid():
            horario.nombre = form.cleaned_data["nombre"]
            horario.tipo_turno = TipoTurno.objects.get(id=int(form.cleaned_data["tipo_turno"]))
            horario.save()
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(Horario).pk,
                object_id=horario.pk,
                object_repr=str(horario),
                action_flag=CHANGE,
                change_message=f'Updated {horario}'
            )
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'errors': form.errors}, status=400)

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
    horarios = Horario.objects.all().values_list('id', 'nombre')
    profesores = Profesor.objects.all().values_list('id', 'nombres')
    
    if request.method == 'GET':
        search_query = request.GET.get('search', '')
        page = request.GET.get('page', 1)
        
        if search_query:
            grupos = Grupo.objects.filter(
                models.Q(nombre__icontains=search_query) |
                models.Q(nivel__icontains=search_query) |
                models.Q(cupo_maximo__icontains=search_query) |
                models.Q(horario__nombre__icontains=search_query) |
                models.Q(profesor__nombres__icontains=search_query)
            )
        else:
            grupos = Grupo.objects.all()
        
        paginator = Paginator(grupos, 10) 
        grupos_page = paginator.get_page(page)
        
        if id:
            grupo = get_object_or_404(Grupo, id=id)
            edit_grupo_form = GrupoForm(
                initial={
                    'nombre': grupo.nombre,
                    'nivel': grupo.nivel,
                    'cupo_maximo': grupo.cupo_maximo,
                    'horario': grupo.horario.id,
                    'profesor': grupo.profesor.id
                },
                horarios=horarios,
                profesores=profesores
            )
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
            horario = get_object_or_404(Horario, id=horario_id)
            profesor_id = grupo_form.cleaned_data["profesor"]
            profesor = get_object_or_404(Profesor, id=profesor_id)
            
            if id:
                grupo = get_object_or_404(Grupo, id=id)
                grupo.nombre = nombre
                grupo.nivel = nivel
                grupo.cupo_maximo = cupo_maximo
                grupo.horario = horario
                grupo.profesor = profesor
                grupo.save()
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
                LogEntry.objects.log_action(
                    user_id=request.user.pk,
                    content_type_id=ContentType.objects.get_for_model(Grupo).pk,
                    object_id=new_grupo.pk,
                    object_repr=str(new_grupo),
                    action_flag=ADDITION,
                    change_message=f'Added {new_grupo}'
                )
            return redirect("grupo")
        else:
            if id:
                return render(request, "crud/grupo.html", {'form': grupo_form, 'grupo': grupo})
            else:
                return render(request, "crud/grupo.html", {'form': grupo_form})

@login_required(login_url='signin')
def grupo_add(request):
    horarios = Horario.objects.all().values_list('id', 'nombre')
    profesores = Profesor.objects.all().values_list('id', 'nombres')
    if request.method == 'GET':
        form = GrupoForm(horarios=horarios, profesores=profesores)
        return render(request, 'crud/partials/grupo_form.html', {'form': form})
    
    if request.method == 'POST':
        form = GrupoForm(request.POST, horarios=horarios, profesores=profesores)
        if form.is_valid():
            horario = get_object_or_404(Horario, id=int(form.cleaned_data["horario"]))
            profesor = get_object_or_404(Profesor, id=int(form.cleaned_data["profesor"]))
            new_grupo = Grupo(
                nombre=form.cleaned_data["nombre"],
                nivel=form.cleaned_data["nivel"],
                cupo_maximo=form.cleaned_data["cupo_maximo"],
                horario=horario,
                profesor=profesor
            )
            new_grupo.save()
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(Grupo).pk,
                object_id=new_grupo.pk,
                object_repr=str(new_grupo),
                action_flag=ADDITION,
                change_message=f'Added {new_grupo}'
            )
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'errors': form.errors}, status=400)

@login_required(login_url='signin')
def grupo_edit(request, id):
    horarios = Horario.objects.all().values_list('id', 'nombre')
    profesores = Profesor.objects.all().values_list('id', 'nombres')
    grupo = get_object_or_404(Grupo, id=id)
    if request.method == 'GET':
        form = GrupoForm(
            initial={
                'nombre': grupo.nombre,
                'nivel': grupo.nivel,
                'cupo_maximo': grupo.cupo_maximo,
                'profesor': grupo.profesor.id,
                'horario': grupo.horario.id
            },
            horarios=horarios,
            profesores=profesores
        )
        return render(request, 'crud/partials/grupo_form.html', {'form': form})
        
    if request.method == 'POST':
        form = GrupoForm(request.POST, horarios=horarios, profesores=profesores)
        if form.is_valid():
            grupo.nombre = form.cleaned_data["nombre"]
            grupo.nivel = form.cleaned_data["nivel"]
            grupo.cupo_maximo = form.cleaned_data["cupo_maximo"]
            grupo.profesor = get_object_or_404(Profesor, id=int(form.cleaned_data["profesor"]))
            grupo.horario = get_object_or_404(Horario, id=int(form.cleaned_data["horario"]))
            grupo.save()
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(Grupo).pk,
                object_id=grupo.pk,
                object_repr=str(grupo),
                action_flag=CHANGE,
                change_message=f'Updated {grupo}'
            )
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'errors': form.errors}, status=400)

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
        page = request.GET.get('page', 1) 

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
        paginator = Paginator(alumnos, 10) 
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
            alumno_creado = {'id':new_alumno.pk, 'nombres':new_alumno.nombres, 'apellidos': new_alumno.apellidos}
            return JsonResponse({'success': True, 'alumno': alumno_creado})
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
            return render(request, "crud/pago.html", {'pagos': pagos_page})

    elif request.method == 'POST':
        pago_form = PagoForm(request.POST)
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
    if request.method == 'GET':
        form = PagoForm()
        return render(request, 'crud/partials/pago_form.html', {'form': form})

    if request.method == 'POST':
        form = PagoForm(request.POST)
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

            grupo = Grupo.objects.select_related('horario').get(id=new_pago.alumno.grupo_id)
            tipo_turno = TipoTurno.objects.get(id=grupo.horario.tipo_turno_id)

            return JsonResponse({
                'success': True,
                'pago_id': new_pago.pk,
                'fecha': date.today().strftime('%B %d, %Y'),
                'alumno': f'{new_pago.alumno.nombres} {new_pago.alumno.apellidos}',
                'cantidad_en_letras': str(num2words(new_pago.monto, to='currency', lang='es_NI')).capitalize(),
                'mes_pagado': new_pago.fecha.strftime("%B %Y"),
                'horario': f'{tipo_turno.dias} de {tipo_turno.hora_entrada}-{tipo_turno.hora_salida} {tipo_turno.formato}',
                'importe': f'C$ {new_pago.monto}'
            })
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
        form = PagoForm(request.POST)
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

@login_required(login_url='signin')
def pagos(request):
    # lecturas de base de datos
    tipos_pagos = TipoPago.objects.all()
    grupos = Grupo.objects.all().values_list('id', 'nombre')

    # agregando icono a cada tipo de pago
    tipos_pagos = map(agregar_icono_tipo_pago, tipos_pagos)

    # crear formularios
    new_alumno_form = AlumnoForm(grupos=grupos)
    new_pago_form = PagoForm(initial={'fecha': date.today()})

    context = {
        'tipos_pagos': tipos_pagos,
        'alumno_form': new_alumno_form,
        'pago_form': new_pago_form
    }
    return render(request, "procesos/pagos.html", context)

@login_required(login_url='signin')
def filtrar_alumnos(request):
    filtro = request.GET.get('filtrar', '')
    alumnos_encontrados = dumps(
        list(
            Alumno.objects.filter(
                models.Q(nombres__icontains=filtro) |
                models.Q(apellidos__icontains=filtro)
            ).values('id', 'nombres', 'apellidos')
        )
    )
    return JsonResponse({'alumnos': alumnos_encontrados}, status=200)

@login_required(login_url='signin')
def descargar_factura(request, pago_id):
    pago = Pago.objects.select_related('alumno', 'tipo_pago').get(id=pago_id)

    # armando nombre del archivo
    tipo_pago_efectuado = pago.tipo_pago.nombre.lower()
    mes = pago.fecha.strftime("%B").lower()
    anio = pago.fecha.strftime("%Y")
    nombre_del_alumno = pago.alumno.nombres.lower() if ' ' not in pago.alumno.nombres else pago.alumno.nombres.split(' ')[0].lower()
    nombre_del_archivo = f'{tipo_pago_efectuado}_{mes}_{anio}_{nombre_del_alumno}'

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={nombre_del_archivo}.pdf'

    # inicializando documento
    pdf = canvas.Canvas(response, pagesize=letter)
    pdf.setFont('Helvetica-Bold', 12)
    pdf.setTitle('Hoja de matricula' if tipo_pago_efectuado == 'matricula' else 'Factura')
    
    grupo = Grupo.objects.select_related('horario').get(id=pago.alumno.grupo_id)
    tipo_turno = TipoTurno.objects.get(id=grupo.horario.tipo_turno_id)

    # header
    pdf.drawString(219, 760, 'Howard Bilingual School - H.B.S')
    pdf.drawString(234, 730, 'RECIBO OFICIAL DE CAJA')

    # numero de whatsapp
    lienzo = Drawing(400, 200)
    lienzo.add(Rect(365, 120, 130, 55, fillColor=colors.lightgrey, strokeColor=colors.lightgrey))
    lienzo.add(String(400, 153, 'Whatsapp', fontName='Helvetica-Bold', fontSize=12, fillColor=colors.black))
    lienzo.add(String(400, 132, '8593-7255', fontName='Helvetica-Bold', fontSize=12, fillColor=colors.black))

    # datos de la factura
    no_recibo = pago.id
    pdf.drawString(192, 690, 'No. RECIBO')
    lienzo.add(Rect(220, 88, 30, 14, fillColor=colors.lightgrey, strokeColor=colors.lightgrey))
    lienzo.add(String(237, 90, str(no_recibo), fontName='Helvetica-Bold', fontSize=12, fillColor=colors.black))

    # fecha
    pdf.drawString(386, 690, 'FECHA:')
    pdf.line(440, 689, 560, 689)
    lienzo.add(String(395, 90, date.today().strftime('%B %d, %Y'), fontName='Helvetica', fontSize=12, fillColor=colors.black))

    # recibimos de
    pdf.drawString(50, 650, 'RECIBIMOS DE:')
    pdf.line(192, 649, 450, 649)
    lienzo.add(String(147, 50, f'{pago.alumno.nombres} {pago.alumno.apellidos}', fontName='Helvetica', fontSize=12, fillColor=colors.black))

    # la suma de
    pdf.drawString(50, 620, 'LA SUMA DE:')
    pdf.line(192, 619, 450, 619)
    lienzo.add(String(147, 20, str(num2words(pago.monto, to='currency', lang='es_NI')).capitalize(), fontName='Helvetica', fontSize=12, fillColor=colors.black))

    # tabla del pago
    headers = ['MATRICULA DE'if tipo_pago_efectuado == 'matricula' else "MENSUALIDAD DE" , 'HORARIO', 'DEBE', 'IMPORTE']
    horario = f'{tipo_turno.dias} de {tipo_turno.hora_entrada}-{tipo_turno.hora_salida} {tipo_turno.formato}'
    values = [pago.fecha.strftime("%B %Y"), horario, '', f'C$ {pago.monto}']
    footer = ['EFECTIVO - CAJA', 'VALOR', '', f'C$ {pago.monto}']
    data = [headers, values, footer]

    table = Table(data, colWidths=[1.6*inch, 3*inch, 1*inch, 1.5*inch])
    # (columna, fila)
    table.setStyle(TableStyle([
    ('GRID',(0,0), (-1,-2), 0.5, colors.black),
    ('FONTNAME', (0,0), (3,0), 'Helvetica-Bold'),
    ('BACKGROUND',(0,0), (3,0), colors.lightgrey),
    ('ALIGN', (1,0), (3,0), 'CENTER'),
    ('LINEABOVE', (0,0), (-1,0), 1, colors.black),
    ('LINEABOVE', (0,1), (-1,-2), 0.25, colors.black),
    ('LINEBELOW', (0,-1), (-1,-2), 1, colors.black),
    ('ALIGN', (1,1), (-1,-2), 'LEFT'),
    ('ALIGN', (3,1), (-1,-2), 'RIGHT'),
    ('ALIGN', (-3,-1), (-1,-1), 'RIGHT'),
    ('GRID',(-2,-1), (-1,-1), 0.5, colors.black),
    ('FONTNAME', (-4,-1), (-3,-1), 'Helvetica-Bold'),
    ('LEFTPADDING', (-4,-1), (-4,-1), 2),
    ]))
    width=600
    height=560
    table.wrapOn(pdf, width, height)
    table.drawOn(pdf, 50, height - len(data))

    # cajero(a)
    pdf.drawString(52, 530, 'CAJERO(A):')
    pdf.line(130, 529, 350, 529)
    lienzo.add(String(85, -70, 'Howard Ramos', fontName='Helvetica', fontSize=12, fillColor=colors.black))

    # firma
    pdf.drawString(290, 480, 'FIRMA')

    # render lienzo
    lienzo.drawOn(pdf, 50, 600)

    pdf.save()
    return response

# 3. REPORTE IA PDF PROFESIONAL
@login_required(login_url='signin')
def reporte_ia_pdf(request):
    """
    Genera Reporte Ejecutivo con diseño profesional y LISTAS DE ALUMNOS.
    """
    # 1. Obtener Datos
    monto_ia, mes_ia, conf_ia = predecir_ingresos_prophet()
    pico_ia, bajo_ia = analizar_matricula_prophet()
    riesgo_mes_ia, riesgo_det_ia = analizar_riesgo_morosidad()
    clustering = segmentar_clientes_kmeans()
    
    # Datos Reales para justificación
    promedio_real = Pago.objects.aggregate(Avg('monto'))['monto__avg'] or 0

    # 2. Configurar PDF
    response = HttpResponse(content_type='application/pdf')
    filename = f"Reporte_Inteligente_{date.today()}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilos
    estilo_titulo = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=20, textColor=colors.darkblue, alignment=1, spaceAfter=20)
    estilo_seccion = ParagraphStyle('Sec', parent=styles['Heading2'], fontSize=14, textColor=colors.darkblue, spaceBefore=15)
    estilo_normal = styles['Normal']

    # --- CONTENIDO ---
    elements.append(Paragraph("Howard Bilingual School", estilo_titulo))
    elements.append(Paragraph(f"Reporte de Inteligencia de Negocios - {date.today().strftime('%d/%m/%Y')}", styles['Heading3']))
    elements.append(Spacer(1, 10))

    # A. FINANZAS
    elements.append(Paragraph("1. Proyección Financiera (Próximo Mes)", estilo_seccion))
    data_finanzas = [
        ['Concepto', 'Predicción IA', 'Dato Histórico (Contexto)'],
        [f'Ingreso {mes_ia}', f'C$ {monto_ia:,.2f}', f'Promedio real: C$ {promedio_real:,.2f}'],
        ['Confianza', f'{conf_ia}%', 'Basado en histórico 2024-2025']
    ]
    t1 = Table(data_finanzas, colWidths=[150, 120, 200])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(t1)

    # B. MAPA DE CALOR (CLIENTES)
    elements.append(Paragraph("2. Semáforo de Comportamiento de Pago", estilo_seccion))
    if clustering:
        data_cluster = [
            ['Perfil', 'Cantidad', 'Estrategia Sugerida'],
            ['💎 Premium (Puntuales)', str(clustering['premium']['cantidad']), 'Fidelizar / Beca Honorífica'],
            ['✅ Estándar (Normal)', str(clustering['estandar']['cantidad']), 'Seguimiento regular'],
            ['🚨 Riesgo (Morosos)', str(clustering['riesgo']['cantidad']), 'Gestión de Cobro Inmediata']
        ]
        t2 = Table(data_cluster, colWidths=[150, 80, 240])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('TEXTCOLOR', (0, 3), (-1, 3), colors.red), # Rojo para riesgo
        ]))
        elements.append(t2)

    # C. DETALLE NOMINAL (LISTAS)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("3. Detalle de Alumnos en Riesgo (Acción Requerida)", estilo_seccion))
    
    if clustering and clustering['riesgo']['cantidad'] > 0:
        # Convertir tuplas a lista de listas para la tabla
        lista_riesgo = [['Nombre del Estudiante', 'Apellido']]
        # Limitamos a los primeros 15 para que quepan en la hoja (o pon todos si quieres)
        for nombre, apellido in clustering['riesgo']['lista'][:20]: 
            lista_riesgo.append([nombre, apellido])
        
        t_riesgo = Table(lista_riesgo, colWidths=[200, 200])
        t_riesgo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.firebrick),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        elements.append(t_riesgo)
        if clustering['riesgo']['cantidad'] > 20:
            elements.append(Paragraph(f"... y {clustering['riesgo']['cantidad'] - 20} más.", styles['Italic']))
    else:
        elements.append(Paragraph("No se detectaron alumnos en el perfil de riesgo.", styles['Normal']))

    # PIE
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("Reporte generado automáticamente por Howard Web System.", styles['Italic']))

    doc.build(elements)
    return response

# reportes endpoints
def reportes(request):
    search_query = request.GET.get('search', '')
    search_pagos_query = request.GET.get('search_pagos', '')
    logs_page_number = request.GET.get('logs_page', 1)  # Captura la página de logs
    pagos_page_number = request.GET.get('pagos_page', 1)  # Captura la página de pagos
    page_size = request.GET.get('page_size', 10)

    try:
        logs_page_number = int(logs_page_number)
    except ValueError:
        logs_page_number = 1

    try:
        pagos_page_number = int(pagos_page_number)
    except ValueError:
        pagos_page_number = 1

    try:
        page_size = int(page_size)
    except ValueError:
        page_size = 10

    logs = LogEntry.objects.select_related('content_type', 'user').all().order_by('-action_time')
    pagos = Pago.objects.all().order_by('-fecha')
    total_alumnos = Alumno.objects.count()
    total_profesores = Profesor.objects.count()
    total_grupos = Grupo.objects.count()
    total_pagos = Pago.objects.count()
    pagos_fecha = Pago.objects.values('fecha__year','fecha__month').annotate(total=models.Sum('monto')).order_by('fecha__year', 'fecha__month')

    if search_query:
        logs = logs.filter(
            models.Q(user__username__icontains=search_query) |
            models.Q(content_type__model__icontains=search_query) |
            models.Q(object_repr__icontains=search_query)
        )

    if search_pagos_query:
        pagos_fecha = pagos_fecha.filter(
            models.Q(fecha__year__icontains=search_pagos_query) |
            models.Q(fecha__month__icontains=search_pagos_query)
        )

    paginator_logs = Paginator(logs, page_size)  # Mostrar `page_size` logs por página
    paginator_pagos = Paginator(pagos_fecha, page_size)  # Mostrar `page_size` pagos por página

    try:
        logs_page = paginator_logs.page(logs_page_number)
    except PageNotAnInteger:
        logs_page = paginator_logs.page(1)
    except EmptyPage:
        logs_page = paginator_logs.page(paginator_logs.num_pages)

    try:
        pagos_page = paginator_pagos.page(pagos_page_number)
    except PageNotAnInteger:
        pagos_page = paginator_pagos.page(1)
    except EmptyPage:
        pagos_page = paginator_pagos.page(paginator_pagos.num_pages)

    # Preparar datos para la gráfica
    meses = []
    totales = []
    for pago in pagos_fecha:
        meses.append(f"{pago['fecha__year']}-{pago['fecha__month']:02d}")
        totales.append(int(pago['total']))

    context = {
        'logs': logs_page,
        'pagos': pagos_page,
        'total_alumnos': total_alumnos,
        'total_profesores': total_profesores,
        'total_grupos': total_grupos,
        'total_pagos': total_pagos,
        'pagos_fecha': pagos_fecha,
        'ADDITION': ADDITION,
        'CHANGE': CHANGE,
        'DELETION': DELETION,
        'search_query': search_query,
        'search_pagos_query': search_pagos_query,
        'meses': dumps(meses),
        'totales': dumps(totales),
    }
    return render(request, 'utilidades/reportes.html', context)

#view perfil
@login_required(login_url='signin')
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            update_session_auth_hash(request, request.user)  # Mantiene al usuario autenticado después de cambiar la contraseña
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
    context = {
        'u_form': u_form
    }
    return render(request, 'profile/profile.html', context)

@login_required(login_url='signin')
def account_settings(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, '¡La información de la cuenta se ha actualizado con éxito!')
            return redirect('account_settings')
    else:
        u_form = UserUpdateForm(instance=request.user)

    password_change_form = CustomPasswordChangeForm(user=request.user)

    context = {
        'u_form': u_form,
        'password_change_form': password_change_form,
    }
    return render(request, 'profile/account_settings.html', context)

@login_required(login_url='signin')
def update_profile_picture(request):
    if request.method == 'POST':
        p_form = ProfilePictureForm(request.POST, request.FILES, instance=request.user)
        if p_form.is_valid():
            p_form.save()
            messages.success(request, '¡La foto de perfil se ha actualizado con éxito!')
            return redirect('account_settings')
    else:
        p_form = ProfilePictureForm(instance=request.user)

    context = {
        'p_form': p_form,
    }
    return render(request, 'profile/update_profile_picture.html', context)

@login_required(login_url='signin')
def change_password(request):
    if request.method == 'POST':
        password_change_form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if password_change_form.is_valid():
            user = password_change_form.save()
            update_session_auth_hash(request, user)  # Important, to update the session with the new password
            messages.success(request, '¡La contraseña se ha cambiado con éxito!')
            return redirect('account_settings')
        else:
            messages.error(request, 'La contraseña no cumple con los requisitos.')
    else:
        password_change_form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'profile/account_settings.html', {
        'password_change_form': password_change_form,
    })

@login_required(login_url='signin')
def delete_profile_picture(request):
    if request.method == 'POST':
        user = request.user
        user.profile_picture.delete(save=False)
        user.profile_picture = 'default_profile_picture.jpg'
        user.save()
        messages.success(request, '¡La foto de perfil se ha eliminado con éxito!')
        return redirect('account_settings')

#register profile view
@login_required(login_url='signin')
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.is_superuser = True
            user.is_staff = True
            if 'profile_picture' in request.FILES:
                user.profile_picture = request.FILES['profile_picture']
            user.save()
            messages.success(request, '¡Usuario creado con éxito!')
            return redirect('register')
        else:
            messages.error(request, 'Por favor, corrija los errores.')
    else:
        form = UserRegisterForm()
    return render(request, 'profile/register.html', {'form': form})

# --- LAS FUNCIONES QUE TE FALTABAN AL FINAL ---

# splash screen
def splash_screen(request):
    if request.session.get('splash_seen', False):
        return redirect('dashboard')  
    request.session['splash_seen'] = True
    return render(request, 'splash.html')

# revision de pago
def alumno_detalle(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id)
    tipo_mensualidad = TipoPago.objects.get(nombre="Mensualidad")
    ultimo_pago_mensualidad = Pago.objects.filter(alumno=alumno, tipo_pago=tipo_mensualidad).order_by('-fecha').first()
    hoy = date.today()

    if ultimo_pago_mensualidad:
        proximo_pago = ultimo_pago_mensualidad.fecha + timedelta(days=30)
        dias_restantes = (proximo_pago - hoy).days
    else:
        proximo_pago = None
        dias_restantes = None

    context = {
        'alumno': alumno,
        'ultimo_pago_mensualidad': ultimo_pago_mensualidad,
        'proximo_pago': proximo_pago,
        'dias_restantes': dias_restantes
    }
    return render(request, 'alumno_detalle.html', context)