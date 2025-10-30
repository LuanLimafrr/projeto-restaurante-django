# Arquivo: fila/context_processors.py

from .models import ClienteFila
from reservas.models import Reserva # Importar model de reservas

def informacoes_fila(request):
    """
    Context processor para o BALÃO DE CLIENTE.
    Verifica a sessão do cliente.
    """
    contexto = {
        'id_cliente_na_fila': None,
        'posicao_cliente_na_fila': 0,
        'status_cliente_na_fila': None,
    }
    id_cliente_sessao = request.session.get('id_cliente_fila')
    if id_cliente_sessao:
        try:
            cliente_atual = ClienteFila.objects.get(id=id_cliente_sessao)
            if cliente_atual.status == 'AGUARDANDO':
                clientes_aguardando_antes = ClienteFila.objects.filter(
                    status='AGUARDANDO',
                    timestamp_entrada__lt=cliente_atual.timestamp_entrada
                ).count()
                contexto['id_cliente_na_fila'] = cliente_atual.id
                contexto['posicao_cliente_na_fila'] = clientes_aguardando_antes + 1
                contexto['status_cliente_na_fila'] = 'AGUARDANDO'
            else:
                contexto['status_cliente_na_fila'] = cliente_atual.status
                # Não limpa a sessão aqui, deixa o JS do balão tratar
        except ClienteFila.DoesNotExist:
            if 'id_cliente_fila' in request.session:
                del request.session['id_cliente_fila']
    return contexto


# --- NOVA FUNÇÃO ADICIONADA ---
def staff_notifications(request):
    """
    Context processor para os BADGES DE NOTIFICAÇÃO DO STAFF.
    Busca contagem de pendências.
    """
    if request.user.is_authenticated and request.user.is_staff:
        # Contar clientes aguardando na fila
        fila_pendente_count = ClienteFila.objects.filter(status='AGUARDANDO').count()
        # Contar reservas com status pendente
        reservas_pendente_count = Reserva.objects.filter(status='PENDENTE').count()
        
        return {
            'fila_pendente_count': fila_pendente_count,
            'reservas_pendente_count': reservas_pendente_count,
        }
    return {} # Retorna vazio se não for staff