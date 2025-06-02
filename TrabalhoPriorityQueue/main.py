import heapq
from plyer import notification

class PriorityQueue:
    def __init__(self):
        self._heap = []

    def push(self, prioridade_combinada_tuple, timestamp, chamado_obj):
        heapq.heappush(self._heap, (prioridade_combinada_tuple, timestamp, chamado_obj))

        self._show_notification("Novo chamado adicionado", "Resolva!")

    def pop(self):
        return heapq.heappop(self._heap)[-1]
    
    def is_empty(self):
        return len(self._heap) == 0
    
    def _show_notification(titulo, mensagem):
        """Mostra notificaçõesn no desktop utilizando plyer"""
        try:
            notification.notify(
                title = titulo,
                message = mensagem,
                app_name = "Chamado Suporte",
                timeout = 3
            )
        except Exception as e:
            print(f"Falha na notificação: {e}")
    
pq = PriorityQueue()

