from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

def inicio(request):

    return render(request, 'inicio.html')



def inicio(request):
    return render(request, 'inicio.html')

def login_restaurante(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        senha = request.POST.get('senha')

        user = authenticate(request, username=usuario, password=senha)
        if user is not None:
            login(request, user)
            return redirect('controle')  # nome da sua view do restaurante
        else:
            return render(request, 'login.html', {'erro': 'Usuário ou senha inválidos.'})
    return render(request, 'login.html')
