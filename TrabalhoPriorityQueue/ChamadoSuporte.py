from enum import Enum
from datetime import datetime

class tipoCliente(Enum):
    PRIORITARIO = 1
    SEM_PRIORIDADE = 2
    DEMONSTRACAO = 3

class tipoChamado(Enum):
    SERVER_DOWN = 1
    IMPACTA_PRODUCAO = 2
    SEM_IMPACTO = 3
    DUVIDA = 4

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
    
    def calcular_prioridade_total(self):
        """Retorn tuple com (tipo_chamado, tipo_cliente)"""
        prioridade_total = (self.tipo_chamado, self.tipo_cliente)
        return prioridade_total
    
    def to_dict(self) -> dict:
        """"Serializa chamado para dicionário pra facilitar a conversão pra JSON quando formos fazer a API"""
        return {
            "id_chamado": self.id_chamado,
            "cliente_nome": self.cliente_nome,
            "tipo_cliente": self.tipo_cliente.name,
            "tipo_chamado": self.tipo_chamado.name,
            "descricao": self.descricao,
            "timestamp": self.timestamp.isoformat(),
        }
    
    def from_dict(cls, data: dict) -> dict:
        """Deserializa de dicionário"""
        return cls(
            id_chamado = data['id_chamado'],
            cliente_nome = data['cliente_nome'],
            tipo_cliente = data['tipo_cliente'],
            tipo_chamado = data['tipo_chamado'],
            descricao = data['descricao'],
            timestamp = datetime.fromisoformat(data['timestamp'])
        )