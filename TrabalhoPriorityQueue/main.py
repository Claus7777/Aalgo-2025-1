import heapq
from notifypy import Notify
from fastapi import FastAPI
import ChamadoSuporte
from ChamadoSuporte import ChamadoSuporte, ChamadoSuporteModel
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.exception_handlers import RequestValidationError
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

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

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content={"detail": exc.errors(), "body": exc.body},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Erro interno do servidor."},
    )

@app.post("/chamado", response_model=ChamadoSuporteModel)
def adicionar_chamado(chamado_obj: ChamadoSuporteModel):
    """
    Adiciona um chamado à fila de prioridade.
    Exemplo de uso: POST /chamado com o corpo do chamado.
    """
    try:
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
    except Exception as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=f"Erro ao adicionar chamado: {str(e)}")

@app.get("/proximo_chamado")
def processar_proximo_chamado():
    """
    Processa o próximo chamado na fila de prioridade.
    Exemplo de uso: GET /processar_proximo_chamado
    """
    try:
        if pq.is_empty():
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Nenhum chamado na fila.")
        pq.processar_proximo_chamado()
        return {"message": "Próximo chamado processado!"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao processar chamado: {str(e)}")

def processarChamado(chamado_obj):
    tipo_chamado_map = {
        "SERVER_DOWN": "Chamado de servidor fora do ar",
        "IMPACTA_PRODUCAO": "Chamado que impacta a produção",
        "SEM_IMPACTO": "Chamado sem impacto",
        "DUVIDA": "Chamado de dúvida",
    }

    if chamado_obj.tipo_chamado.name in tipo_chamado_map:
        pq._enviar_notificacao_desktop(
            tipo_chamado_map[chamado_obj.tipo_chamado.name],
            f"""Cliente 
            {chamado_obj.cliente_nome} 
            ({chamado_obj.tipo_cliente.name})\nTipo:
            {chamado_obj.tipo_chamado.name}\nDescrição:
            {chamado_obj.descricao[:50]}...""",
        )