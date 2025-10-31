# /projetorestaurante/reservas/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Reserva
from .forms import ReservaForm
from django.utils import timezone
from django.conf import settings
# from django.core.mail import send_mail  <-- REMOVIDO (Não usamos mais)
# from django.template.loader import render_to_string <-- REMOVIDO
from django.contrib.auth.models import User
from cardapio.views import is_staff_user # Assumindo que sua função 'is_staff' está aqui

# --- NOVAS IMPORTAÇÕES ---
import requests
import os
# --- FIM DAS NOVAS IMPORTAÇÕES ---


# Função para checar se é staff (você já deve ter uma parecida)
# SE a função 'is_staff_user' (importada de cardapio.views) NÃO funcionar,
# descomente a linha abaixo para definir 'is_staff' localmente.
# def is_staff(user):
#    return user.is_staff

# --- FUNÇÃO DE EMAIL REESCRITA PARA USAR A API WEB DO SENDGRID ---
def enviar_email_status_reserva(request, reserva):
    # Vamos ler a API Key e o email de remetente das variáveis de ambiente
    # que JÁ configuramos no Render
    api_key = os.environ.get('EMAIL_HOST_PASSWORD')
    from_email = os.environ.get('DEFAULT_FROM_EMAIL')

    if not api_key or not from_email:
        # Se as variáveis não estiverem configuradas, apenas loga o erro no console
        print("ERRO DE DEPLOY: API Key do SendGrid ou E-mail de Remetente não configurado.")
        # Adiciona uma mensagem para o staff, mas não para o usuário
        if request.user.is_staff:
            messages.warning(request, "Configuração de e-mail incompleta no servidor.")
        return # Sai da função sem travar

    status_map = {
        'CONFIRMADA': 'Confirmada',
        'CANCELADA': 'Cancelada',
        'PENDENTE': 'Pendente',
    }
    status_amigavel = status_map.get(reserva.status, reserva.status)
    assunto = f"Sua reserva no Chama do Cerrado foi {status_amigavel}!"
    
    # Mensagem em HTML (mais bonito)
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
    
    # Payload da API SendGrid v3
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

    # Tenta enviar o e-mail via API
    try:
        # IMPORTANTE: Definir um timeout de 10s (o Gunicorn é 30s)
        response = requests.post('https://api.sendgrid.com/v3/mail/send', headers=headers, json=data, timeout=10)
        
        # Verifica se a API do SendGrid aceitou
        if response.status_code == 202: # 202 Accepted é o sucesso do SendGrid
            # Não precisamos de mensagem de sucesso aqui, a view principal já faz isso.
            print(f"E-mail de {status_amigavel} enviado para {reserva.usuario.email}.")
        else:
            # Se o SendGrid der erro, informa o admin e loga o erro
            print(f"Erro ao enviar email via SendGrid API: {response.status_code} - {response.text}")
            if request.user.is_staff:
                messages.warning(request, f"Reserva salva, mas houve um erro ao enviar o e-mail (API SendGrid: {response.status_code}).")
    
    except requests.exceptions.RequestException as e:
        # Se houver um erro de rede (como timeout da nossa requisição)
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
            reserva.status = 'PENDENTE' # Ou outro status inicial
            reserva.save()
            messages.success(request, 'Sua reserva foi criada com sucesso! Aguardando confirmação.')
            # enviar_email_status_reserva(request, reserva) # Descomente se quiser enviar e-mail de "Pendente"
            return redirect('historico_reservas') # Redireciona para o histórico
        else:
            messages.error(request, 'Erro ao criar a reserva. Por favor, verifique os dados.')
    else:
        form = ReservaForm()
    
    # Renderiza o template 'reservas/fazer_reserva.html'
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
            # enviar_email_status_reserva(request, reserva) # Descomente se quiser enviar e-mail de "Pendente"
            return redirect('historico_reservas') # Redireciona para o histórico
        else:
            messages.error(request, 'Erro ao criar a reserva via modal. Por favor, verifique os dados.')
            form = ReservaForm(request.POST) # Re-instancia o form para mostrar erros
    else:
        form = ReservaForm()
    
    # Renderiza o template 'reservas/fazer_reserva_modal.html' (ou o que você usar)
    return render(request, 'reservas/fazer_reserva_modal.html', {'form': form})

# --- VIEW HISTÓRICO DE RESERVAS (PARA O USUÁRIO) ---
@login_required
def historico_reservas(request):
    reservas = Reserva.objects.filter(usuario=request.user).order_by('-data', '-hora')
    return render(request, 'reservas/historico_reservas.html', {'reservas': reservas})

# --- VIEW GERENCIAR RESERVAS (PARA O STAFF) ---
@login_required
@user_passes_test(is_staff_user) # Usa a função de staff importada
def gerenciar_reservas(request):
    # Pegando todas as reservas e separando por status
    reservas_pendentes = Reserva.objects.filter(status='PENDENTE').order_by('data', 'hora')
    # Mostra confirmadas de hoje em diante
    reservas_confirmadas = Reserva.objects.filter(status='CONFIRMADA', data__gte=timezone.now().date()).order_by('data', 'hora')
    
    context = {
        'reservas_pendentes': reservas_pendentes,
        'reservas_confirmadas': reservas_confirmadas,
    }
    return render(request, 'reservas/gerenciar_reservas.html', context)

# --- VIEW CONFIRMAR RESERVA (PARA O STAFF) ---
@login_required
@user_passes_test(is_staff_user) # Usa a função de staff importada
def confirmar_reserva(request, id): # O urls.py usa 'id', não 'reserva_id'
    reserva = get_object_or_404(Reserva, id=id)
    
    # Verifica se a ação é via POST (mais seguro)
    # Se o seu botão for um link GET, mude 'if request.method == "POST":' para 'if True:'
    # if request.method == 'POST': 
    reserva.status = 'CONFIRMADA'
    reserva.save()
    messages.success(request, f"Reserva de {reserva.usuario.get_full_name()} confirmada!")
    
    # Chama a nova função de e-mail (que não trava mais)
    enviar_email_status_reserva(request, reserva) 
    
    return redirect('gerenciar_reservas')
    # return redirect('gerenciar_reservas') # Se for GET, só precisa redirecionar

# --- VIEW CANCELAR RESERVA (PARA O STAFF) ---
@login_required
@user_passes_test(is_staff_user) # Usa a função de staff importada
def cancelar_reserva(request, id): # O urls.py usa 'id', não 'reserva_id'
    reserva = get_object_or_404(Reserva, id=id)
    
    # if request.method == 'POST':
    reserva.status = 'CANCELADA'
    reserva.save()
    messages.warning(request, f"Reserva de {reserva.usuario.get_full_name()} foi cancelada.")
    
    # Chama a nova função de e-mail (que não trava mais)
    enviar_email_status_reserva(request, reserva) 
    
    return redirect('gerenciar_reservas')
    # return redirect('gerenciar_reservas')