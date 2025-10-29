# Arquivo: usuarios/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroUsuarioForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

# --- VIEW DE REGISTRO ---
def registrar(request):
    if request.user.is_authenticated: return redirect('perfil') # Se já logado, vai para perfil
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(); login(request, user)
            messages.success(request, f"Bem-vindo(a), {user.first_name}! Cadastro realizado.")
            return redirect('perfil') # Após cadastro, vai para perfil
        else: messages.error(request, "Erro no cadastro. Verifique os campos abaixo.")
    else: form = RegistroUsuarioForm()
    return render(request, 'registration/register.html', {'form': form})

# --- VIEW DE PERFIL ---
@login_required
def perfil(request):
    # Se for staff tentando acessar /perfil/, redireciona para o dashboard
    if request.user.is_staff: return redirect('mapa_mesas')
    # Mostra perfil do cliente
    return render(request, 'usuarios/perfil.html')

# --- LOGIN VIEW UNIFICADA (ATUALIZADA) ---
class CustomLoginViewUnificada(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url: return next_url # Respeita o parâmetro ?next=

        # --- MUDANÇA AQUI: Staff vai para mapa_mesas ---
        if self.request.user.is_staff:
            return reverse_lazy('mapa_mesas') # URL name do dashboard staff
        else:
            return reverse_lazy('perfil') # Cliente vai para o perfil
        # --- FIM DA MUDANÇA ---

    def form_invalid(self, form):
        messages.error(self.request, "Usuário ou senha inválidos.")
        return super().form_invalid(form)