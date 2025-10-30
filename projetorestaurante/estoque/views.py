# Arquivo: estoque/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import ItemEstoque
from decimal import Decimal, InvalidOperation
from .forms import ItemEstoqueForm # <-- 1. IMPORTAR O NOVO FORM
from cardapio.views import is_staff_user # Helper de staff

@login_required
@user_passes_test(is_staff_user, login_url='inicio')
def gerenciar_estoque(request):
    """
    Mostra a lista de itens e o formulário de novo item (no modal).
    """
    itens_estoque = ItemEstoque.objects.all().order_by('nome')
    for item in itens_estoque:
        item.alerta_estoque = (
            item.ponto_reposicao is not None and
            item.quantidade_atual <= item.ponto_reposicao
        )

    # --- 2. ADICIONAR FORM VAZIO AO CONTEXTO ---
    # Verifica se há um form com erros vindo da view 'criar_novo_item_estoque'
    if 'form_novo_item_invalido' in request.session:
        form_novo_item = ItemEstoqueForm(request.session.pop('form_novo_item_invalido'))
    else:
        form_novo_item = ItemEstoqueForm() # Cria um form vazio
    
    contexto = {
        'itens_estoque': itens_estoque,
        'form_novo_item': form_novo_item, # Passa o form para o modal
    }
    return render(request, 'estoque/gerenciar_estoque.html', contexto)

# --- 3. CRIAR NOVA VIEW PARA O POST DO MODAL ---
@login_required
@user_passes_test(is_staff_user, login_url='inicio')
@require_POST
def criar_novo_item_estoque(request):
    form = ItemEstoqueForm(request.POST)
    if form.is_valid():
        try:
            form.save()
            messages.success(request, f"Novo item '{form.cleaned_data['nome']}' criado no estoque.")
        except Exception as e: # Captura erros (ex: 'unique=True' no nome)
            messages.error(request, f"Erro ao criar item: {e}")
    else:
         # Salva o form inválido na sessão para exibi-lo no modal
         request.session['form_novo_item_invalido'] = request.POST
         messages.error(request, "Erro no formulário. Verifique os campos.")
    
    return redirect('gerenciar_estoque') # Redireciona de volta para a lista

# View para adicionar quantidade (sem mudanças)
@login_required
@user_passes_test(is_staff_user, login_url='inicio')
@require_POST
def adicionar_estoque_item(request, id_item):
    item = get_object_or_404(ItemEstoque, id=id_item)
    quantidade_str = request.POST.get('quantidade_adicionar')
    if not quantidade_str:
        messages.error(request, "Quantidade não fornecida.")
        return redirect('gerenciar_estoque')
    try:
        quantidade = int(quantidade_str)
        if quantidade <= 0:
            messages.error(request, "A quantidade a adicionar deve ser positiva.")
        else:
            item.adicionar_estoque(quantidade)
            messages.success(request, f"{quantidade} un. adicionadas ao estoque de '{item.nome}'.")
    except (ValueError, TypeError):
        messages.error(request, "Valor de quantidade inválido.")
    except Exception as e:
         messages.error(request, f"Erro inesperado: {e}")
    return redirect('gerenciar_estoque')