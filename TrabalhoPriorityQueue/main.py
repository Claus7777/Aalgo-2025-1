import heapq
from notifypy import Notify
from fastapi import FastAPI
import ChamadoSuporte
from ChamadoSuporte import ChamadoSuporte, ChamadoSuporteModel

class PriorityQueue:
    def __init__(self):
        self._heap = []

    def push(self, prioridade_combinada_tuple, timestamp, chamado_obj):
        heapq.heappush(self._heap, (prioridade_combinada_tuple, timestamp, chamado_obj))

        self._enviar_notificacao_desktop("Novo chamado adicionado", "Resolva!")

    def pop(self):
        return heapq.heappop(self._heap)
    
    def is_empty(self):
        return len(self._heap) == 0
    
    def _enviar_notificacao_desktop(self, titulo, mensagem):
        """Mostra notificações no desktop utilizando plyer"""
        try:
            notification = Notify()
            notification.title = titulo
            notification.message = mensagem
            notification.application_name = "Chamado Suporte"
            notification.send()
        except Exception as e:
            print(f"Falha na notificação: {e}")
    
    def processar_proximo_chamado(self):
        if not self.is_empty():
            chamado_tuple = self.pop()
            # chamado_tuple is (prioridade_combinada_tuple, timestamp, chamado_obj)
            prioridade_combinada_tuple, timestamp, chamado_objeto = chamado_tuple
            print(f"Processando chamado: {chamado_objeto.to_dict()}")
            processarChamado(chamado_objeto)
            # imprima

app = FastAPI()
pq = PriorityQueue()

@app.post("/chamado", response_model=ChamadoSuporteModel)
def adicionar_chamado(chamado_obj: ChamadoSuporteModel):
    """
    Adiciona um chamado à fila de prioridade.
    Exemplo de uso: POST /chamado com o corpo do chamado.
    """
    # Converte o objeto ChamadoSuporteModel para um objeto ChamadoSuporte
    chamado_obj = ChamadoSuporte(
        id_chamado=chamado_obj.id_chamado,
        cliente_nome=chamado_obj.cliente_nome,
        tipo_cliente=chamado_obj.tipo_cliente,
        tipo_chamado=chamado_obj.tipo_chamado,
        descricao=chamado_obj.descricao,
        timestamp=chamado_obj.timestamp
    )
    prioridade_combinada_tuple = chamado_obj.calcular_prioridade_total()
    timestamp = chamado_obj.timestamp
    pq.push(prioridade_combinada_tuple, timestamp, chamado_obj)
    return chamado_obj.to_dict()

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

    print(chamado_obj.tipo_chamado.name)

    if chamado_obj.tipo_chamado.name in tipo_chamado_map:
        pq._enviar_notificacao_desktop(
            tipo_chamado_map[chamado_obj.tipo_chamado.name],
            f"""Cliente 
            {chamado_obj.cliente_nome} 
            ({chamado_obj.tipo_cliente.name})\nTipo:
            {chamado_obj.tipo_chamado.name}\nDescrição:
            {chamado_obj.descricao[:50]}...""",
        )