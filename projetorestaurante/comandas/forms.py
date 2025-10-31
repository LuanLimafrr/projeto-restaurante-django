# comandas/forms.py

from django import forms
from cardapio.models import ItemCardapio
from .models import Mesa  # <-- ADICIONE ESTA IMPORTAÇÃO

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

# --- NOVO FORMULÁRIO PARA ADICIONAR MESAS ---
class MesaForm(forms.ModelForm):
    class Meta:
        model = Mesa
        # Assumindo que seu modelo 'Mesa' tem 'numero' e 'capacidade'
        fields = ['numero', 'capacidade'] 
        widgets = {
            'numero': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Número da Mesa'}),
            'capacidade': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Capacidade (pessoas)'}),
        }

    # Esta função garante que o número da mesa não seja duplicado
    def clean_numero(self):
        numero = self.cleaned_data.get('numero')
        # Verifica se já existe uma mesa com esse número (ignorando a si mesma, caso seja uma edição)
        if Mesa.objects.filter(numero=numero).exists():
            raise forms.ValidationError("Uma mesa com este número já existe.")
        return numero