# Arquivo: comandas/views.py
# CORRIGIDO: Redirecionamento da Recepcionista após alocação

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import models
from django.db import transaction
from .models import Mesa, Comanda, ItemComanda
from django.utils import timezone
from fila.models import ClienteFila
from .forms import ItemComandaForm
from django.contrib import messages
from django.db.models import Sum, Count, Case, When, F
from decimal import Decimal
import datetime
from datetime import timedelta
# Importações de permissão
from cardapio.views import is_gerente, is_staff_user 

# --- VIEW PRINCIPAL DO STAFF (PDV MESAS) - SÓ GERENTE ---
@login_required
@user_passes_test(is_gerente, login_url='inicio') 
def mapa_mesas(request):
    if not request.user.is_staff: return redirect('inicio')
    cliente_id_para_alocar = request.GET.get('alocar_cliente_id')
    cliente_a_alocar = None
    if cliente_id_para_alocar:
        try: cliente_a_alocar = ClienteFila.objects.get(id=cliente_id_para_alocar, status='AGUARDANDO')
        except ClienteFila.DoesNotExist:
            messages.error(request, "Cliente não encontrado ou já foi alocado.")
            return redirect('mapa_mesas')
    mesas = Mesa.objects.all().order_by('numero')
    clientes_aguardando = ClienteFila.objects.filter(status='AGUARDANDO').order_by('timestamp_entrada')
    proximo_cliente = clientes_aguardando.first()
    contexto = { 
        'mesas': mesas, 
        'clientes_aguardando': clientes_aguardando, 
        'proximo_cliente': proximo_cliente, 
        'cliente_a_alocar': cliente_a_alocar,
        'is_gerente': True # Para o template saber que é o gerente
    }
    return render(request, 'comandas/dashboard_staff.html', contexto)

# --- NOVA VIEW: MAPA DE MESAS PARA RECEPCIONISTA ---
@login_required
@user_passes_test(is_staff_user, login_url='inicio') # Todo staff pode ver
def mapa_mesas_recepcao(request, id_cliente):
    if not request.user.is_staff: return redirect('inicio')
    
    try:
        cliente_a_alocar = ClienteFila.objects.get(id=id_cliente, status='AGUARDANDO')
    except ClienteFila.DoesNotExist:
        messages.error(request, "Cliente não encontrado ou já foi alocado.")
        return redirect('gerenciar_fila')

    mesas = Mesa.objects.all().order_by('numero')
    
    # --- INÍCIO DA CORREÇÃO ---
    # Estas linhas estavam faltando. O template 'dashboard_staff.html'
    # precisa delas (assim como a view 'gerenciar_fila').
    clientes_aguardando = ClienteFila.objects.filter(status='AGUARDANDO').order_by('timestamp_entrada')
    proximo_cliente = clientes_aguardando.first()
    # --- FIM DA CORREÇÃO ---
    
    contexto = { 
        'mesas': mesas, 
        'cliente_a_alocar': cliente_a_alocar,
        'is_gerente': is_gerente(request.user), # Passa False para Recepcionista
        
        # --- CONTEXTO ADICIONADO ---
        'clientes_aguardando': clientes_aguardando, 
        'proximo_cliente': proximo_cliente,
        # --- FIM DO CONTEXTO ADICIONADO ---
    }
    # Esta view renderiza o MESMO template do dashboard
    return render(request, 'comandas/dashboard_staff.html', contexto)


# --- VIEW PARA PROCESSAR A ALOCAÇÃO (TODO STAFF PODE FAZER) ---
@login_required
@user_passes_test(is_staff_user, login_url='inicio') 
def processar_alocacao_cliente(request, id_mesa, id_cliente):
    if not request.user.is_staff: return redirect('inicio')
    
    mesa = get_object_or_404(Mesa, id=id_mesa)
    cliente_a_sentar = get_object_or_404(ClienteFila, id=id_cliente)
    
    # --- CORREÇÃO AQUI ---
    # Define para onde redirecionar ANTES de qualquer ação
    redirect_url = 'mapa_mesas' if is_gerente(request.user) else 'gerenciar_fila'

    if mesa.status == 'LIVRE' and cliente_a_sentar.status == 'AGUARDANDO':
        mesa.status = 'OCUPADA'; mesa.save()
        cliente_a_sentar.status = 'CHAMADO'; cliente_a_sentar.timestamp_atendimento = timezone.now(); cliente_a_sentar.save()
        Comanda.objects.create(mesa=mesa, status='ABERTA')
        messages.success(request, f"Cliente '{cliente_a_sentar.nome}' alocado à Mesa {mesa.numero}.")
        return redirect(redirect_url) # <-- REDIRECIONAMENTO INTELIGENTE
            
    else:
        messages.warning(request, "Não foi possível alocar: Mesa não está livre ou cliente não está mais aguardando.")
        return redirect(redirect_url) # <-- REDIRECIONAMENTO INTELIGENTE

# --- VIEW DETALHE COMANDA (SÓ GERENTE) ---
@login_required
@user_passes_test(is_gerente, login_url='inicio') 
def detalhe_comanda(request, id_mesa):
    if not request.user.is_staff: return redirect('inicio')
    mesa = get_object_or_404(Mesa, id=id_mesa)
    comanda_ativa = Comanda.objects.filter(mesa=mesa).exclude(status='PAGA').first()
    form_invalido = None
    if request.method == 'POST' and comanda_ativa and comanda_ativa.status == 'ABERTA':
        form = ItemComandaForm(request.POST)
        if form.is_valid():
            item_sel = form.cleaned_data['item_cardapio']; qtd = form.cleaned_data['quantidade']; obs = form.cleaned_data.get('observacao')
            if item_sel.item_estoque and item_sel.item_estoque.quantidade_atual < qtd:
                messages.error(request, f"Estoque insuficiente para '{item_sel.nome}'. Restam {item_sel.item_estoque.quantidade_atual} un.")
                form_invalido = form
            else:
                ItemComanda.objects.create(comanda=comanda_ativa, item_cardapio=item_sel, quantidade=qtd, observacao=obs)
                messages.success(request, f"Item '{item_sel.nome}' adicionado.")
                return redirect('detalhe_comanda', id_mesa=mesa.id)
        else: messages.error(request, "Erro ao adicionar item."); form_invalido = form
    form_para_template = form_invalido if form_invalido else ItemComandaForm()
    itens_da_comanda = comanda_ativa.itens.all().order_by('id') if comanda_ativa else []
    contexto = { 'mesa': mesa, 'comanda': comanda_ativa, 'itens_da_comanda': itens_da_comanda, 'form': form_para_template }
    return render(request, 'comandas/detalhe_comanda.html', contexto)

# --- VIEW FECHAR CONTA / GERAR NOTA (SÓ GERENTE) ---
@login_required
@user_passes_test(is_gerente, login_url='inicio') 
def fechar_comanda(request, id_comanda):
    if not request.user.is_staff: return redirect('inicio')
    comanda = get_object_or_404(Comanda, id=id_comanda)
    if comanda.status == 'ABERTA':
        comanda.status = 'FECHADA'; comanda.timestamp_fechamento = timezone.now(); comanda.save()
        comanda.mesa.status = 'PAGAMENTO'; comanda.mesa.save()
        messages.info(request, f"Conta da Mesa {comanda.mesa.numero} fechada. Aguardando pagamento.")
    if comanda.status == 'FECHADA':
        contexto = {
            'comanda': comanda,
            'itens_comanda': comanda.itens.all().order_by('id'),
            'subtotal': comanda.get_subtotal(),
            'taxa_servico': comanda.get_taxa_servico(),
            'total_geral': comanda.get_total(),
        }
        return render(request, 'comandas/nota_fiscal.html', contexto)
    messages.warning(request, "Esta comanda não está mais aguardando pagamento.")
    return redirect('mapa_mesas')

# --- VIEW CONFIRMAR PAGAMENTO (SÓ GERENTE) ---
@login_required
@transaction.atomic
@user_passes_test(is_gerente, login_url='inicio') 
def confirmar_pagamento(request, id_comanda):
    if not request.user.is_staff: return redirect('inicio')
    comanda = get_object_or_404(Comanda, id=id_comanda)
    if comanda.status == 'FECHADA':
        itens_com_estoque = comanda.itens.select_related('item_cardapio__item_estoque').filter(item_cardapio__item_estoque__isnull=False)
        pode_pagar = True
        for item_comanda in itens_com_estoque:
            item_estoque = item_comanda.item_cardapio.item_estoque
            if item_estoque.quantidade_atual < item_comanda.quantidade:
                messages.error(request, f"ERRO ESTOQUE: '{item_estoque.nome}' possui {item_estoque.quantidade_atual} un. Pedido: {item_comanda.quantidade}.")
                pode_pagar = False; break
        if pode_pagar:
            for item_comanda in itens_com_estoque:
                item_estoque = item_comanda.item_cardapio.item_estoque
                item_estoque.remover_do_estoque(item_comanda.quantidade)
                if item_estoque.ponto_reposicao is not None and item_estoque.quantidade_atual <= item_estoque.ponto_reposicao:
                    messages.warning(request, f"ALERTA ESTOQUE: '{item_estoque.nome}' baixo! Restam {item_estoque.quantidade_atual} un.")
            comanda.status = 'PAGA'; comanda.save()
            comanda.mesa.status = 'LIVRE'; comanda.mesa.save()
            messages.success(request, f"Pagamento da Mesa {comanda.mesa.numero} confirmado. Estoque atualizado.")
            return redirect('mapa_mesas')
        else:
            messages.error(request, "Pagamento falhou devido a erro de estoque.")
            return redirect('fechar_comanda', id_comanda=comanda.id) # Volta para a nota
    messages.info(request, "Esta comanda não está aguardando pagamento.")
    return redirect('mapa_mesas')

# --- AÇÕES DE ITEM NA COMANDA (SÓ GERENTE) ---
@login_required
@user_passes_test(is_gerente, login_url='inicio') 
def remover_item_comanda(request, id_item):
    if not request.user.is_staff: return redirect('inicio')
    item = get_object_or_404(ItemComanda, id=id_item); comanda_pai = item.comanda; id_mesa_redirect = comanda_pai.mesa.id
    if comanda_pai.status == 'ABERTA': nome_item = item.item_cardapio.nome; item.delete(); messages.warning(request, f"Item '{nome_item}' removido.")
    return redirect('detalhe_comanda', id_mesa=id_mesa_redirect)
@login_required
@user_passes_test(is_gerente, login_url='inicio') 
def toggle_taxa_servico(request, id_comanda):
    if not request.user.is_staff: return redirect('inicio')
    comanda = get_object_or_404(Comanda, id=id_comanda)
    if comanda.status == 'ABERTA':
        comanda.incluir_taxa_servico = not comanda.incluir_taxa_servico; comanda.save()
        status_taxa = "incluída" if comanda.incluir_taxa_servico else "removida"; messages.info(request, f"Taxa {status_taxa}.")
    return redirect('detalhe_comanda', id_mesa=comanda.mesa.id)
@login_required
@user_passes_test(is_gerente, login_url='inicio') 
def aumentar_quantidade_item(request, id_item):
    if not request.user.is_staff: return redirect('inicio')
    item = get_object_or_404(ItemComanda, id=id_item); comanda_pai = item.comanda
    if comanda_pai.status == 'ABERTA': item.quantidade += 1; item.save()
    return redirect('detalhe_comanda', id_mesa=comanda_pai.mesa.id)
@login_required
@user_passes_test(is_gerente, login_url='inicio') 
def diminuir_quantidade_item(request, id_item):
    if not request.user.is_staff: return redirect('inicio')
    item = get_object_or_404(ItemComanda, id=id_item); comanda_pai = item.comanda
    if comanda_pai.status == 'ABERTA':
        if item.quantidade > 1: item.quantidade -= 1; item.save()
        else: nome_item = item.item_cardapio.nome; item.delete(); messages.warning(request, f"Item '{nome_item}' removido.")
    return redirect('detalhe_comanda', id_mesa=comanda_pai.mesa.id)

# --- VIEW DE RELATÓRIO (SÓ GERENTE) ---
@login_required
@user_passes_test(is_gerente, login_url='inicio') 
def relatorio_diario(request):
    if not request.user.is_staff: return redirect('inicio')
    hoje = timezone.now().date(); periodo = request.GET.get('periodo', 'hoje')
    data_custom_str = request.GET.get('data'); data_inicio = hoje; data_fim = hoje
    titulo_relatorio = f"Relatório de Vendas - {hoje.strftime('%d/%m/%Y')}"
    data_valida = True
    if data_custom_str:
        try: data_sel = datetime.datetime.strptime(data_custom_str, '%Y-%m-%d').date(); data_inicio = data_sel; data_fim = data_sel; periodo = 'custom'; titulo_relatorio = f"Relatório - {data_sel.strftime('%d/%m/%Y')}"
        except ValueError: messages.error(request, "Data inválida."); periodo = 'hoje'; data_valida = False
    if data_valida and periodo == 'semana':
        dia_sem = hoje.weekday(); data_inicio = hoje - timedelta(days=dia_sem + 1 if dia_sem < 6 else 0); data_fim = data_inicio + timedelta(days=6); titulo_relatorio = f"Semanal ({data_inicio:%d/%m} - {data_fim:%d/%m})"
    elif data_valida and periodo == 'mes':
        data_inicio = hoje.replace(day=1); prox_mes = (data_inicio + timedelta(days=32)).replace(day=1); data_fim = prox_mes - timedelta(days=1); titulo_relatorio = f"Mensal ({hoje.strftime('%B/%Y')})"
    comandas_no_periodo = Comanda.objects.filter(status='PAGA', timestamp_fechamento__date__range=[data_inicio, data_fim])
    totais = comandas_no_periodo.aggregate(total_vendido=Sum(F('itens__preco_unitario_momento') * F('itens__quantidade')), total_taxa=Sum(Case(When(incluir_taxa_servico=True, then=(F('itens__preco_unitario_momento')*F('itens__quantidade')*Decimal('0.10'))), default=Decimal('0.0'), output_field=models.DecimalField())), num_comandas=Count('id', distinct=True) )
    total_vendido_bruto = totais['total_vendido'] or Decimal('0.0'); total_taxa_calc = totais['total_taxa'] or Decimal('0.0')
    num_comandas = totais['num_comandas'] or 0
    valor_total = (total_vendido_bruto + total_taxa_calc).quantize(Decimal('0.01'))
    contexto = { 'titulo_relatorio': titulo_relatorio, 'data_inicio': data_inicio, 'data_fim': data_fim, 'periodo_selecionado': periodo, 'numero_comandas': num_comandas, 'valor_total': valor_total, 'comandas_do_periodo': comandas_no_periodo.order_by('-timestamp_fechamento')}
    return render(request, 'comandas/relatorio_diario.html', contexto)