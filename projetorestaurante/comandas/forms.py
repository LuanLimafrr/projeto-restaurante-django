# comandas/forms.py

from django import forms
from cardapio.models import ItemCardapio

class ItemComandaForm(forms.Form):
    item_cardapio = forms.ModelChoiceField(
        queryset=ItemCardapio.objects.all().order_by('categoria__nome', 'nome'), # Ordenado!
        label="Item do Cardápio",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    quantidade = forms.IntegerField(
        label="Quantidade", initial=1, min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    observacao = forms.CharField(
        label="Observação (Opcional)", required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Sem cebola, ponto mal passado'})
    )