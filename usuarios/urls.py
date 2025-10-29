# Arquivo: usuarios/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views # Views padrão

urlpatterns = [
    path('registrar/', views.registrar, name='registrar'),
    path('perfil/', views.perfil, name='perfil'),

    # --- LOGIN UNIFICADO ---
    path('login/', views.CustomLoginViewUnificada.as_view(), name='login'),

    # --- LOGOUT PADRÃO ---
    # Usa a LogoutView padrão do Django. Redireciona para LOGOUT_REDIRECT_URL ('inicio')
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]