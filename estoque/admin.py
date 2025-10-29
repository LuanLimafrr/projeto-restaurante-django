# Arquivo: estoque/admin.py

from django.contrib import admin
from .models import ItemEstoque

@admin.register(ItemEstoque)
class ItemEstoqueAdmin(admin.ModelAdmin):
    list_display = ('nome', 'quantidade_atual', 'ponto_reposicao', 'em_alerta_de_estoque')
    search_fields = ('nome',)
    list_filter = ('quantidade_atual', 'ponto_reposicao')
    list_editable = ('quantidade_atual', 'ponto_reposicao') # Permite editar direto na lista

    @admin.display(boolean=True, description='Alerta de Estoque?')
    def em_alerta_de_estoque(self, obj):
        if obj.ponto_reposicao is not None:
            return obj.quantidade_atual <= obj.ponto_reposicao
        return False