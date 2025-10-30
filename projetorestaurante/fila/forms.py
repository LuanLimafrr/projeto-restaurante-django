# Arquivo: fila/forms.py

from django import forms

class EntrarFilaForm(forms.Form):
    nome = forms.CharField(
        max_length=100, required=True, label="Nome Completo",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Seu nome'})
    )
    quantidade = forms.IntegerField(
        required=True, min_value=1, initial=1, label="Quantidade de Pessoas",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    # --- NOVOS CAMPOS ADICIONADOS ---
    telefone = forms.CharField(
        max_length=20, required=False, label="Telefone (Opcional)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(XX) XXXXX-XXXX'})
    )
    email = forms.EmailField(
        max_length=100, required=False, label="E-mail (Opcional)",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seuemail@exemplo.com'})
    )
    # --- FIM DOS NOVOS CAMPOS ---