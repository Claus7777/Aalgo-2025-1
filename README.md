🛠️ Sistema de Chamados de Suporte com Prioridade

Este é um sistema de gerenciamento de chamados de suporte técnico que utiliza uma fila de prioridade para organizar e processar os chamados com base no tipo de cliente e tipo de problema. A API é construída com FastAPI e oferece notificações desktop ao adicionar ou processar chamados.
🚀 Funcionalidades

    📥 Adicionar chamados à fila com prioridade.

    ⏩ Processar o próximo chamado com maior prioridade.

    🔔 Notificações de desktop para novos chamados e chamados processados.

    🧠 Classificação automática com base em enums definidos para tipo de cliente e tipo de chamado.

🧱 Tecnologias Utilizadas

    FastAPI - Web framework moderno para construção da API.

    Pydantic - Validação de dados.

    notifypy - Envio de notificações de desktop.

    Python heapq - Estrutura de dados de fila de prioridade (heap).


📬 Endpoints da API
POST /chamado

Adiciona um chamado à fila de prioridade.
Exemplo de corpo da requisição:

{
  "id_chamado": 101,
  "cliente_nome": "Empresa XYZ",
  "tipo_cliente": 1,
  "tipo_chamado": 2,
  "descricao": "Sistema lento durante operação crítica",
  "timestamp": "2025-06-26T15:30:00"
}

    tipo_cliente:

        1: PRIORITARIO

        2: SEM_PRIORIDADE

        3: DEMONSTRACAO

    tipo_chamado:

        1: SERVER_DOWN

        2: IMPACTA_PRODUCAO

        3: SEM_IMPACTO

        4: DUVIDA

GET /proximo_chamado

Processa o próximo chamado com maior prioridade na fila.
📋 Lógica de Priorização

Os chamados são organizados por uma tupla de prioridade:

(tipo_chamado.value, tipo_cliente.value)

Menores valores têm prioridade mais alta, ou seja:

    SERVER_DOWN (1) e PRIORITARIO (1) têm a maior prioridade.

    DUVIDA (4) e DEMONSTRACAO (3) têm a menor prioridade.

🖥️ Notificações Desktop

A cada chamado adicionado ou processado, uma notificação será exibida no desktop com o resumo do chamado.

    ⚠️ É necessário estar com o ambiente gráfico ativo (não funciona em servidores sem interface gráfica).
