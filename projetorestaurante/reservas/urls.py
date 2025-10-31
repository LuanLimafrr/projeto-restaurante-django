# /projetorestaurante/reservas/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # URLs para Clientes
    path('fazer/', views.fazer_reserva, name='fazer_reserva'),
    path('fazer_modal/', views.fazer_reserva_modal, name='fazer_reserva_modal'),
    path('historico/', views.historico_reservas, name='historico_reservas'), # O cliente verá o próprio histórico

    # URLs para Staff (Administradores)
    path('gerenciar/', views.gerenciar_reservas, name='gerenciar_reservas'), # Staff gerencia todas as reservas
    path('confirmar/<int:id>/', views.confirmar_reserva, name='confirmar_reserva'),
    path('cancelar/<int:id>/', views.cancelar_reserva, name='cancelar_reserva'),
    # Nova URL para o histórico geral do staff (inclui canceladas e passadas)
    path('historico-staff/', views.historico_geral_reservas_staff, name='historico_geral_reservas_staff'),
]