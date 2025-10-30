# Arquivo: estoque/forms.py

from django import forms
from .models import ItemEstoque

class ItemEstoqueForm(forms.ModelForm):
    """
    Formulário para CRIAR um novo item no estoque.
    """
    class Meta:
        model = ItemEstoque
        fields = ['nome', 'quantidade_atual', 'ponto_reposicao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'quantidade_atual': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'value': '0'}),
            'ponto_reposicao': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }
        labels = {
            'nome': 'Nome do Item no Estoque',
            'quantidade_atual': 'Quantidade Inicial',
            'ponto_reposicao': 'Ponto de Reposição (Nível Mínimo)',
        }
        help_texts = {
            'nome': 'Ex: Coca-Cola Lata 350ml, Garrafa Vinho X, Dose Jack Daniels',
        }