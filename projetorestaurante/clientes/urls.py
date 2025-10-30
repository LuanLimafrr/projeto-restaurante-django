from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),            # Lista de espera cliente
    path('salvar/', views.salvar, name='salvar'), # Formulário POST
    path('delete/<int:id>/', views.delete, name='delete'),
    path('posicao/<int:id>/', views.posicao, name='posicao'),

]
