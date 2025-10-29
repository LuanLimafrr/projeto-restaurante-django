# Arquivo: reservas/models.py

from django.db import models
from django.utils import timezone
# Importar User para a ForeignKey
from django.contrib.auth.models import User

class Reserva(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('CONFIRMADA', 'Confirmada'),
        ('CANCELADA', 'Cancelada'),
    ]
    # Campo que liga a reserva ao usuário logado
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='reservas') # null=True permite que as migrações funcionem em dados antigos

    # Campos principais (nome/tel foram removidos)
    data = models.DateField()
    hora = models.TimeField()
    quantidade_pessoas = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDENTE')
    timestamp_criacao = models.DateTimeField(auto_now_add=True) # Guarda quando foi criada

    def __str__(self):
        # Usa o nome completo do usuário se disponível
        nome = self.usuario.get_full_name() if self.usuario else "Usuário Desconhecido" # Fallback
        return f"Reserva de {nome} para {self.data.strftime('%d/%m')} às {self.hora.strftime('%H:%M')}"

    # Método para pegar o email do usuário associado
    def get_email_cliente(self):
        return self.usuario.email if self.usuario and self.usuario.email else None