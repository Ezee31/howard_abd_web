from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
  # Authentication views
  path("", views.signin, name="signin"),
  path("dashboard", views.dashboard, name="dashboard"),

  # TipoTurno views
  path('tipo_turno', views.tipo_turno, name='tipo_turno'),
  path('tipo_turno_add/', views.tipo_turno_add, name='tipo_turno_add'),
  path('tipo_turno_edit/<int:id>/', views.tipo_turno_edit, name='tipo_turno_edit'),
  path('tipo_turno_delete/<int:id>/', views.tipo_turno_delete, name='tipo_turno_delete'),

  # Horario views
  path('horario', views.horario, name="horario"),
  path('horario_add/', views.horario_add, name="horario_add"),
  path('horario_edit/<int:id>/', views.horario_edit, name="horario_edit"),
  path('horario_delete/<int:id>/', views.horario_delete, name="horario_delete"),

  # Profesor views
  path('profesor', views.profesor, name='profesor'),
  path('profesor_add/', views.profesor_add, name='profesor_add'),
  path('profesor_edit/<int:id>/', views.profesor_edit, name='profesor_edit'),
  path('profesor_delete/<int:id>/', views.profesor_delete, name='profesor_delete'),
  
  # TipoPago views
  path('tipo_pago', views.tipo_pago, name='tipo_pago'),
  path('tipo_pago_add/', views.tipo_pago_add, name='tipo_pago_add'),
  path('tipo_pago_edit/<int:id>/', views.tipo_pago_edit, name='tipo_pago_edit'),
  path('tipo_pago_delete/<int:id>/', views.tipo_pago_delete, name='tipo_pago_delete'),


  # Grupo views
  path('grupo', views.grupo, name='grupo'),
  path('grupo_add/', views.grupo_add, name='grupo_add'),
  path('grupo_edit/<int:id>/', views.grupo_edit, name='grupo_edit'),
  path('grupo_delete/<int:id>/', views.grupo_delete, name='grupo_delete'),

  # Alumno views
  path('alumno', views.alumno, name='alumno'),
  path('alumno_add/', views.alumno_add, name='alumno_add'),
  path('alumno_edit/<int:id>/', views.alumno_edit, name='alumno_edit'),
  path('alumno_delete/<int:id>/', views.alumno_delete, name='alumno_delete'),

  # Pago views
  path('pago', views.pago, name='pago'),
  path('pago_add/', views.pago_add, name='pago_add'),
  path('pago_edit/<int:id>/', views.pago_edit, name='pago_edit'),
  path('pago_delete/<int:id>/', views.pago_delete, name='pago_delete'),

  # Logout view
  path("logout/", LogoutView.as_view(next_page='signin'), name="logout"),
  
  # Reportes view
 path("reportes", views.reportes, name="reportes"),
]