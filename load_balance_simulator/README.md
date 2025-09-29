# Simulador de Load Balance - MC714

## Visão Geral

Este simulador implementa e compara diferentes políticas de balanceamento de carga em sistemas distribuídos, conforme solicitado no projeto de MC714.

## Funcionalidades Implementadas

### ✅ Requisitos Atendidos

1. **Três políticas de balanceamento obrigatórias:**

   - **Escolha Aleatória (Random)**: Seleciona servidor aleatoriamente
   - **Round Robin**: Distribui requisições igualmente entre servidores
   - **Fila Mais Curta (Shortest Queue)**: Direciona para servidor com menor fila

2. **Simulação de tráfego:**

   - Requisições chegam em intervalos aleatórios (distribuição exponencial)
   - Tipos variados: CPU-intensivo e I/O-intensivo
   - Padrões: constante e rajadas (burst)

3. **Simulação de servidores:**

   - 3 servidores configuráveis
   - Filas de requisições individuais
   - Tempos de processamento variáveis
   - Monitoramento de estado (ocupado/livre)

4. **Métricas implementadas:**
   - **Throughput** (vazão do sistema)
   - **Tempo médio de resposta**
   - **Tempo médio de espera**
   - **Utilização do sistema**
   - **Desvio padrão dos tempos**
   - **Distribuição de carga**

## Estrutura do Projeto

```
load_balance_simulator/
├── main.py                 # Interface principal
├── requirements.txt        # Dependências
├── config/
│   ├── __init__.py
│   └── settings.py         # Configurações e enums
└── src/
    ├── __init__.py
    ├── load_balancer.py     # Políticas de balanceamento
    ├── traffic_generator.py # Geração de tráfego
    ├── metrics_analyzer.py  # Análise e relatórios
    ├── models/
    │   ├── __init__.py
    │   ├── request.py       # Modelo de requisição
    │   └── server.py        # Modelo de servidor
    └── simulator/
        ├── __init__.py
        └── load_balance_simulator.py  # Simulador principal
```

## Como Executar

### 1. Configuração do Ambiente

```bash
# Clone ou navegue até o diretório do projeto
cd load_balance_simulator

# Crie ambiente virtual
python3 -m venv venv

# Ative o ambiente virtual
source venv/bin/activate

# Instale dependências
pip install simpy
```

### 2. Executando o Simulador

#### Modo Interativo (Recomendado)

```bash
python3 main.py
```

#### Modo Linha de Comando

```bash
# Análise completa (todas as políticas e padrões)
python3 main.py --full-analysis

# Comparar apenas políticas
python3 main.py --compare-policies

# Analisar padrões de tráfego
python3 main.py --traffic-analysis
```

## Exemplos de Uso

### 1. Simulação Única

Execute uma simulação com parâmetros específicos através do menu interativo.

### 2. Comparação de Políticas

Compara as 3 políticas obrigatórias sob as mesmas condições:

- Duração: 100s
- Taxa: 3 req/s
- Mesmo padrão de tráfego

### 3. Análise Completa

Executa múltiplas simulações comparando:

- Todas as políticas
- Tráfego constante vs rajadas
- Testes de alta carga

## Resultados e Relatórios

O simulador gera:

1. **Saída na tela**: Logs detalhados e resumos
2. **Arquivos JSON**: Relatórios completos para análise posterior
   - `policy_comparison_report.json`
   - `traffic_pattern_report.json`
   - `comprehensive_analysis_report.json`

### Métricas Coletadas

**Sistema:**

- Throughput total (req/s)
- Tempo médio de resposta
- Utilização dos recursos
- Desvio padrão dos tempos

**Por Servidor:**

- Requisições processadas
- Throughput individual
- Tempo médio por requisição
- Tamanho atual da fila

**Load Balancer:**

- Distribuição de requisições
- Variância da distribuição
- Eficiência da política

## Interpretação dos Resultados

### Quando usar cada política:

1. **Random**:

   - ✅ Implementação simples
   - ✅ Boa para cargas uniformes
   - ❌ Pode causar desbalanceamento

2. **Round Robin**:

   - ✅ Distribuição equitativa garantida
   - ✅ Ideal para servidores homogêneos
   - ❌ Não considera carga atual dos servidores

3. **Shortest Queue**:
   - ✅ Otimiza latência
   - ✅ Adapta-se a cargas heterogêneas
   - ✅ Melhor utilização de recursos
   - ❌ Maior complexidade de implementação

## Parâmetros Configuráveis

### Em `config/settings.py`:

- Tempos de processamento (CPU vs I/O)
- Capacidade dos servidores
- Poder de processamento (CPU power)

### Durante execução:

- Duração da simulação
- Taxa de chegada de requisições
- Política de balanceamento
- Padrão de tráfego

## Exemplo de Saída

```
🚀 SIMULADOR DE LOAD BALANCE - ANÁLISE COMPLETA
==================================================

📊 MÉTRICAS DO SISTEMA:
  • Throughput: 2.847 req/s
  • Tempo médio de resposta: 0.384s
  • Tempo médio de espera: 0.127s
  • Utilização do sistema: 67.2%
  • Total processado: 285 requisições

🏆 MELHORES POLÍTICAS POR MÉTRICA:
  • throughput: shortest_queue
  • avg_response_time: shortest_queue
  • avg_waiting_time: shortest_queue
  • utilization: shortest_queue
```

## Tecnologias Utilizadas

- **Python 3.8+**: Linguagem principal
- **SimPy**: Biblioteca para simulação de eventos discretos
- **Dataclasses**: Para modelagem de dados
- **JSON**: Para relatórios estruturados

## Contribuições para o Relatório

Este simulador fornece dados quantitativos para suportar as seguintes análises no relatório:

1. **Comparação objetiva** entre políticas
2. **Análise de performance** sob diferentes cargas
3. **Recomendações baseadas em dados** para cada cenário
4. **Justificativas técnicas** para escolha de políticas
5. **Métricas padronizadas** da indústria

## Próximos Passos

Para estender o projeto, considere:

- Implementar outras políticas (Weighted Round Robin, Least Connections)
- Adicionar servidores com capacidades diferentes
- Simular falhas de servidores
- Implementar balanceamento por localização geográfica
- Adicionar visualizações gráficas dos resultados
