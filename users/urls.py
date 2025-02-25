from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic.base import RedirectView
from . import views  # Import your custom views

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),
    path("accounts/profile/", RedirectView.as_view(url="/", permanent=True), name="redirect_home"),
]
