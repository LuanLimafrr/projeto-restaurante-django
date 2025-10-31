# comandas/forms.py

from django import forms
from cardapio.models import ItemCardapio
from .models import Mesa  # <-- IMPORTAÇÃO OK

# --- SEU FORMULÁRIO EXISTENTE (Sem mudanças) ---
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

# --- FORMULÁRIO DE MESA (CORRIGIDO) ---
class MesaForm(forms.ModelForm):
    class Meta:
        model = Mesa
        # CORREÇÃO AQUI: Removido 'capacidade'
        fields = ['numero'] 
        widgets = {
            'numero': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Número da Mesa'}),
            # CORREÇÃO AQUI: Removido widget 'capacidade'
        }

    # Esta função garante que o número da mesa não seja duplicado
    def clean_numero(self):
        numero = self.cleaned_data.get('numero')
        if Mesa.objects.filter(numero=numero).exists():
            raise forms.ValidationError("Uma mesa com este número já existe.")
        return numero