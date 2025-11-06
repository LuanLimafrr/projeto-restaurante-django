# Arquivo: reservas/forms.py

from django import forms
from .models import Reserva # Importa o modelo Reserva
import datetime # Importa datetime para validação de hora

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva # Indica qual modelo este formulário representa

        # A lista 'fields' contém apenas os campos que o cliente precisa preencher
        fields = ['data', 'hora', 'quantidade_pessoas']

        # Widgets para estilização (Bootstrap) e configuração
        widgets = {
            'data': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control'
            }),
            
            # --- CORREÇÃO AQUI ---
            'hora': forms.TimeInput(attrs={
                'type': 'time', 
                'step': '1800',  # 1800 segundos = 30 minutos
                'class': 'form-control'
            }), 
            # --- FIM DA CORREÇÃO ---
            
            'quantidade_pessoas': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': '1'
            }), 
        }
        
        # Labels para deixar os nomes mais amigáveis
        labels = {
            'data': 'Data da Reserva',
            'hora': 'Horário (Intervalos de 30 min)', # Label atualizada
            'quantidade_pessoas': 'Número de Pessoas',
        }

    # --- VALIDAÇÃO ADICIONAL (BOA PRÁTICA) ---
    # Garante que o horário seja em incrementos de 30 minutos
    def clean_hora(self):
        hora = self.cleaned_data.get('hora')
        
        # Verifica se a hora foi fornecida
        if hora:
            # Permite :00 ou :30
            if hora.minute not in [0, 30]:
                raise forms.ValidationError("Por favor, selecione um horário em intervalos de 30 minutos (ex: 19:00 ou 19:30).")
            
            # (Opcional) Adicione aqui sua lógica de horário de funcionamento
            # Ex: if hora < datetime.time(18, 0) or hora > datetime.time(22, 0):
            #         raise forms.ValidationError("Reservas disponíveis apenas das 18:00 às 22:00.")
            
        return hora

    # (Opcional) Validação para não permitir datas no passado
    def clean_data(self):
        data = self.cleaned_data.get('data')
        if data and data < datetime.date.today():
            raise forms.ValidationError("Não é possível fazer reservas para datas passadas.")
        return data