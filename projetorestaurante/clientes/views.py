from django.shortcuts import render, redirect
from .models import Pessoa

# Create your views here.

def home(request):
    pessoas = Pessoa.objects.all()
    return render(request,"index.html",{"pessoas":pessoas})



def salvar(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        telefone = request.POST.get("telefone")
        email = request.POST.get("email")
        quantidade = request.POST.get("quantidade")
        
        # Cria a pessoa e pega o objeto salvo
        pessoa = Pessoa.objects.create(
            nome=nome,
            telefone=telefone,
            email=email,
            quantidade=quantidade
        )
        
        # Redireciona para a página de posição, passando o ID
        return redirect("posicao", id=pessoa.id)
    
 
def posicao(request, id):
    pessoa = Pessoa.objects.get(id=id)
    
    # Contar quantos clientes estão antes na fila
    posicao_fila = Pessoa.objects.filter(id__lte=pessoa.id).count()
    
    return render(request, "posicao.html", {"posicao": posicao_fila})



def delete(request, id):
    pessoa = Pessoa.objects.get(id = id)
    pessoa.delete()
    return redirect(home)

