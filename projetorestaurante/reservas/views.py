# /projetorestaurante/reservas/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Reserva
from .forms import ReservaForm
from django.utils import timezone
from django.conf import settings
import requests
import os
from django.contrib.auth.models import User
from cardapio.views import is_staff_user # Assumindo que sua função 'is_staff' está aqui

# --- FUNÇÃO DE EMAIL REESCRITA PARA USAR A API WEB DO SENDGRID ---
def enviar_email_status_reserva(request, reserva):
    api_key = os.environ.get('EMAIL_HOST_PASSWORD')
    from_email = os.environ.get('DEFAULT_FROM_EMAIL')

    if not api_key or not from_email:
        print("ERRO DE DEPLOY: API Key do SendGrid ou E-mail de Remetente não configurado.")
        if request.user.is_staff:
            messages.warning(request, "Configuração de e-mail incompleta no servidor.")
        return

    status_map = {
        'CONFIRMADA': 'Confirmada',
        'CANCELADA': 'Cancelada',
        'PENDENTE': 'Pendente',
    }
    status_amigavel = status_map.get(reserva.status, reserva.status)
    assunto = f"Sua reserva no Chama do Cerrado foi {status_amigavel}!"
    
    nome_usuario = reserva.usuario.get_full_name() or reserva.usuario.username
    mensagem_html = f"""
    <html>
    <body>
        <h3>Olá, {nome_usuario}!</h3>
        <p>O status da sua reserva no Chama do Cerrado foi atualizado:</p>
        <hr>
        <p><strong>Status:</strong> {status_amigavel}</p>
        <p><strong>Data:</strong> {reserva.data.strftime('%d/%m/%Y')}</p>
        <p><strong>Hora:</strong> {reserva.hora.strftime('%H:%M')}</p>
        <p><strong>Pessoas:</strong> {reserva.numero_pessoas}</p>
        <hr>
        <p>Obrigado por escolher o Chama do Cerrado!</p>
    </body>
    </html>
    """
    
    data = {
        "personalizations": [{
            "to": [{"email": reserva.usuario.email}],
            "subject": assunto
        }],
        "from": {"email": from_email, "name": "Chama do Cerrado"},
        "content": [{
            "type": "text/html",
            "value": mensagem_html
        }]
    }

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post('https://api.sendgrid.com/v3/mail/send', headers=headers, json=data, timeout=10)
        
        if response.status_code == 202:
            print(f"E-mail de {status_amigavel} enviado para {reserva.usuario.email}.")
        else:
            print(f"Erro ao enviar email via SendGrid API: {response.status_code} - {response.text}")
            if request.user.is_staff:
                messages.warning(request, f"Reserva salva, mas houve um erro ao enviar o e-mail (API SendGrid: {response.status_code}).")
    
    except requests.exceptions.RequestException as e:
        print(f"Erro de rede ao conectar com SendGrid API: {e}")
        if request.user.is_staff:
            messages.warning(request, "Reserva salva, mas o serviço de e-mail demorou a responder.")


# --- VIEW FAZER RESERVA (PÁGINA PRINCIPAL) ---
@login_required
def fazer_reserva(request):
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.usuario = request.user
            reserva.status = 'PENDENTE'
            reserva.save()
            messages.success(request, 'Sua reserva foi criada com sucesso! Aguardando confirmação.')
            # AQUI: Redireciona para o histórico de reservas do CLIENTE
            return redirect('historico_reservas')
        else:
            messages.error(request, 'Erro ao criar a reserva. Por favor, verifique os dados.')
    else:
        form = ReservaForm()
    return render(request, 'reservas/fazer_reserva.html', {'form': form})

# --- VIEW FAZER RESERVA (MODAL) ---
@login_required
def fazer_reserva_modal(request):
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.usuario = request.user
            reserva.status = 'PENDENTE'
            reserva.save()
            messages.success(request, 'Sua reserva foi criada com sucesso (via modal)!')
            # AQUI: Redireciona para o histórico de reservas do CLIENTE
            return redirect('historico_reservas')
        else:
            messages.error(request, 'Erro ao criar a reserva via modal. Por favor, verifique os dados.')
            form = ReservaForm(request.POST)
    else:
        form = ReservaForm()
    return render(request, 'reservas/fazer_reserva_modal.html', {'form': form})

# --- VIEW HISTÓRICO DE RESERVAS (PARA O CLIENTE) ---
@login_required
def historico_reservas(request):
    reservas = Reserva.objects.filter(usuario=request.user).order_by('-data', '-hora')
    # AJUSTADO: Usa o nome do arquivo correto `historico.html`
    return render(request, 'reservas/historico.html', {'reservas': reservas})

# --- VIEW GERENCIAR RESERVAS (PARA O STAFF - ATUAIS/PENDENTES) ---
@login_required
@user_passes_test(is_staff_user)
def gerenciar_reservas(request):
    reservas_pendentes = Reserva.objects.filter(status='PENDENTE').order_by('data', 'hora')
    reservas_confirmadas = Reserva.objects.filter(status='CONFIRMADA', data__gte=timezone.now().date()).order_by('data', 'hora')
    
    context = {
        'reservas_pendentes': reservas_pendentes,
        'reservas_confirmadas': reservas_confirmadas,
    }
    # AJUSTADO: Usa o nome do arquivo correto `gerenciar.html`
    return render(request, 'reservas/gerenciar.html', context)

# --- NOVA VIEW HISTÓRICO GERAL DE RESERVAS (PARA O STAFF) ---
@login_required
@user_passes_test(is_staff_user)
def historico_geral_reservas_staff(request):
    # Para o staff, mostra todas as reservas, incluindo canceladas e passadas.
    reservas = Reserva.objects.all().order_by('-data', '-hora')
    return render(request, 'reservas/historico_geral_staff.html', {'reservas': reservas})


# --- VIEW CONFIRMAR RESERVA (PARA O STAFF) ---
@login_required
@user_passes_test(is_staff_user)
def confirmar_reserva(request, id):
    reserva = get_object_or_404(Reserva, id=id)
    reserva.status = 'CONFIRMADA'
    reserva.save()
    messages.success(request, f"Reserva de {reserva.usuario.get_full_name()} confirmada!")
    enviar_email_status_reserva(request, reserva) 
    return redirect('gerenciar_reservas')

# --- VIEW CANCELAR RESERVA (PARA O STAFF) ---
@login_required
@user_passes_test(is_staff_user)
def cancelar_reserva(request, id):
    reserva = get_object_or_404(Reserva, id=id)
    reserva.status = 'CANCELADA'
    reserva.save()
    messages.warning(request, f"Reserva de {reserva.usuario.get_full_name()} foi cancelada.")
    enviar_email_status_reserva(request, reserva) 
    return redirect('gerenciar_reservas')