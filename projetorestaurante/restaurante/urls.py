# Arquivo: restaurante/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cardapio/', include('cardapio.urls')),
    path('reservar/', include('reservas.urls')),
    path('comandas/', include('comandas.urls')),
    path('contas/', include('usuarios.urls')),
    
    # --- NOVA LINHA ADICIONADA ---
    path('estoque/', include('estoque.urls')),
    # --- FIM DA NOVA LINHA ---
    
    path('', include('fila.urls')), # Fila na raiz
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)