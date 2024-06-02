from django.urls import path
from . import views

urlpatterns = [
  path("", views.signin, name="signin"),
  path("dashboard", views.dashboard, name="dashboard"),
  path("tipo_turno", views.tipo_turno, name="tipo_turno"),
  path("tipo_turno/<int:id>", views.tipo_turno, name="tipo_turno_edit"),
  path("tipo_turno_delete/<int:id>", views.tipo_turno_delete, name="tipo_turno_delete"),
]