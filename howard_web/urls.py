from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
  # Authentication views
  path("", views.signin, name="signin"),
  path("dashboard", views.dashboard, name="dashboard"),

  # TipoTurno views
  path("tipo_turno", views.tipo_turno, name="tipo_turno"),
  path("tipo_turno/<int:id>", views.tipo_turno, name="tipo_turno_edit"),
  path("tipo_turno_delete/<int:id>", views.tipo_turno_delete, name="tipo_turno_delete"),

  # Horario views
  path("horario", views.horario, name="horario"),
  path("horario/<int:id>", views.horario, name="horario_edit"),
  path("horario_delete/<int:id>", views.horario_delete, name="horario_delete"),

  # Profesor views
  path("profesor", views.profesor, name="profesor"),
  path("profesor/<int:id>", views.profesor, name="profesor_edit"),
  path("profesor_delete/<int:id>", views.profesor_delete, name="profesor_delete"),

  # TipoPago views
  path("tipo_pago", views.tipo_pago, name="tipo_pago"),
  path("tipo_pago/<int:id>", views.tipo_pago, name="tipo_pago_edit"),
  path("tipo_pago_delete/<int:id>", views.tipo_pago_delete, name="tipo_pago_delete"),

  # Grupo views
  path("grupo", views.grupo, name="grupo"),
  path("grupo/<int:id>", views.grupo, name="grupo_edit"),
  path("grupo_delete/<int:id>", views.grupo_delete, name="grupo_delete"),

  # Alumno views
  path("alumno", views.alumno, name="alumno"),
  path("alumno/<int:id>", views.alumno, name="alumno_edit"),
  path("alumno_delete/<int:id>", views.alumno_delete, name="alumno_delete"),

  # Pago views
  path("pago", views.pago, name="pago"),
  path("pago/<int:id>", views.pago, name="pago_edit"),
  path("pago_delete/<int:id>", views.pago_delete, name="pago_delete"),

  # Logout view
  path("logout/", LogoutView.as_view(next_page='signin'), name="logout"),

]