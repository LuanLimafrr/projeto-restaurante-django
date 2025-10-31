# /projetorestaurante/reservas/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # URL para o cliente fazer uma reserva (página principal)
    path('fazer/', views.fazer_reserva, name='fazer_reserva'),
    # URL para o cliente fazer uma reserva (via modal, se for uma view separada)
    path('fazer_modal/', views.fazer_reserva_modal, name='fazer_reserva_modal'),

    # URL para o cliente ver seu histórico de reservas
    path('historico/', views.historico_reservas, name='historico_reservas'),

    # URL para o staff gerenciar as reservas
    path('gerenciar/', views.gerenciar_reservas, name='gerenciar_reservas'),
    path('confirmar/<int:id>/', views.confirmar_reserva, name='confirmar_reserva'),
    path('cancelar/<int:id>/', views.cancelar_reserva, name='cancelar_reserva'),

    # URL para o staff ver o histórico completo (incluindo canceladas e passadas)
    # Se você tiver uma view separada para isso. Se não, gerenciar_reservas já faz o trabalho.
    # path('historico-staff/', views.historico_reservas_staff, name='historico_reservas_staff'),
    # Assumi que 'historico_reservas_staff' aponta para a mesma view que 'gerenciar_reservas' ou uma similar
    # Se você não tem 'historico_reservas_staff', o link no gerenciar.html deveria apontar para 'gerenciar_reservas'
]