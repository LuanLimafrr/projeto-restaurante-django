# Arquivo: estoque/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.gerenciar_estoque, name='gerenciar_estoque'),
    path('adicionar/<int:id_item>/', views.adicionar_estoque_item, name='adicionar_estoque_item'),
    
    # --- NOVA URL ADICIONADA ---
    path('criar-novo-item/', views.criar_novo_item_estoque, name='criar_novo_item_estoque'),
]