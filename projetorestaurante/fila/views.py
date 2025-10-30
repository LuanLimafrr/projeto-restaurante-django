# Arquivo: fila/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import ClienteFila
from django.utils import timezone
from django.contrib import messages
from comandas.models import Mesa, Comanda # Importar Mesa e Comanda
import datetime
from django.contrib.auth.decorators import login_required
from cardapio.models import ItemCardapio
from django.http import JsonResponse
from .forms import EntrarFilaForm
from reservas.forms import ReservaForm

# --- VIEW DA LANDING PAGE (Redireciona Staff) ---
def inicio(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('mapa_mesas') # Staff vai para o dashboard
    itens_destaque = ItemCardapio.objects.all().order_by('?')[:3]
    fila_form = EntrarFilaForm(); reserva_form = ReservaForm()
    contexto = { 'itens_destaque': itens_destaque, 'fila_form': fila_form, 'reserva_form': reserva_form }
    return render(request, 'inicio.html', contexto)

# --- VIEW PARA PROCESSAR O MODAL DA FILA ---
def entrar_na_fila_modal(request):
    if request.method == 'POST':
        form = EntrarFilaForm(request.POST)
        if form.is_valid():
            try:
                novo_cliente = ClienteFila.objects.create(nome=form.cleaned_data['nome'], quantidade=form.cleaned_data['quantidade'], telefone=form.cleaned_data.get('telefone'), email=form.cleaned_data.get('email'))
                request.session['id_cliente_fila'] = novo_cliente.id
                messages.success(request, f"'{novo_cliente.nome}', adicionado à fila!")
            except Exception as e: messages.error(request, f"Erro: {e}")
        else: messages.error(request, f"Erro: {next(iter(form.errors.values()))[0] if form.errors else 'Verifique.'}")
    return redirect('inicio')

# --- VIEW DA FILA DO CLIENTE (página /fila/) ---
def pagina_fila(request):
    if request.method == 'POST':
        form = EntrarFilaForm(request.POST)
        if form.is_valid():
            try:
                novo_cliente = ClienteFila.objects.create(nome=form.cleaned_data['nome'], quantidade=form.cleaned_data['quantidade'], telefone=form.cleaned_data.get('telefone'), email=form.cleaned_data.get('email'))
                request.session['id_cliente_fila'] = novo_cliente.id
                messages.success(request, f"'{novo_cliente.nome}', adicionado à fila!")
                return redirect('pagina_fila') 
            except Exception as e: messages.error(request, f"Erro: {e}")
    else: form = EntrarFilaForm()
    posicao_atual = 0; cliente_atual_obj = None
    id_cliente_sessao = request.session.get('id_cliente_fila')
    if id_cliente_sessao:
        try:
            cliente_atual_obj = ClienteFila.objects.get(id=id_cliente_sessao)
            if cliente_atual_obj.status == 'AGUARDANDO':
                clientes_antes = ClienteFila.objects.filter(status='AGUARDANDO', timestamp_entrada__lt=cliente_atual_obj.timestamp_entrada).count()
                posicao_atual = clientes_antes + 1
            else:
                if 'id_cliente_fila' in request.session: del request.session['id_cliente_fila']; cliente_atual_obj = None
        except ClienteFila.DoesNotExist:
            if 'id_cliente_fila' in request.session: del request.session['id_cliente_fila']; cliente_atual_obj = None
    contexto = {'posicao_cliente': posicao_atual, 'cliente_atual': cliente_atual_obj, 'fila_form': form}
    return render(request, 'fila/index.html', contexto)

# --- API CHECAR POSICAO ---
def checar_posicao(request):
    id_cliente_sessao = request.session.get('id_cliente_fila')
    if not id_cliente_sessao: return JsonResponse({'status': 'nao_esta_na_fila'}, status=404)
    try:
        cliente = ClienteFila.objects.get(id=id_cliente_sessao)
        if cliente.status != 'AGUARDANDO':
            status_report = cliente.status; del request.session['id_cliente_fila']
            return JsonResponse({'status': status_report})
        clientes_antes = ClienteFila.objects.filter(status='AGUARDANDO', timestamp_entrada__lt=cliente.timestamp_entrada).count()
        posicao = clientes_antes + 1
        return JsonResponse({'status': 'AGUARDANDO', 'posicao': posicao})
    except ClienteFila.DoesNotExist:
        if 'id_cliente_fila' in request.session: del request.session['id_cliente_fila']
        return JsonResponse({'status': 'nao_encontrado'}, status=404)

# --- VIEWS GERENCIAMENTO FILA ---
@login_required
def gerenciar_fila(request):
    if not request.user.is_staff: return redirect('inicio')
    clientes_aguardando = ClienteFila.objects.filter(status='AGUARDANDO').order_by('timestamp_entrada')
    proximo_cliente = clientes_aguardando.first()
    contexto = {'clientes_aguardando': clientes_aguardando, 'proximo_cliente': proximo_cliente}
    return render(request, 'fila/gerenciar_fila.html', contexto)

# --- FUNÇÕES REMOVIDAS ---
# A view 'chamar_proximo_cliente' foi REMOVIDA.
# A view 'alocar_cliente_na_fila' foi REMOVIDA.

@login_required
def remover_cliente(request, id):
    if not request.user.is_staff: return redirect('inicio')
    cliente = get_object_or_404(ClienteFila, id=id); nome_cliente = cliente.nome; cliente.delete()
    messages.warning(request, f"Cliente '{nome_cliente}' removido.")
    return redirect('gerenciar_fila')

@login_required
def marcar_como_desistente(request, id):
    if not request.user.is_staff: return redirect('inicio')
    cliente = get_object_or_404(ClienteFila, id=id)
    if cliente.status == 'AGUARDANDO': cliente.status = 'CANCELADO'; cliente.save(); messages.info(request, f"Cliente '{cliente.nome}' desistiu.")
    else: messages.warning(request, f"'{cliente.nome}' não está aguardando.")
    return redirect('gerenciar_fila')

def sair_da_fila_cliente(request):
    id_cliente_sessao = request.session.get('id_cliente_fila')
    if id_cliente_sessao:
        try:
            cliente = ClienteFila.objects.get(id=id_cliente_sessao, status='AGUARDANDO')
            cliente.status = 'CANCELADO'; cliente.save(); messages.info(request, "Você saiu da fila.")
        except ClienteFila.DoesNotExist: messages.error(request, "Não encontrado na fila.")
        if 'id_cliente_fila' in request.session: del request.session['id_cliente_fila']
    else: messages.warning(request, "Você não parece estar na fila.")
    return redirect('pagina_fila')