# Arquivo: comandas/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # URL do Gerente (PDV Completo)
    path('', views.mapa_mesas, name='mapa_mesas'), 
    
    # --- NOVA URL PARA RECEPCIONISTA ---
    path('alocar/<int:id_cliente>/', views.mapa_mesas_recepcao, name='mapa_mesas_recepcao'),
    
    # URL de Ação (que ambos usam)
    path('processar-alocacao/<int:id_mesa>/<int:id_cliente>/', views.processar_alocacao_cliente, name='processar_alocacao_cliente'),

    # URLs de Gerente
    path('mesa/<int:id_mesa>/', views.detalhe_comanda, name='detalhe_comanda'),
    path('fechar/<int:id_comanda>/', views.fechar_comanda, name='fechar_comanda'),
    path('item/remover/<int:id_item>/', views.remover_item_comanda, name='remover_item_comanda'),
    path('taxa/toggle/<int:id_comanda>/', views.toggle_taxa_servico, name='toggle_taxa_servico'),
    path('pagamento/confirmar/<int:id_comanda>/', views.confirmar_pagamento, name='confirmar_pagamento'),
    path('item/aumentar/<int:id_item>/', views.aumentar_quantidade_item, name='aumentar_quantidade_item'),
    path('item/diminuir/<int:id_item>/', views.diminuir_quantidade_item, name='diminuir_quantidade_item'),
    path('relatorio/diario/', views.relatorio_diario, name='relatorio_diario'),
]