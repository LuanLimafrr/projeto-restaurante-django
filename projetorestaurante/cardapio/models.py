# Arquivo: cardapio/models.py
from django.db import models
# --- IMPORTAR MODELO DE ESTOQUE ---
from estoque.models import ItemEstoque

class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    class Meta: ordering = ['nome']
    def __str__(self): return self.nome

class ItemCardapio(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    imagem = models.ImageField(upload_to='pratos/', blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='itens')
    ativo = models.BooleanField(default=True, help_text="Desmarque para ocultar este item do cardápio público.")

    # --- NOVO CAMPO DE LIGAÇÃO (ForeignKey) ---
    item_estoque = models.ForeignKey(
        ItemEstoque,
        on_delete=models.SET_NULL, # Se deletar o item de estoque, não deleta o prato
        null=True,                 # Permite que o campo seja NULO
        blank=True,                # Permite que o campo seja VAZIO no admin
        related_name='itens_cardapio',
        help_text="Opcional: Ligue este item do cardápio a um item do estoque para controle."
    )
    # --- FIM DO NOVO CAMPO ---

    class Meta:
        ordering = ['categoria__nome', 'nome']

    def __str__(self):
        status = "" if self.ativo else " [INATIVO]"
        return f"{self.nome} ({self.categoria.nome}){status}"