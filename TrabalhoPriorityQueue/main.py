import heapq
from notifypy import Notify
from fastapi import FastAPI
import ChamadoSuporte
from ChamadoSuporte import AgenteSuporte, ChamadoSuporte, ChamadoSuporteModel, tipoChamado, tipoCliente
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.exception_handlers import RequestValidationError
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from typing import Optional

class PriorityQueue:
    def __init__(self):
        self._heap = []
        self._chamados_map = {} 

    def push(self, prioridade_combinada_tuple, timestamp, chamado_obj):
        heapq.heappush(self._heap, (prioridade_combinada_tuple, timestamp, chamado_obj))

        self._enviar_notificacao_desktop("Novo chamado adicionado", "Resolva!")
    
    def remove(self, id_chamado: int):
        """Remove logicamente o chamado da fila"""
        if id_chamado in self._chamados_map:
            del self._chamados_map[id_chamado]
        else:
            raise KeyError("Chamado não está na fila")

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
indice_agente = 0
chamados_repo = {}
agentes_disponiveis = [
    AgenteSuporte(id_agente=1, nome="Alice"),
    AgenteSuporte(id_agente=2, nome="Bob"),
    AgenteSuporte(id_agente=3, nome="Carlos"),
]

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
        chamado_obj.agente_atribuido = atribuir_agente()
        prioridade_combinada_tuple = chamado_obj.calcular_prioridade_total()
        timestamp = chamado_obj.timestamp
        pq.push(prioridade_combinada_tuple, timestamp, chamado_obj)
        chamados_repo[chamado_obj.id_chamado] = chamado_obj
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

@app.put("/escalar_chamado/{id_chamado}")
def escalar_prioridade_chamado(id_chamado: int, novo_tipo_chamado: Optional[int] = None, novo_tipo_cliente: Optional[int] = None):
    """
    Escala a prioridade de um chamado existente.
    Exemplo: PUT /escalar_chamado/1?novo_tipo_chamado=1&novo_tipo_cliente=1
    """
    chamado = chamados_repo.get(id_chamado)
    if not chamado:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Chamado não encontrado.")

    try:
        # Converte inteiros para Enums, se fornecidos
        if novo_tipo_chamado is not None:
            novo_tipo_chamado = tipoChamado(novo_tipo_chamado)
        if novo_tipo_cliente is not None:
            novo_tipo_cliente = tipoCliente(novo_tipo_cliente)
        
        try:
            pq.remove(chamado.id_chamado)
        except KeyError:
            pass 
    
        chamado.escala_prioridade(novo_tipo_chamado, novo_tipo_cliente)

        prioridade_nova = chamado.calcular_prioridade_total()
        pq.push(prioridade_nova, chamado.timestamp, chamado)
        
        return {"message": "Prioridade escalada com sucesso.", "chamado": chamado.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=f"Erro ao escalar prioridade: {str(e)}")

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

@app.get("/chamados/agente/{id_agente}")
def listar_chamados_por_agente(id_agente: int):
    chamados = [
        c.to_dict()
        for c in chamados_repo.values()
        if c.agente_atribuido and c.agente_atribuido.id_agente == id_agente
    ]
    return chamados

def atribuir_agente():
    global indice_agente
    agente = agentes_disponiveis[indice_agente % len(agentes_disponiveis)]
    indice_agente += 1
    return agente