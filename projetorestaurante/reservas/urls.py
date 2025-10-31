# Arquivo: reservas/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Mantém a URL da página de reserva separada (se quiser)
    path('', views.fazer_reserva, name='fazer_reserva'),

    # --- NOVA URL ADICIONADA (PARA O MODAL) ---
    path('modal/', views.fazer_reserva_modal, name='fazer_reserva_modal'),

    # URLs de Gerenciamento e Histórico
    path('gerenciar/', views.gerenciar_reservas, name='gerenciar_reservas'),
    path('historico/', views.historico_reservas, name='historico_reservas'),

    # URLs de Ação
    path('confirmar/<int:id>/', views.confirmar_reserva, name='confirmar_reserva'),
    path('cancelar/<int:id>/', views.cancelar_reserva, name='cancelar_reserva'),
]