# Arquivo: fila/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('fila/', views.pagina_fila, name='pagina_fila'),
    path('sair-da-fila/', views.sair_da_fila_cliente, name='sair_da_fila_cliente'),
    path('checar-posicao/', views.checar_posicao, name='checar_posicao'),
    path('entrar-fila-modal/', views.entrar_na_fila_modal, name='entrar_na_fila_modal'),

    # URLs de Gerenciamento da Fila (Staff)
    path('gerenciar/', views.gerenciar_fila, name='gerenciar_fila'),
    
    path('remover/<int:id>/', views.remover_cliente, name='remover_cliente'),
    path('marcar-desistente/<int:id>/', views.marcar_como_desistente, name='marcar_como_desistente'),
]