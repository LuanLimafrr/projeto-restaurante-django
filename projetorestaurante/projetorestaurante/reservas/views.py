# Arquivo: reservas/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ReservaForm
from .models import Reserva
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
import datetime
from datetime import timedelta
import os 

# --- IMPORTAÇÕES DE PERMISSÃO ---
from cardapio.views import is_gerente, is_staff_user 

# --- HELPER PARA ENVIAR EMAIL (VERSÃO RESEND/ANYMAIL) ---
def enviar_email_status_reserva(request, reserva):
    """
    Envia e-mail de confirmação ou cancelamento usando Anymail + Resend.
    """
    if not reserva.usuario or not reserva.usuario.email:
        print(f"DEBUG: Reserva {reserva.id} sem usuário ou email.")
        return

    status_map = {'CONFIRMADA': 'Confirmada', 'CANCELADA': 'Cancelada'}
    status_legivel = status_map.get(reserva.status)
    
    if not status_legivel:
        return

    assunto = f"Sua reserva no Chama do Cerrado foi {status_legivel}!"
    contexto_email = {'reserva': reserva, 'status_legivel': status_legivel}
    
    try:
        # Renderiza o HTML do arquivo templates/emails/status_reserva.html
        mensagem_html = render_to_string('emails/status_reserva.html', contexto_email)
        texto_puro = strip_tags(mensagem_html)

        email = EmailMultiAlternatives(
            subject=assunto,
            body=texto_puro,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[reserva.usuario.email]
        )
        email.attach_alternative(mensagem_html, "text/html")
        email.send()
        print(f"DEBUG: Email enviado para {reserva.usuario.email} com sucesso.")
        
    except Exception as e:
        print(f"ERRO CRÍTICO ao enviar email: {e}")
        if request:
            messages.error(request, "O status foi alterado, mas o e-mail de notificação falhou.")

# --- Views Cliente ---

@login_required
def fazer_reserva_modal(request):
    if request.user.is_staff: 
        messages.error(request, "Funcionários não podem fazer reservas.")
        return redirect('inicio')
        
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            data_reserva = form.cleaned_data['data']
            hora_reserva = form.cleaned_data['hora']
            novas_pessoas = form.cleaned_data['quantidade_pessoas']
            
            reservas_existentes = Reserva.objects.filter(data=data_reserva, hora=hora_reserva, status__in=['PENDENTE', 'CONFIRMADA'])
            total_pessoas = reservas_existentes.aggregate(total=Sum('quantidade_pessoas'))['total'] or 0
            limite = settings.RESTAURANTE_CAPACIDADE_POR_HORARIO
            
            if (total_pessoas + novas_pessoas) > limite:
                vagas = limite - total_pessoas
                messages.error(request, f"Horário lotado. Vagas disponíveis: {vagas}.")
            else:
                reserva = form.save(commit=False)
                reserva.usuario = request.user
                reserva.save()
                messages.success(request, 'Solicitação enviada! Você receberá um e-mail em breve.')
                return redirect('perfil') 
        else:
            messages.error(request, f"Erro: {next(iter(form.errors.values()))[0] if form.errors else 'Verifique os dados.'}")
    return redirect('inicio')

@login_required
def fazer_reserva(request):
    if request.user.is_staff: 
        messages.error(request, "Funcionários não podem fazer reservas.")
        return redirect('inicio')
        
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            data_reserva = form.cleaned_data['data']
            hora_reserva = form.cleaned_data['hora']
            novas_pessoas = form.cleaned_data['quantidade_pessoas']
            
            reservas_existentes = Reserva.objects.filter(data=data_reserva, hora=hora_reserva, status__in=['PENDENTE', 'CONFIRMADA'])
            total_pessoas = reservas_existentes.aggregate(total=Sum('quantidade_pessoas'))['total'] or 0
            limite = settings.RESTAURANTE_CAPACIDADE_POR_HORARIO
            
            if (total_pessoas + novas_pessoas) > limite:
                vagas = limite - total_pessoas
                form.add_error(None, f"Horário lotado. Vagas disponíveis: {vagas}.")
            else:
                reserva = form.save(commit=False)
                reserva.usuario = request.user
                reserva.save()
                messages.success(request, 'Solicitação enviada! Você receberá um e-mail em breve.')
                return redirect('perfil') 
    else:
        form = ReservaForm()
        
    contexto = {'form': form}
    return render(request, 'reservas/fazer_reserva.html', contexto)


# --- Views Administrativas (SÓ GERENTE) ---

@login_required
@user_passes_test(is_gerente, login_url='inicio')
def gerenciar_reservas(request):
    hoje = timezone.now().date()
    data_selecionada_str = request.GET.get('data')
    data_selecionada = hoje
    
    if data_selecionada_str:
        try:
            data_selecionada = datetime.datetime.strptime(data_selecionada_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Data inválida.")
            data_selecionada = hoje

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
        
        dias_com_vagas.append({
            'data': dia,
            'pessoas': pessoas_no_dia,
            'vagas': vagas_restantes,
            'limite': limite_total,
            'dia_semana_pt': weekdays_pt[dia.weekday()] 
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

@login_required
@user_passes_test(is_gerente, login_url='inicio')
def historico_reservas(request):
    hoje = timezone.now().date()
    reservas_canceladas = Reserva.objects.filter(status='CANCELADA')
    reservas_confirmadas_passadas = Reserva.objects.filter(status='CONFIRMADA', data__lt=hoje)
    lista_historico = (reservas_canceladas | reservas_confirmadas_passadas).order_by('-data', '-hora').distinct()
    contexto = {'lista_historico': lista_historico}
    return render(request, 'reservas/historico.html', contexto)

@login_required
@user_passes_test(is_gerente, login_url='inicio')
def confirmar_reserva(request, id):
    reserva = get_object_or_404(Reserva, id=id)
    if reserva.status == 'PENDENTE':
        reserva.status = 'CONFIRMADA'
        reserva.save()
        nome_cliente = reserva.usuario.get_full_name() if (reserva.usuario and reserva.usuario.get_full_name()) else reserva.usuario.username
        messages.success(request, f"Reserva de {nome_cliente} confirmada.")
        enviar_email_status_reserva(request, reserva)
    return redirect('gerenciar_reservas')

@login_required
@user_passes_test(is_gerente, login_url='inicio')
def cancelar_reserva(request, id):
    reserva = get_object_or_404(Reserva, id=id)
    if reserva.status != 'CANCELADA':
        reserva.status = 'CANCELADA'
        reserva.save()
        nome_cliente = reserva.usuario.get_full_name() if (reserva.usuario and reserva.usuario.get_full_name()) else reserva.usuario.username
        messages.warning(request, f"Reserva de {nome_cliente} cancelada.")
        enviar_email_status_reserva(request, reserva)
    return redirect('gerenciar_reservas')