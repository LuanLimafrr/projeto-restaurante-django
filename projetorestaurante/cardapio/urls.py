# Arquivo: cardapio/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # View Pública
    path('', views.exibir_cardapio, name='cardapio'),

    # Gerenciamento Staff
    path('gerenciar/', views.listar_cardapio_admin, name='gerenciar_cardapio'),

    path('categoria/adicionar/', views.adicionar_categoria, name='adicionar_categoria'),
    path('categoria/editar/<int:id>/', views.editar_categoria, name='editar_categoria'),
    path('categoria/deletar/<int:id>/', views.deletar_categoria, name='deletar_categoria'),

    path('item/adicionar/', views.adicionar_item, name='adicionar_item'),
    path('item/editar/<int:id>/', views.editar_item, name='editar_item'),
    path('item/deletar/<int:id>/', views.deletar_item, name='deletar_item'),

    # --- NOVAS URLS ADICIONADAS ---
    path('item/atualizar_preco/<int:id>/', views.atualizar_preco_item, name='atualizar_preco_item'),
    path('item/toggle_ativo/<int:id>/', views.toggle_ativo_item, name='toggle_ativo_item'),
]