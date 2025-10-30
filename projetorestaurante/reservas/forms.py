# Arquivo: reservas/forms.py

from django import forms
from .models import Reserva # Importa o modelo Reserva

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva # Indica qual modelo este formulário representa

        # A lista 'fields' contém apenas os campos que o cliente precisa preencher
        fields = ['data', 'hora', 'quantidade_pessoas']

        # Widgets para estilização (Bootstrap) e configuração
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora': forms.TimeInput(attrs={'type': 'time', 'step': '3600', 'class': 'form-control'}), # Step de 1 hora
            'quantidade_pessoas': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}), # Mínimo 1 pessoa
        }
        # Labels para deixar os nomes mais amigáveis
        labels = {
            'data': 'Data da Reserva',
            'hora': 'Horário (cheio)',
            'quantidade_pessoas': 'Número de Pessoas',
        }