# cardapio/admin.py
from django.contrib import admin
from .models import Categoria, ItemCardapio

# Registra os modelos para que apareçam no /admin
admin.site.register(Categoria)
admin.site.register(ItemCardapio)