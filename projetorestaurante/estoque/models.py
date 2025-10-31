# Arquivo: estoque/models.py

from django.db import models

class ItemEstoque(models.Model):
    nome = models.CharField(max_length=150, unique=True, help_text="Ex: Coca-Cola Lata 350ml, Garrafa Vinho Tinto X, Dose Jack Daniels")
    quantidade_atual = models.IntegerField(default=0, help_text="Quantidade atual em unidades.")
    
    # Opcional: Ponto de Reposição (para alertas futuros)
    ponto_reposicao = models.PositiveIntegerField(default=10, blank=True, null=True, help_text="Quantidade mínima para alerta de reposição.")

    class Meta:
        ordering = ['nome'] # Ordena alfabeticamente
        verbose_name = "Item em Estoque"
        verbose_name_plural = "Itens em Estoque"

    def __str__(self):
        alerta = ""
        if self.ponto_reposicao is not None and self.quantidade_atual <= self.ponto_reposicao:
            alerta = " [BAIXO ESTOQUE!]"
        return f"{self.nome} ({self.quantidade_atual} un.){alerta}"

    def adicionar_estoque(self, quantidade):
        """Adiciona uma quantidade ao estoque atual."""
        if quantidade > 0:
            self.quantidade_atual += quantidade
            self.save()
            return True
        return False

    def remover_do_estoque(self, quantidade):
        """Remove uma quantidade do estoque. Retorna False se não houver estoque suficiente."""
        if quantidade > 0 and self.quantidade_atual >= quantidade:
            self.quantidade_atual -= quantidade
            self.save()
            return True
        # Se não tiver estoque suficiente, não faz nada e avisa
        return False