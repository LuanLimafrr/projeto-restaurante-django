# Arquivo: fila/models.py
from django.db import models
from django.utils import timezone

class ClienteFila(models.Model):
    STATUS_CHOICES = [
        ('AGUARDANDO', 'Aguardando'),
        ('CHAMADO', 'Chamado'), # Status quando alocado
        ('CANCELADO', 'Cancelado/Desistiu'),
        # ('ATENDIDO', 'Atendido'), # Se quiser um status pós-pagamento
    ]

    nome = models.CharField(max_length=100) # Era 50, aumentei
    quantidade = models.PositiveIntegerField()

    # --- NOVOS CAMPOS ADICIONADOS ---
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    # --- FIM DOS NOVOS CAMPOS ---

    timestamp_entrada = models.DateTimeField(default=timezone.now)
    timestamp_atendimento = models.DateTimeField(null=True, blank=True) # Guarda quando foi chamado/alocado
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='AGUARDANDO')

    def __str__(self):
        return f"{self.nome} ({self.quantidade}p) - {self.status}"