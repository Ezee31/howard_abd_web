from django.urls import path
from . import views

urlpatterns = [
  path("", views.signin, name="signin"),
  path("dashboard", views.dashboard, name="dashboard"),
  path("tipo_turno", views.tipo_turno, name="tipo_turno"),
  path("tipo_turno/<int:id>", views.tipo_turno, name="tipo_turno_edit"),
  path("tipo_turno_delete/<int:id>", views.tipo_turno_delete, name="tipo_turno_delete"),
  path("horario", views.horario, name="horario"),
  path("horario/<int:id>", views.horario, name="horario_edit"),
  path("horario_delete/<int:id>", views.horario_delete, name="horario_delete"),
  path("profesor", views.profesor, name="profesor"),
  path("profesor/<int:id>", views.profesor, name="profesor_edit"),
  path("profesor_delete/<int:id>", views.profesor_delete, name="profesor_delete"),
  path("tipo_pago", views.tipo_pago, name="tipo_pago"),  
  path("tipo_pago/<int:id>", views.tipo_pago, name="tipo_pago_edit"), 
  path("tipo_pago_delete/<int:id>", views.tipo_pago_delete, name="tipo_pago_delete"),
  path("grupo", views.grupo, name="grupo"),  
  path("grupo/<int:id>", views.grupo, name="grupo_edit"), 
  path("grupo_delete/<int:id>", views.grupo_delete, name="grupo_delete"),
]