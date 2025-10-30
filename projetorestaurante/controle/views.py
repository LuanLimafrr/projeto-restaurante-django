from django.shortcuts import render, get_object_or_404, redirect
from clientes.models import Pessoa
from django.contrib.auth.decorators import login_required

def controle(request):
    clientes = Pessoa.objects.all()
    return render(request, "restaurante.html", {"clientes": clientes})

def proximo(request, id):
    # pega o cliente (ou retorna 404 se não existir)
    cliente = get_object_or_404(Pessoa, id=id)

    # remove o cliente (chamar quando realmente quiser tirar da fila)
    cliente.delete()

    # redireciona para a página de controle
    # 1) se você tem um nome de URL 'controle' em urls.py:
    return redirect('controle')

@login_required
def controle(request):
    clientes = Pessoa.objects.all()
    return render(request, "restaurante.html", {"clientes": clientes})
