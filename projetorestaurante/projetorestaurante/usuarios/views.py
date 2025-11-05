# Arquivo: usuarios/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroUsuarioForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

# --- IMPORTAÇÃO NECESSÁRIA ---
# Importamos a função que verifica se o usuário está no grupo 'Gerente'
# Assumindo que ela está em 'cardapio/views.py' como você configurou
from cardapio.views import is_gerente 

# --- VIEW DE REGISTRO (Sem mudanças) ---
def registrar(request):
    if request.user.is_authenticated: return redirect('perfil') 
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(); login(request, user)
            messages.success(request, f"Bem-vindo(a), {user.first_name}! Cadastro realizado.")
            return redirect('perfil') 
        else: messages.error(request, "Erro no cadastro. Verifique os campos abaixo.")
    else: form = RegistroUsuarioForm()
    return render(request, 'registration/register.html', {'form': form})

# --- VIEW DE PERFIL (ATUALIZADA) ---
@login_required
def perfil(request):
    # --- LÓGICA DE REDIRECIONAMENTO INTELIGENTE ---
    if request.user.is_staff:
        if is_gerente(request.user):
            return redirect('mapa_mesas') # Gerente vai para o PDV Mesas
        else:
            return redirect('gerenciar_fila') # Recepcionista (ou outro staff) vai para a Fila
    # --- FIM DA LÓGICA ---
    
    # Mostra perfil do cliente (se não for staff)
    return render(request, 'usuarios/perfil.html')

# --- LOGIN VIEW UNIFICADA (ATUALIZADA) ---
class CustomLoginViewUnificada(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url: return next_url # Respeita o parâmetro ?next=

        # --- LÓGICA DE REDIRECIONAMENTO INTELIGENTE ---
        if self.request.user.is_staff:
            if is_gerente(self.request.user):
                return reverse_lazy('mapa_mesas') # Gerente vai para o PDV Mesas
            else:
                return reverse_lazy('gerenciar_fila') # Recepcionista vai para a Fila
        else:
            return reverse_lazy('perfil') # Cliente vai para o perfil
        # --- FIM DA LÓGICA ---

    def form_invalid(self, form):
        messages.error(self.request, "Usuário ou senha inválidos.")
        return super().form_invalid(form)