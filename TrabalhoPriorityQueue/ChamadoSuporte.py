from enum import Enum
from datetime import datetime, timedelta

from pydantic import BaseModel

class tipoCliente(Enum):
    PRIORITARIO = 1
    SEM_PRIORIDADE = 2
    DEMONSTRACAO = 3

class tipoChamado(Enum):
    SERVER_DOWN = 1
    IMPACTA_PRODUCAO = 2
    SEM_IMPACTO = 3
    DUVIDA = 4

class ChamadoSuporteModel(BaseModel):
    id_chamado: int
    cliente_nome: str
    tipo_cliente: tipoCliente
    tipo_chamado: tipoChamado
    descricao: str
    timestamp: datetime

class ChamadoSuporte:

    def __init__(
        self,
        id_chamado: int,
        cliente_nome: str,
        tipo_cliente: tipoCliente,
        tipo_chamado: tipoChamado,
        descricao: str,
        timestamp: datetime
    ):
        self.id_chamado = id_chamado
        self.cliente_nome = cliente_nome
        self.descricao = descricao
        self.timestamp = timestamp
        self.prioridade_escalada = None

        #Ve se o tipo_cliente está no enum tipoCliente
        if isinstance(tipo_cliente, tipoCliente):
            self.tipo_cliente = tipo_cliente
        elif tipo_cliente in [item.value for item in tipoCliente]:
            self.tipo_cliente = tipoCliente(tipo_cliente)
        else:
            valid_options = ', '.join([item.name for item in tipoCliente])
            raise ValueError(f"Tipo de cliente inválido: {tipo_cliente}. Opções: {valid_options}")

        #Mesma coisa com o tipo_chamado
        if isinstance(tipo_chamado, tipoChamado):
            self.tipo_chamado = tipo_chamado
        elif tipo_chamado in [item.value for item in tipoChamado]:
            self.tipo_chamado = tipoChamado(tipo_chamado)
        else:
            valid_options = ', '.join([item.name for item in tipoChamado])
            raise ValueError(f"Tipo de chamado inválido: {tipo_chamado}. Opções: {valid_options}")
        
        self.tempo_estimado_resolucao = self._definir_tempo_estimado()
        
        
    def _definir_tempo_estimado(self) -> timedelta:
        """Define tempo de resolução com base no tipo de chamado"""
        if self.tipo_chamado == tipoChamado.SERVER_DOWN:
            return timedelta(hours=1)
        elif self.tipo_chamado == tipoChamado.IMPACTA_PRODUCAO:
            return timedelta(hours=4)
        elif self.tipo_chamado == tipoChamado.SEM_IMPACTO:
            return timedelta(hours=24)
        elif self.tipo_chamado == tipoChamado.DUVIDA:
            return timedelta(hours=48)
        return timedelta(hours=72)
    
    def calcular_prioridade_total(self):
        """Retorna tuple com (tipo_chamado, tipo_cliente)"""
        if self.prioridade_escalada is not None:
            return self.prioridade_escalada
        prioridade_total = (self.tipo_chamado.value, self.tipo_cliente.value)
        return prioridade_total
    
    def escala_prioridade(self, novo_tipo_chamado = None, novo_tipo_cliente = None):
        """Escalar manualmente a prioridade de um chamado"""
        if novo_tipo_chamado is None:
            novo_tipo_chamado = self.tipo_chamado
        
        if novo_tipo_cliente is None:
            novo_tipo_cliente = self.tipo_cliente
        self.prioridade_escalada = (novo_tipo_chamado.value, novo_tipo_cliente.value)

    
    def to_dict(self) -> dict:
        """"Serializa chamado para dicionário pra facilitar a conversão pra JSON quando formos fazer a API"""
        return {
            "id_chamado": self.id_chamado,
            "cliente_nome": self.cliente_nome,
            "tipo_cliente": self.tipo_cliente.value,
            "tipo_chamado": self.tipo_chamado.value,
            "descricao": self.descricao,
            "timestamp": self.timestamp.isoformat(),
            "prioridade_escalada": self.prioridade_escalada,
            "tempo_estimado_resolucao": self.tempo_estimado_resolucao.total_seconds()
        }
    
    def from_dict(cls, data: dict) -> dict:
        """Deserializa de dicionário"""
        chamado = cls(
            id_chamado = data['id_chamado'],
            cliente_nome = data['cliente_nome'],
            tipo_cliente = data['tipo_cliente'],
            tipo_chamado = data['tipo_chamado'],
            descricao = data['descricao'],
            timestamp = datetime.fromisoformat(data['timestamp'])
        )
        if data.get("prioridade_escalada"):
            chamado.prioridade_escalada = tuple(data["prioridade_escalada"])
        if data.get("tempo_estimado_resolucao"):
            chamado.tempo_estimado_resolucao = timedelta(seconds=float(data["tempo_estimado_resolucao"]))
        return chamado
