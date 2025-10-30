# Arquivo: cardapio/forms.py

from django import forms
from .models import Categoria, ItemCardapio
# Importar o ItemEstoque para que possamos usá-lo
from estoque.models import ItemEstoque 

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'})
        }
        labels = {
            'nome': 'Nome da Categoria'
        }

class ItemCardapioForm(forms.ModelForm):
    class Meta:
        model = ItemCardapio
        # --- CORREÇÃO AQUI: Adicionado 'item_estoque' ---
        fields = ['categoria', 'nome', 'descricao', 'preco', 'imagem', 'ativo', 'item_estoque']
        # --- FIM DA CORREÇÃO ---
        
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'preco': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'imagem': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}), # Widget para o booleano
            
            # --- WIDGET ADICIONADO ---
            'item_estoque': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'nome': 'Nome do Item',
            'descricao': 'Descrição',
            'preco': 'Preço (R$)',
            'imagem': 'Imagem do Prato',
            'categoria': 'Categoria',
            'ativo': 'Item Ativo (visível no cardápio)',
            
            # --- LABEL ADICIONADA ---
            'item_estoque': 'Item de Estoque Vinculado (Opcional)'
        }

    # Adicionamos o __init__ para customizar o campo de estoque
    def __init__(self, *args, **kwargs):
        super(ItemCardapioForm, self).__init__(*args, **kwargs)
        # Torna o campo 'item_estoque' não obrigatório (já que é blank=True no modelo)
        self.fields['item_estoque'].required = False
        # Adiciona um texto "vazio" amigável
        self.fields['item_estoque'].empty_label = "Nenhum (Item não controlável)"