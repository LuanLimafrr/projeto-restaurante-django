# Arquivo: reservas/views.py
# VERSÃO CORRIGIDA (id vs reserva_id) E COM API DE EMAIL

from django.shortcuts import render, redirect, get_object_or_404
from .forms import ReservaForm
from .models import Reserva
from django.contrib.auth.decorators import login_required, user_passes_test # <--- IMPORTAÇÃO CORRIGIDA
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
import datetime
from datetime import timedelta
import requests # <-- IMPORTADO PARA API DE EMAIL
import os # <-- IMPORTADO PARA API DE EMAIL

# --- IMPORTAÇÕES DE PERMISSÃO ---
# Importa as funções de checagem do seu app 'cardapio'
from cardapio.views import is_gerente, is_staff_user 


# --- FUNÇÃO DE EMAIL (USANDO API REQUESTS) ---
def send_email_via_api(to_email, subject, html_content):
    api_key = os.environ.get('SENDGRID_API_KEY') # LÊ A CHAVE DO RENDER
    from_email = settings.DEFAULT_FROM_EMAIL 

    if not api_key or not from_email:
        print("ERRO CRÍTICO: SENDGRID_API_KEY ou DEFAULT_FROM_EMAIL não configurado.")
        return False

    data = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": from_email, "name": "Chama do Cerrado"},
        "subject": subject,
        "content": [{"type": "text/html", "value": html_content}]
    }
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        print(f"DEBUG: Tentando enviar email para {to_email}...")
        response = requests.post('https://api.sendgrid.com/v3/mail/send', headers=headers, json=data, timeout=10)
        
        if response.status_code == 202:
            print(f"DEBUG: Email enviado com Status: 202")
            return True
        else:
            print(f"ERRO: SendGrid rejeitou email. Status: {response.status_code}, Detalhes: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"ERRO: Falha de requisição para SendGrid: {e}")
        return False

# --- HELPER PARA ENVIAR EMAIL (MODIFICADO) ---
def enviar_email_status_reserva(request, reserva):
    if not reserva.usuario or not reserva.usuario.email:
        print(f"DEBUG: Reserva {reserva.id} sem usuário ou email.")
        return

    status_map = {'CONFIRMADA': 'Confirmada', 'CANCELADA': 'Cancelada'}
    status_legivel = status_map.get(reserva.status)
    if not status_legivel:
        return

    assunto = f"Sua reserva no Chama do Cerrado foi {status_legivel}!"
    contexto_email = {'reserva': reserva, 'status_legivel': status_legivel}
    mensagem_html = render_to_string('emails/status_reserva.html', contexto_email) # Renderize HTML

    try:
        # --- MUDANÇA PRINCIPAL AQUI ---
        sucesso = send_email_via_api(
            to_email=reserva.usuario.email,
            subject=assunto,
            html_content=mensagem_html
        )
        # --- FIM DA MUDANÇA ---
        
        if sucesso:
            print(f"DEBUG: Email status '{status_legivel}' enviado com sucesso para {reserva.usuario.email} via SendGrid API.")
        else:
            print(f"Erro: Falha no envio de email para {reserva.usuario.email} via SendGrid API.")
            if request: messages.error(request, f"Erro ao enviar email para {reserva.usuario.email}.")

    except Exception as e:
        print(f"Exceção inesperada ao tentar enviar email para {reserva.usuario.email}: {e}")
        if request: messages.error(request, f"Erro crítico ao enviar email para {reserva.usuario.email}.")

# --- Views Cliente (fazer_reserva_modal, fazer_reserva - sem mudanças) ---
@login_required
def fazer_reserva_modal(request):
    if request.user.is_staff: messages.error(request, "Funcionários não podem fazer reservas."); return redirect('inicio')
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            data_reserva = form.cleaned_data['data']; hora_reserva = form.cleaned_data['hora']; novas_pessoas = form.cleaned_data['quantidade_pessoas']
            reservas_existentes = Reserva.objects.filter(data=data_reserva, hora=hora_reserva, status__in=['PENDENTE', 'CONFIRMADA'])
            total_pessoas = reservas_existentes.aggregate(total=Sum('quantidade_pessoas'))['total'] or 0
            limite = settings.RESTAURANTE_CAPACIDADE_POR_HORARIO
            if (total_pessoas + novas_pessoas) > limite:
                vagas = limite - total_pessoas; messages.error(request, f"Horário lotado. Vagas: {vagas}.")
            else:
                reserva = form.save(commit=False); reserva.usuario = request.user; reserva.save()
                messages.success(request, 'Solicitação enviada! Aguarde email.')
                return redirect('perfil') # Redireciona para o perfil do cliente
        else: messages.error(request, f"Erro: {next(iter(form.errors.values()))[0] if form.errors else 'Verifique.'}")
    return redirect('inicio')

@login_required
def fazer_reserva(request):
    if request.user.is_staff: messages.error(request, "Funcionários não podem fazer reservas."); return redirect('inicio')
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            data_reserva = form.cleaned_data['data']; hora_reserva = form.cleaned_data['hora']; novas_pessoas = form.cleaned_data['quantidade_pessoas']
            reservas_existentes = Reserva.objects.filter(data=data_reserva, hora=hora_reserva, status__in=['PENDENTE', 'CONFIRMADA'])
            total_pessoas = reservas_existentes.aggregate(total=Sum('quantidade_pessoas'))['total'] or 0
            limite = settings.RESTAURANTE_CAPACIDADE_POR_HORARIO
            if (total_pessoas + novas_pessoas) > limite:
                vagas = limite - total_pessoas; form.add_error(None, f"Horário lotado. Vagas: {vagas}.")
            else:
                reserva = form.save(commit=False); reserva.usuario = request.user; reserva.save()
                messages.success(request, 'Solicitação enviada! Aguarde email.')
                return redirect('perfil') # Redireciona para o perfil do cliente
    else: form = ReservaForm()
    contexto = {'form': form}
    return render(request, 'reservas/fazer_reserva.html', contexto)


# --- VIEW GERENCIAR RESERVAS (SÓ GERENTE) ---
@login_required
@user_passes_test(is_gerente, login_url='inicio') # <-- SÓ GERENTE
def gerenciar_reservas(request):
    if not request.user.is_staff: return redirect('inicio')

    hoje = timezone.now().date()
    data_selecionada_str = request.GET.get('data')
    data_selecionada = hoje
    if data_selecionada_str:
        try: data_selecionada = datetime.datetime.strptime(data_selecionada_str, '%Y-%m-%d').date()
        except ValueError: messages.error(request, "Data inválida."); data_selecionada = hoje

    weekdays_pt = {
        0: 'Segunda-feira', 1: 'Terça-feira', 2: 'Quarta-feira',
        3: 'Quinta-feira', 4: 'Sexta-feira', 5: 'Sábado', 6: 'Domingo'
    }

    dias_com_vagas = []
    limite_total = settings.RESTAURANTE_CAPACIDADE_POR_HORARIO
    for i in range(7):
        dia = hoje + timedelta(days=i)
        reservas_no_dia = Reserva.objects.filter(data=dia, status__in=['PENDENTE', 'CONFIRMADA'])
        pessoas_no_dia = reservas_no_dia.aggregate(total=Sum('quantidade_pessoas'))['total'] or 0
        vagas_restantes = max(0, limite_total - pessoas_no_dia)
        dia_da_semana_int = dia.weekday() 
        
        dias_com_vagas.append({
            'data': dia,
            'pessoas': pessoas_no_dia,
            'vagas': vagas_restantes,
            'limite': limite_total,
            'dia_semana_pt': weekdays_pt[dia_da_semana_int] 
        })

    reservas_pendentes_dia = Reserva.objects.filter(status='PENDENTE', data=data_selecionada)
    reservas_confirmadas_dia = Reserva.objects.filter(status='CONFIRMADA', data=data_selecionada)
    lista_reservas_dia = (reservas_pendentes_dia | reservas_confirmadas_dia).order_by('hora').distinct()

    reservas_pendentes_todas = Reserva.objects.filter(status='PENDENTE').order_by('data', 'hora')

    contexto = {
        'lista_reservas_dia': lista_reservas_dia,
        'reservas_pendentes_todas': reservas_pendentes_todas,
        'dias_com_vagas': dias_com_vagas,
        'data_selecionada': data_selecionada,
    }
    return render(request, 'reservas/gerenciar.html', contexto)


# --- historico_reservas (SÓ GERENTE) ---
@login_required
@user_passes_test(is_gerente, login_url='inicio') # <-- SÓ GERENTE
def historico_reservas(request):
    if not request.user.is_staff: return redirect('inicio')
    hoje = timezone.now().date()
    reservas_canceladas = Reserva.objects.filter(status='CANCELADA')
    reservas_confirmadas_passadas = Reserva.objects.filter(status='CONFIRMADA', data__lt=hoje)
    lista_historico = (reservas_canceladas | reservas_confirmadas_passadas).order_by('-data', '-hora').distinct()
    contexto = {'lista_historico': lista_historico}
    return render(request, 'reservas/historico.html', contexto)

# --- confirmar_reserva (SÓ GERENTE) ---
@login_required
@user_passes_test(is_gerente, login_url='inicio') # <-- SÓ GERENTE
def confirmar_reserva(request, id): # <-- CORRIGIDO AQUI (era reserva_id)
    if not request.user.is_staff: return redirect('inicio')
    reserva = get_object_or_404(Reserva, id=id) # <-- CORRIGIDO AQUI
    if reserva.status == 'PENDENTE':
        reserva.status = 'CONFIRMADA'; reserva.save()
        nome_cliente = reserva.usuario.get_full_name() if reserva.usuario else 'Cliente'
        messages.success(request, f"Reserva de {nome_cliente} confirmada.")
        enviar_email_status_reserva(request, reserva)
    return redirect('gerenciar_reservas')

# --- cancelar_reserva (SÓ GERENTE) ---
@login_required
@user_passes_test(is_gerente, login_url='inicio') # <-- SÓ GERENTE
def cancelar_reserva(request, id): # <-- CORRIGIDO AQUI (era reserva_id)
    if not request.user.is_staff: return redirect('inicio')
    reserva = get_object_or_404(Reserva, id=id) # <-- CORRIGIDO AQUI
    if reserva.status != 'CANCELADA':
        reserva.status = 'CANCELADA'; reserva.save()
        nome_cliente = reserva.usuario.get_full_name() if reserva.usuario else 'Cliente'
        messages.warning(request, f"Reserva de {nome_cliente} cancelada.")
        enviar_email_status_reserva(request, reserva)
    return redirect('gerenciar_reservas')
