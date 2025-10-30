# comandas/admin.py
from django.contrib import admin
from .models import Mesa, Comanda, ItemComanda

admin.site.register(Mesa)
admin.site.register(Comanda)
admin.site.register(ItemComanda)