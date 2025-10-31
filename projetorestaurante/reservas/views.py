# /projetorestaurante/reservas/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
# ... (outros imports do django)
from django.contrib import messages
from .models import Reserva
from .forms import ReservaForm
from django.utils import timezone
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth.models import User

# --- NOVAS IMPORTAÇÕES ---
import requests
import os
# --- FIM DAS NOVAS IMPORTAÇÕES ---


# Função para checar se é staff (você já deve ter uma parecida)
def is_staff(user):
    return user.is_staff

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

# --- (O RESTO DAS SUAS VIEWS DE RESERVA) ---
# ... (suas views fazer_reserva, gerenciar_reservas, etc., devem estar aqui) ...

# (Exemplo de como sua view confirmar_reserva deve estar)
@login_required
@user_passes_test(is_staff)
def confirmar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    if request.method == 'POST':
        reserva.status = 'CONFIRMADA'
        reserva.save()
        messages.success(request, f"Reserva de {reserva.usuario.get_full_name()} confirmada!")
        
        # Chama a nova função de e-mail (que não trava mais)
        enviar_email_status_reserva(request, reserva) 
        
        return redirect('gerenciar_reservas')
    return redirect('gerenciar_reservas')

# (Exemplo de como sua view cancelar_reserva deve estar)
@login_required
@user_passes_test(is_staff)
def cancelar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    if request.method == 'POST':
        reserva.status = 'CANCELADA'
        reserva.save()
        messages.warning(request, f"Reserva de {reserva.usuario.get_full_name()} foi cancelada.")
        
        # Chama a nova função de e-mail (que não trava mais)
        enviar_email_status_reserva(request, reserva) 
        
        return redirect('gerenciar_reservas')
    return redirect('gerenciar_reservas')

# ... (Certifique-se de que suas outras views de reserva estejam aqui) ...

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
            # Não envia e-mail aqui se a reserva é PENDENTE e você só envia status atualizado
            # Se quiser enviar um e-mail de "reserva pendente", adicione:
            # enviar_email_status_reserva(request, reserva)
            return redirect('historico_reservas') # Redireciona para o histórico
        else:
            messages.error(request, 'Erro ao criar a reserva. Por favor, verifique os dados.')
    else:
        form = ReservaForm()
    
    # Renderiza o template 'reservas/fazer_reserva.html'
    return render(request, 'reservas/fazer_reserva.html', {'form': form})

# A view para o modal (geralmente renderiza apenas um formulário para AJAX ou para ser incluído)
@login_required
def fazer_reserva_modal(request):
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.usuario = request.user
            reserva.status = 'PENDENTE'
            reserva.save()
            # O modal geralmente precisa de uma resposta JSON ou um redirecionamento
            # Aqui, para simplificar, redirecionamos. Para AJAX, você retornaria um JsonResponse.
            messages.success(request, 'Sua reserva foi criada com sucesso (via modal)!')
            # Você pode enviar o e-mail aqui se desejar um e-mail de "pendente"
            # enviar_email_status_reserva(request, reserva)
            return redirect('historico_reservas') # Redireciona para o histórico
        else:
            # Para modal, você geralmente retorna o formulário com erros ou JSON de erro
            messages.error(request, 'Erro ao criar a reserva via modal. Por favor, verifique os dados.')
            form = ReservaForm(request.POST) # Re-instancia o form para mostrar erros
    else:
        form = ReservaForm()
    
    # Renderiza o template 'reservas/fazer_reserva_modal.html' (se você tiver um)
    # Ou 'reservas/fazer_reserva.html' se for um modal que usa o mesmo form
    return render(request, 'reservas/fazer_reserva_modal.html', {'form': form})