from django.urls import path
from . import views

urlpatterns = [
  path("", views.signin, name="signin"),
  #path("login", views.login, name="login"),
  path("dashboard", views.dashboard, name="dashboard")
]