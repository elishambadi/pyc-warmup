from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages

from django.contrib.auth.models import User

from .forms import RegisterForm

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']

            if password1 == password2:
                user = User.objects.create_user(username=username, email=email, password=password1)
                login(request, user)
                return redirect("home")
            else:
                form.add_error('password2', 'Passwords do not match')
    else:
        form = RegisterForm()

    return render(request, "registration/register.html", {"form": form})