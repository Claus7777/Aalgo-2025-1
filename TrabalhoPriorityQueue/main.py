import heapq
from plyer import notification
from fastapi import FastAPI
import ChamadoSuporte

class PriorityQueue:
    def __init__(self):
        self._heap = []

    def push(self, prioridade_combinada_tuple, timestamp, chamado_obj):
        heapq.heappush(self._heap, (prioridade_combinada_tuple, timestamp, chamado_obj))

        self._enviar_notificacao_desktop("Novo chamado adicionado", "Resolva!")

    def pop(self):
        return heapq.heappop(self._heap)[-1]
    
    def is_empty(self):
        return len(self._heap) == 0
    
    def _enviar_notificacao_desktop(self, titulo, mensagem):
        """Mostra notificações no desktop utilizando plyer"""
        try:
            notification.notify(
                title = titulo,
                message = mensagem,
                app_name = "Chamado Suporte",
                timeout = 3
            )
        except Exception as e:
            print(f"Falha na notificação: {e}")
    
    def processar_proximo_chamado(self):
        if not self.is_empty():
            chamado = self.pop()
            print(f"Processando chamado: {chamado.to_dict()}")
            # Extrai prioridade_combinada_tuple, timestamp e chamado_objeto da tupla recuperada.
            prioridade_combinada_tuple, timestamp, chamado_objeto = chamado
            processarChamado(chamado_objeto)
            # imprima
        else:
            print("Nenhum chamado na fila.")

app = FastAPI()
pq = PriorityQueue()

@app.post("/chamado")
def adicionar_chamado(chamado_obj: ChamadoSuporte):
    """
    Adiciona um chamado à fila de prioridade.
    Exemplo de uso: POST /chamado com o corpo do chamado.
    """
    prioridade_combinada_tuple = chamado_obj.calcular_prioridade_total()
    timestamp = chamado_obj.timestamp
    pq.push(prioridade_combinada_tuple, timestamp, chamado_obj)
    return {"message": "Chamado adicionado com sucesso!"}

@app.get("/proximo_chamado")
def processar_proximo_chamado():
    """
    Processa o próximo chamado na fila de prioridade.
    Exemplo de uso: GET /processar_proximo_chamado
    """
    pq.processar_proximo_chamado()
    return {"message": "Próximo chamado processado!"}

def processarChamado(chamado_obj):
    tipo_chamado_map = {
        "SERVER_DOWN": "Chamado de servidor fora do ar",
        "IMPACTA_PRODUCAO": "Chamado que impacta a produção",
        "SEM_IMPACTO": "Chamado sem impacto",
        "DUVIDA": "Chamado de dúvida",
    }


    if chamado_obj.tipo_chamado in tipo_chamado_map:
        pq._enviar_notificacao_desktop(
            tipo_chamado_map[chamado_obj.tipo_chamado],
            f"""Cliente 
            {chamado_obj.cliente_nome} 
            ({chamado_obj.tipo_cliente})\nTipo:
            {chamado_obj.tipo_chamado}\nDescrição:
            {chamado_obj.descricao[:50]}...""",
        )