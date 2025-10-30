# Arquivo: comandas/models.py

from django.db import models
from django.utils import timezone
from cardapio.models import ItemCardapio
from decimal import Decimal

# --- Mesa (sem mudanças) ---
class Mesa(models.Model):
    STATUS_CHOICES = [('LIVRE', 'Livre'), ('OCUPADA', 'Ocupada'), ('PAGAMENTO', 'Pagamento')]
    numero = models.PositiveIntegerField(unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='LIVRE')
    def __str__(self): return f"Mesa {self.numero} ({self.get_status_display()})"

# --- Comanda (sem mudanças) ---
class Comanda(models.Model):
    STATUS_CHOICES = [('ABERTA', 'Aberta'), ('FECHADA', 'Fechada'), ('PAGA', 'Paga')]
    mesa = models.ForeignKey(Mesa, on_delete=models.PROTECT, related_name='comandas')
    timestamp_abertura = models.DateTimeField(default=timezone.now)
    timestamp_fechamento = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ABERTA')
    incluir_taxa_servico = models.BooleanField(default=True)
    def get_subtotal(self): return sum(item.get_total_item() for item in self.itens.all())
    def get_taxa_servico(self): return (self.get_subtotal() * Decimal('0.10')).quantize(Decimal('0.01')) if self.incluir_taxa_servico else Decimal(0)
    def get_total(self): return self.get_subtotal() + self.get_taxa_servico()
    def __str__(self): return f"Comanda da Mesa {self.mesa.numero} ({self.status})"

# --- ItemComanda (COM MUDANÇA) ---
class ItemComanda(models.Model):
    comanda = models.ForeignKey(Comanda, on_delete=models.CASCADE, related_name='itens')
    
    # --- MUDANÇA AQUI ---
    # Trocado 'on_delete=models.PROTECT' por 'on_delete=models.SET_NULL, null=True'
    item_cardapio = models.ForeignKey(
        ItemCardapio,
        on_delete=models.SET_NULL, # Se deletar o item do cardápio, seta este campo como NULO
        null=True # Permite que o campo seja NULO no banco
    )
    # --- FIM DA MUDANÇA ---
    
    quantidade = models.PositiveIntegerField(default=1)
    preco_unitario_momento = models.DecimalField(max_digits=8, decimal_places=2)
    observacao = models.TextField(blank=True, null=True, help_text="Ex: Sem cebola, ponto da carne")

    def save(self, *args, **kwargs):
        # Salva o preço no momento do pedido, se for um item novo E se o item_cardapio não for nulo
        if not self.id and self.item_cardapio:
            self.preco_unitario_momento = self.item_cardapio.preco
        # Garante que a quantidade não seja zero
        if self.quantidade < 1: self.quantidade = 1
        super().save(*args, **kwargs)

    def get_total_item(self):
        return self.preco_unitario_momento * self.quantidade

    def __str__(self):
        nome_item = self.item_cardapio.nome if self.item_cardapio else "[Item Removido]"
        obs = f" ({self.observacao})" if self.observacao else ""
        return f"{self.quantidade}x {nome_item}{obs} (R$ {self.get_total_item()})"