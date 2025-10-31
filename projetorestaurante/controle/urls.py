# controle/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.controle, name='controle'),
    path('proximo/<int:id>/', views.proximo, name='proximo'),
]
    