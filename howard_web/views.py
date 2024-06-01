from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import LoginForm
from django.contrib.auth import authenticate, login

# Create your views here. 

def home(request): 
    return render(request,"home.html")

#Login
#@login_required(login_url='login')
def signin(request):
    if request.method == "GET":
        return render(request,"login/index.html")
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
        else:
            new_login_form = LoginForm()
            return render(request, "login/index.html", {'form': new_login_form})

def dashboard(request):
    return render(request,"dashboard/index.html")



     