# Arquivo: cardapio/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import Categoria, ItemCardapio
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import CategoriaForm, ItemCardapioForm
from django.urls import reverse_lazy
# --- NOVOS IMPORTS ---
from django.views.decorators.http import require_POST # Para garantir POST nas ações
from django.db.models import Prefetch # Para filtrar itens ativos na view pública
from decimal import Decimal, InvalidOperation # Para validar preço

# --- HELPER STAFF ---
def is_staff_user(user): return user.is_staff

# --- View Pública (ATUALIZADA) ---
def exibir_cardapio(request):
    """Exibe o cardápio público, mostrando apenas itens ativos."""
    categorias = Categoria.objects.prefetch_related(
        # Filtra os itens DENTRO do prefetch para pegar só os ativos
        Prefetch('itens', queryset=ItemCardapio.objects.filter(ativo=True).order_by('nome'))
    ).order_by('nome') # Ordena as categorias

    # Filtra categorias que ficaram sem nenhum item ativo após o prefetch
    categorias_com_itens = [cat for cat in categorias if cat.itens.all()]

    contexto = {'categorias': categorias_com_itens}
    return render(request, 'cardapio.html', contexto)

# --- VIEWS DE GERENCIAMENTO ---

@login_required
@user_passes_test(is_staff_user, login_url='inicio')
def listar_cardapio_admin(request):
    """Lista TODAS as categorias e itens (ativos e inativos) para o admin."""
    categorias = Categoria.objects.all().prefetch_related('itens').order_by('nome')
    contexto = {'categorias': categorias}
    return render(request, 'cardapio/gerenciar_cardapio.html', contexto)

# --- Categorias (sem mudanças) ---
@login_required
@user_passes_test(is_staff_user, login_url='inicio')
def adicionar_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            try:
                form.save(); messages.success(request, f"Categoria '{form.cleaned_data['nome']}' adicionada.")
                return redirect('gerenciar_cardapio')
            except Exception as e: # Captura erro de 'unique'
                 messages.error(request, f"Erro ao adicionar categoria: {e}")
        else: messages.error(request, "Erro no formulário.")
    else: form = CategoriaForm()
    return render(request, 'cardapio/categoria_form.html', {'form': form, 'titulo': 'Adicionar Categoria'})

@login_required
@user_passes_test(is_staff_user, login_url='inicio')
def editar_categoria(request, id):
    categoria = get_object_or_404(Categoria, id=id)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            try:
                form.save(); messages.success(request, f"Categoria '{form.cleaned_data['nome']}' atualizada.")
                return redirect('gerenciar_cardapio')
            except Exception as e: messages.error(request, f"Erro ao editar: {e}")
        else: messages.error(request, "Erro no formulário.")
    else: form = CategoriaForm(instance=categoria)
    return render(request, 'cardapio/categoria_form.html', {'form': form, 'titulo': f'Editar: {categoria.nome}'})

@login_required
@user_passes_test(is_staff_user, login_url='inicio')
def deletar_categoria(request, id):
    categoria = get_object_or_404(Categoria, id=id)
    if request.method == 'POST':
        nome_deletado = categoria.nome
        if categoria.itens.exists():
             messages.error(request, f"Não é possível deletar '{nome_deletado}', pois contém itens.")
        else:
            categoria.delete(); messages.success(request, f"Categoria '{nome_deletado}' deletada.")
        return redirect('gerenciar_cardapio')
    return render(request, 'cardapio/confirm_delete.html', {'objeto': categoria, 'tipo': 'Categoria'})

# --- Itens do Cardápio ---
@login_required
@user_passes_test(is_staff_user, login_url='inicio')
def adicionar_item(request):
    if request.method == 'POST':
        form = ItemCardapioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(); messages.success(request, f"Item '{form.cleaned_data['nome']}' adicionado.")
            return redirect('gerenciar_cardapio')
        else: messages.error(request, "Erro no formulário. Verifique os campos.")
    else: form = ItemCardapioForm()
    return render(request, 'cardapio/item_form.html', {'form': form, 'titulo': 'Adicionar Item', 'enctype': 'multipart/form-data'})

@login_required
@user_passes_test(is_staff_user, login_url='inicio')
def editar_item(request, id):
    item = get_object_or_404(ItemCardapio, id=id)
    if request.method == 'POST':
        form = ItemCardapioForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save(); messages.success(request, f"Item '{form.cleaned_data['nome']}' atualizado.")
            return redirect('gerenciar_cardapio')
        else: messages.error(request, "Erro no formulário.")
    else: form = ItemCardapioForm(instance=item)
    return render(request, 'cardapio/item_form.html', {'form': form, 'titulo': f'Editar: {item.nome}', 'enctype': 'multipart/form-data', 'item': item})

@login_required
@user_passes_test(is_staff_user, login_url='inicio')
def deletar_item(request, id):
    item = get_object_or_404(ItemCardapio, id=id)
    if request.method == 'POST':
        nome_deletado = item.nome
        item.delete(); messages.success(request, f"Item '{nome_deletado}' deletado.")
        return redirect('gerenciar_cardapio')
    return render(request, 'cardapio/confirm_delete.html', {'objeto': item, 'tipo': 'Item'})


# --- NOVAS VIEWS DE AÇÃO ---

@login_required
@user_passes_test(is_staff_user, login_url='inicio')
@require_POST # Garante que esta view só aceita POST
def atualizar_preco_item(request, id):
    item = get_object_or_404(ItemCardapio, id=id)
    novo_preco_str = request.POST.get('novo_preco')

    if novo_preco_str:
        try:
            # Tenta converter para Decimal e valida se é positivo
            novo_preco = Decimal(novo_preco_str.replace(',', '.')) # Aceita vírgula ou ponto
            if novo_preco >= 0:
                item.preco = novo_preco
                item.save()
                messages.success(request, f"Preço de '{item.nome}' atualizado para R$ {novo_preco:.2f}.")
            else:
                messages.error(request, "O preço não pode ser negativo.")
        except InvalidOperation:
            messages.error(request, "Valor de preço inválido.")
        except Exception as e:
             messages.error(request, f"Erro ao atualizar preço: {e}")
    else:
        messages.warning(request, "Nenhum novo preço fornecido.")

    return redirect('gerenciar_cardapio')


@login_required
@user_passes_test(is_staff_user, login_url='inicio')
# Não precisa @require_POST aqui, pois o link GET é seguro (só muda um booleano)
def toggle_ativo_item(request, id):
    item = get_object_or_404(ItemCardapio, id=id)
    item.ativo = not item.ativo # Inverte o valor booleano
    item.save()
    status = "ativado" if item.ativo else "desativado"
    messages.info(request, f"Item '{item.nome}' foi {status}.")
    return redirect('gerenciar_cardapio')