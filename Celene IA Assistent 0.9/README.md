# CÉLENE

> Assistente virtual pessoal com IA local, ferramentas integradas, monitoramento do sistema e interface inspirada em terminais de ficção científica.

---

## CÉLENE v0.3

A Célene é uma assistente virtual pessoal desenvolvida para funcionar localmente utilizando inteligência artificial através do Ollama.

A ideia do projeto é construir uma assistente capaz de:

- Conversar naturalmente
- Entender a intenção do usuário
- Utilizar ferramentas automaticamente
- Consultar informações externas
- Realizar cálculos
- Gerar código
- Apresentar resultados em cards específicos
- Monitorar o computador
- Trabalhar com arquivos
- Executar automações
- Futuramente interagir por voz
- Futuramente controlar partes do sistema operacional

---

# VISÃO DO PROJETO

A arquitetura da Célene foi criada de forma modular.

```text
                         ┌─────────────────────────┐
                         │        INTERFACE        │
                         │      HTML / CSS / JS     │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │         SERVER          │
                         │          Flask          │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │          BRAIN          │
                         │     Núcleo da Célene    │
                         └────────────┬────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
              ▼                       ▼                       ▼
      ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
      │ TOOL DETECTOR│        │    OLLAMA    │        │   SERVICES   │
      └──────┬───────┘        └──────────────┘        └──────┬───────┘
             │                                                │
       ┌─────┼─────────┐                           ┌──────────┼─────────┐
       ▼     ▼         ▼                           ▼          ▼         ▼
    WEATHER CALCULATOR CODE                      SYSTEM      FILES    OUTROS
```

---

# TECNOLOGIAS

## Backend

- Python
- Flask
- Ollama
- psutil

## Frontend

- HTML
- CSS
- JavaScript

## Inteligência Artificial

- Ollama
- Modelo personalizado `celene`
- Modelo base `llama3.2:3b`

---

# ESTRUTURA DO PROJETO

```text
Celene/
│
├── app/
│   ├── ai/
│   │   ├── __init__.py
│   │   └── model.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── server.py
│   │
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── browser.py
│   │   ├── calculator.py
│   │   ├── files.py
│   │   ├── system.py
│   │   └── weather.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── brain.py
│   │   ├── message.py
│   │   ├── router.py
│   │   ├── tool_detector.py
│   │   ├── tool_parser.py
│   │   └── tool_registry.py
│   │
│   ├── services/
│   │   ├── system_monitor.py
│   │   └── code_generator.py
│   │
│   └── main.py
│
├── data/
├── interface/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── models/
│   └── manifests/
│
├── Modelfile
├── requirements.txt
└── README.md
```

---

# FLUXO PRINCIPAL

Uma mensagem enviada pelo usuário passa por várias etapas.

```text
┌─────────────────────────────┐
│            USER             │
│                             │
│ "Crie um código Python..."  │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│           SERVER            │
│            Flask            │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│            BRAIN            │
│                             │
│ Processa a solicitação      │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│       TOOL DETECTOR         │
│                             │
│ Identifica: CODE            │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│       CODE GENERATOR        │
│                             │
│       Ollama + IA           │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│            BRAIN            │
│                             │
│ Organiza o resultado        │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│          FRONTEND           │
│                             │
│       CODE CARD             │
└─────────────────────────────┘
```

---

# BRAIN

Arquivo:

```text
app/core/brain.py
```

O Brain é o núcleo lógico da Célene.

Responsabilidades:

- Receber mensagens
- Analisar contexto
- Detectar ferramentas
- Executar ferramentas
- Conversar com o modelo
- Processar resultados
- Organizar respostas
- Enviar resultados para a interface

Fluxo:

```text
Mensagem
   ↓
Brain
   ↓
Tool Detector
   ↓
Existe ferramenta?
   │
   ├── SIM
   │    ↓
   │ Executa ferramenta
   │
   └── NÃO
        ↓
      Ollama
        ↓
      Resposta
```

---

# TOOL DETECTOR

Arquivo:

```text
app/core/tool_detector.py
```

O Tool Detector identifica automaticamente a intenção do usuário.

Exemplo:

```text
Qual a previsão para Fortaleza?
```

Resultado:

```text
weather
```

Outro exemplo:

```text
Quanto é 20 + 20?
```

Resultado:

```text
calculator
```

Outro exemplo:

```text
Crie um código Python que calcule uma média.
```

Resultado:

```text
code
```

Ferramentas planejadas:

```text
weather
calculator
code
browser
files
system
automation
voice
media
```

---

# TOOL REGISTRY

Arquivo:

```text
app/core/tool_registry.py
```

Funciona como um catálogo das ferramentas disponíveis.

```text
TOOL REGISTRY

├── weather
├── calculator
├── code
├── browser
├── files
└── system
```

A arquitetura permite adicionar novas ferramentas sem alterar toda a aplicação.

---

# WEATHER

Arquivo:

```text
app/commands/weather.py
```

Responsável pelas consultas meteorológicas.

Informações:

- Temperatura máxima
- Temperatura mínima
- Sensação térmica
- Probabilidade de chuva
- Precipitação
- Velocidade do vento
- Nascer do sol
- Pôr do sol

Exemplo:

```text
Como está o tempo em Fortaleza?
```

A ferramenta consulta os dados meteorológicos e retorna as informações para o Brain.

---

# WEATHER CARD

A interface possui um componente visual específico para previsão do tempo.

```text
┌──────────────────────────────────────────────┐
│ PREVISÃO DO TEMPO                            │
│                                              │
│ Fortaleza, Ceará                             │
│ 30/07/2026                                   │
│                                              │
│ 30.5°                                        │
│                                              │
│ Máxima       30.5 °C                         │
│ Mínima       25.0 °C                         │
│ Chuva        33%                             │
│ Precipitação 0.3 mm                          │
│ Vento        20.4 km/h                       │
│ Sensação     32.5 °C                         │
│                                              │
│ Nascer       05:42                           │
│ Pôr do sol   17:39                           │
└──────────────────────────────────────────────┘
```

---

# CALCULATOR

Arquivo:

```text
app/commands/calculator.py
```

Responsável por cálculos matemáticos.

Exemplo:

```text
Quanto é 20 + 20?
```

Resultado:

```text
40
```

A calculadora funciona como ferramenta independente para operações matemáticas.

---

# CODE MODE

O Code Mode permite que a Célene gere código automaticamente.

Arquivo:

```text
app/services/code_generator.py
```

Exemplo:

```text
Crie um código Python que calcule
a média de uma lista.
```

O sistema identifica:

```text
tool = code
```

Depois o gerador produz os dados necessários para a interface.

Exemplo:

```json
{
    "title": "Calculadora de média",
    "language": "python",
    "filename": "media.py",
    "description": "Calcula a média de uma lista de números.",
    "code": "def calcular_media(valores):\n    return sum(valores) / len(valores)"
}
```

---

# CODE CARD

O frontend possui um card especializado para código.

```text
┌───────────────────────────────────────────────┐
│ CODE://GENERATED                    [ READY ] │
│                                               │
│ Calculadora de Média                          │
│                                               │
│ FILE       media.py                           │
│ LANGUAGE   PYTHON                             │
│                                               │
│ Calcula a média de uma lista de números.      │
│                                               │
│ ┌───────────────────────────────────────────┐ │
│ │ media.py                         PYTHON   │ │
│ ├───────────────────────────────────────────┤ │
│ │ 01 │ def calcular_media(valores):         │ │
│ │ 02 │     return sum(valores) / len(...)   │ │
│ │ 03 │                                      │ │
│ │ 04 │ valores = [1, 2, 3, 4, 5]            │ │
│ │ 05 │ print(calcular_media(valores))       │ │
│ └───────────────────────────────────────────┘ │
│                                               │
│ [ COPY ]                                      │
│                                               │
│ STATUS://GENERATED                            │
└───────────────────────────────────────────────┘
```

O botão `COPY` permite copiar o código para a área de transferência.

---

# SYSTEM MONITOR

Arquivo:

```text
app/services/system_monitor.py
```

O System Monitor acompanha o estado do computador.

Monitoramento:

```text
CPU
GPU
RAM
DISCOS
```

Possíveis extensões:

```text
Temperatura da CPU
Temperatura da GPU
VRAM
Processos
Rede
Espaço disponível
Uso de energia
```

---

# SYSTEM STATUS

A interface possui uma área destinada ao status do sistema.

```text
[ SYSTEM STATUS ]

CORE          [ ONLINE ]
MEMORY        [ ONLINE ]
TOOLS         [ ONLINE ]
WEATHER       [ ONLINE ]
CALCULATOR    [ ONLINE ]
OLLAMA        [ ONLINE ]
```

Monitoramento de hardware:

```text
[ HARDWARE ]

CPU      ███████░░░  67%
GPU      █████░░░░░  48%
RAM      ██████░░░░  61%

DISK C   ███░░░░░░░  31%
DISK D   █░░░░░░░░░  08%
```

---

# MONITORAMENTO EM TEMPO REAL

O System Monitor foi pensado para atualizar os dados periodicamente.

Durante uma geração:

```text
USER
 │
 ▼
CÉLENE PROCESSANDO
 │
 ├───────────────► CPU 72%
 ├───────────────► GPU 41%
 ├───────────────► RAM 63%
 └───────────────► DISK 12%
```

A interface pode continuar recebendo informações enquanto o Ollama processa uma resposta.

---

# OLLAMA

A inteligência artificial da Célene é executada localmente através do Ollama.

Modelo personalizado:

```text
celene
```

Modelo base:

```text
llama3.2:3b
```

O comportamento da assistente é definido pelo arquivo:

```text
Modelfile
```

---

# MODELFILE

Exemplo:

```text
FROM llama3.2:3b

SYSTEM """
Você é Celene.

Você é uma assistente virtual pessoal.

Você sempre responde em português do Brasil.

Seja clara, natural, objetiva e amigável.

Você é especialmente útil para programação,
organização, estudos e automações.

Nunca invente informações quando não souber uma resposta.

Forneça apenas a resposta final ao usuário.

Priorize sempre a mensagem mais recente do usuário.

Use mensagens anteriores apenas quando forem relevantes
para responder à mensagem atual.

Não continue espontaneamente assuntos antigos que o usuário
não mencionou novamente.
"""

PARAMETER temperature 0.7

PARAMETER num_ctx 4096
```

---

# CRIANDO O MODELO

Baixe o modelo base:

```bash
ollama pull llama3.2:3b
```

Crie o modelo:

```bash
ollama create celene -f Modelfile
```

Verifique:

```bash
ollama list
```

Deverá aparecer:

```text
celene
llama3.2:3b
```

---

# AMBIENTE PYTHON

Crie o ambiente virtual:

```bash
python -m venv .venv
```

No Windows:

```bash
.venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

---

# EXECUTANDO A CÉLENE

Entre na pasta do projeto:

```bash
cd C:\laragon\www\Celene
```

Execute:

```bash
python -m app.api.server
```

O servidor será iniciado em:

```text
http://127.0.0.1:5000
```

Abra no navegador:

```text
http://127.0.0.1:5000
```

---

# API

A aplicação possui endpoints HTTP.

## POST /api/chat

Endpoint principal da conversação.

```text
POST /api/chat
```

Fluxo:

```text
Frontend
   ↓
/api/chat
   ↓
Brain
   ↓
Ferramenta ou Ollama
   ↓
Resposta
   ↓
Frontend
```

## POST /api/chat/stream

Endpoint destinado ao streaming de respostas.

```text
POST /api/chat/stream
```

A ideia é permitir que respostas sejam transmitidas progressivamente.

## POST /api/classify

Endpoint utilizado para classificação da intenção.

```text
POST /api/classify
```

Exemplo:

```text
Usuário:

Crie um código Python.
```

Resultado:

```json
{
    "tool": "code"
}
```

---

# FRONTEND

A interface está localizada em:

```text
interface/
```

Arquivos:

```text
index.html
script.js
style.css
```

---

# INDEX.HTML

Arquivo responsável pela estrutura da interface.

Principais elementos:

```text
Header
Sidebar
Conversation
Messages
Input
System Status
Cards
```

---

# STYLE.CSS

Arquivo responsável pela identidade visual.

A estética da Célene utiliza elementos inspirados em:

- Terminais antigos
- Computadores de ficção científica
- Interfaces CRT
- Sistemas militares
- Monitores monocromáticos
- ASCII Art
- Computadores dos anos 80/90
- Ficção científica retrofuturista

Características:

```text
Verde terminal
Fundo preto
Bordas finas
Fonte monoespaçada
ASCII
Brilho sutil
Linhas técnicas
Cards minimalistas
```

---

# SCRIPT.JS

Arquivo responsável pela lógica da interface.

Principais funções:

```text
Enviar mensagens
Receber respostas
Renderizar mensagens
Renderizar Weather Cards
Renderizar Code Cards
Copiar código
Atualizar interface
Controlar scroll
Atualizar informações do sistema
```

---

# ARQUITETURA DE RESPOSTAS

A Célene trabalha com diferentes tipos de resposta.

```text
TEXT
 │
 └── Mensagem normal

WEATHER
 │
 └── Weather Card

CALCULATOR
 │
 └── Result Card

CODE
 │
 └── Code Card

ERROR
 │
 └── Error Message
```

Futuramente:

```text
IMAGE CARD
FILE CARD
SYSTEM CARD
SEARCH CARD
MUSIC CARD
VIDEO CARD
TERMINAL CARD
AUTOMATION CARD
```

---

# VOZ

Uma das próximas etapas é implementar reconhecimento de voz.

Arquitetura planejada:

```text
              🎙️ MICROFONE
                    │
                    ▼
          SPEECH RECOGNITION
                    │
                    ▼
                  BRAIN
                    │
                    ▼
                 OLLAMA
                    │
                    ▼
                 RESPOSTA
                    │
                    ▼
             TEXT TO SPEECH
                    │
                    ▼
                  🔊
```

Objetivo: permitir conversar com a Célene sem precisar digitar.

---

# MEMÓRIA

Outra etapa planejada é implementar um sistema de memória.

A memória poderá armazenar informações relevantes como:

```text
Preferências
Contextos
Projetos
Informações importantes
Histórico
Configurações
```

Arquitetura futura:

```text
Usuário
   ↓
Brain
   ↓
Memory Manager
   ↓
Memória relevante
   ↓
Ollama
```

---

# EXECUÇÃO DE CÓDIGO

O Code Mode poderá evoluir de geração para execução.

Fluxo planejado:

```text
PEDIDO
  ↓
GERAR
  ↓
ANALISAR
  ↓
VALIDAR
  ↓
EXECUTAR
  ↓
CAPTURAR RESULTADO
  ↓
MOSTRAR CARD
```

A execução deverá utilizar isolamento adequado para evitar que código gerado possa comprometer o sistema.

---

# SISTEMA DE ARQUIVOS

Futuramente a Célene poderá trabalhar com arquivos.

Operações planejadas:

```text
Ler
Criar
Editar
Renomear
Mover
Organizar
Analisar
Pesquisar
```

Exemplos:

```text
Leia meu arquivo README.md.

Crie uma pasta para esse projeto.

Analise essa planilha.

Renomeie esse arquivo.
```

---

# NAVEGADOR

Uma ferramenta de navegador poderá permitir que a Célene:

```text
Pesquisar informações
Abrir páginas
Consultar sites
Preencher formulários
Executar tarefas
```

Arquitetura:

```text
Usuário
   ↓
Brain
   ↓
Browser Tool
   ↓
Navegador
   ↓
Resultado
   ↓
Brain
   ↓
Usuário
```

---

# AUTOMAÇÃO

A Célene poderá ser utilizada como uma camada de automação.

Exemplos:

```text
Abrir programas
Executar comandos
Organizar arquivos
Processar planilhas
Automatizar navegador
Executar scripts
```

---

# CONTROLE DO COMPUTADOR

Uma etapa futura será permitir interação com o sistema operacional.

Possibilidades:

```text
Abrir aplicativos
Fechar aplicativos
Executar comandos
Consultar processos
Controlar volume
Abrir arquivos
Automatizar tarefas
```

Operações potencialmente destrutivas devem possuir controles de segurança.

---

# MONITORAMENTO AVANÇADO

O System Monitor deverá evoluir para um painel semelhante a:

```text
╔════════════════════════════════════════════╗
║              CELENE SYSTEM                 ║
╠════════════════════════════════════════════╣
║                                            ║
║ CPU    ███████░░░  67%                    ║
║ GPU    █████░░░░░  48%                    ║
║ RAM    ██████░░░░  61%                    ║
║                                            ║
║ DISK C ███░░░░░░░  31%                    ║
║ DISK D █░░░░░░░░░  08%                    ║
║                                            ║
║ OLLAMA             [ ONLINE ]             ║
║ CORE               [ ONLINE ]             ║
║ TOOLS              [ ONLINE ]             ║
║                                            ║
╚════════════════════════════════════════════╝
```

---

# SISTEMA DE CARDS

A interface utiliza cards especializados.

```text
                    RESPONSE
                       │
          ┌────────────┼────────────┐
          │            │            │
          ▼            ▼            ▼
       WEATHER     CALCULATOR      CODE
          │            │            │
          ▼            ▼            ▼
       WEATHER       RESULT        CODE
        CARD          CARD         CARD
```

Isso evita transformar todas as respostas em simples blocos de texto.

---

# FILOSOFIA DO PROJETO

A Célene não foi criada apenas como um chatbot.

O objetivo é construir uma assistente pessoal modular.

```text
                       CELENE
                          │
             ┌────────────┼────────────┐
             │            │            │
             ▼            ▼            ▼
             IA         TOOLS        SYSTEM
             │            │            │
             ▼            ▼            ▼
          Conversa      Ações     Monitoramento
             │            │            │
             └────────────┼────────────┘
                          │
                          ▼
                     EXPERIÊNCIA
```

Cada funcionalidade deve ser independente.

Isso permite adicionar novas ferramentas sem reconstruir todo o sistema.

---

# PRINCÍPIOS

### Modularidade

Cada componente deve possuir uma responsabilidade clara.

### Simplicidade

O sistema deve evitar complexidade desnecessária.

### Local First

Sempre que possível, a IA e os dados devem permanecer localmente.

### Extensibilidade

Novas ferramentas devem poder ser adicionadas facilmente.

### Interface própria

A Célene deve possuir identidade visual própria.

### Segurança

Ferramentas capazes de executar ações no computador devem possuir controles apropriados.

---

# STATUS ATUAL

```text
CELENE v0.3

[ OK ] Conversação
[ OK ] Ollama
[ OK ] Brain
[ OK ] Tool Detector
[ OK ] Tool Registry
[ OK ] Weather
[ OK ] Calculator
[ OK ] Code Generator
[ OK ] Code Response
[ OK ] Weather Card
[ OK ] Code Card
[ OK ] System Monitor
[ OK ] System Status
[ OK ] Interface Futurista
```

Em desenvolvimento:

```text
[ >> ] Monitoramento em tempo real
[ >> ] Reconhecimento de voz
[ >> ] Text To Speech
[ >> ] Memória avançada
[ >> ] Execução de código
[ >> ] Sistema de arquivos
[ >> ] Browser Tool
[ >> ] Automação
[ >> ] Controle do computador
[ >> ] Interface avançada
```

---

# ROADMAP

## Fase 1 — Núcleo

```text
[✓] Ollama
[✓] Modelo Celene
[✓] Brain
[✓] Router
[✓] Tool Detector
[✓] Tool Registry
```

## Fase 2 — Ferramentas

```text
[✓] Calculadora
[✓] Weather
[✓] Code Generator
[✓] System Monitor
```

## Fase 3 — Interface

```text
[✓] Chat
[✓] Tema futurista
[✓] Tema terminal
[✓] Weather Card
[✓] Code Card
[✓] Copy Code
[ ] System Dashboard
[ ] Animações avançadas
```

## Fase 4 — Inteligência

```text
[ ] Memória
[ ] Context Manager
[ ] Planejamento
[ ] Tool Chaining
[ ] Melhor entendimento de intenção
```

## Fase 5 — Voz

```text
[ ] Speech Recognition
[ ] Voice Activity Detection
[ ] Text To Speech
[ ] Wake Word
```

## Fase 6 — Automação

```text
[ ] Browser
[ ] Files
[ ] Terminal
[ ] Windows Automation
[ ] Process Manager
```

## Fase 7 — Célene Autônoma

```text
[ ] Planejamento de tarefas
[ ] Execução de múltiplas ferramentas
[ ] Memória contextual
[ ] Monitoramento do sistema
[ ] Automação avançada
```

---

# EXEMPLOS DE USO

## Conversação

```text
Usuário:

Oi Celene
```

```text
Celene:

Oi! Tudo certo por aí?
```

## Calculadora

```text
Usuário:

Quanto é 25 * 4?
```

```text
Celene:

100
```

## Weather

```text
Usuário:

Qual a previsão para Fortaleza?
```

A interface apresenta um Weather Card.

## Código

```text
Usuário:

Crie um código Python que calcule
a média de uma lista.
```

A interface apresenta um Code Card com o código gerado.

---

# DEBUG

Quando ocorrer um erro no backend, verificar:

```text
1. Terminal do Flask
2. Brain
3. Tool Detector
4. Tool Parser
5. Tool Registry
6. Serviço responsável
7. Resposta da API
8. Console do navegador
```

Fluxo de diagnóstico:

```text
Usuário
   ↓
Frontend
   ↓
API
   ↓
Brain
   ↓
Tool Detector
   ↓
Tool
   ↓
Resultado
   ↓
Frontend
```

O ponto em que o fluxo parar normalmente indica onde está o problema.

---

# CONVENÇÕES

Arquivos Python:

```text
snake_case
```

Exemplos:

```text
system_monitor.py
tool_detector.py
code_generator.py
```

Classes:

```text
PascalCase
```

Exemplo:

```python
class SystemMonitor:
    pass
```

Funções:

```text
snake_case
```

Exemplo:

```python
def detect_tool():
    pass
```

---

# ORGANIZAÇÃO DAS FERRAMENTAS

Uma ferramenta deve, preferencialmente, possuir:

```text
Detector
Parser
Executor
Response
Frontend Renderer
```

Exemplo:

```text
WEATHER

tool_detector.py
      ↓
tool_parser.py
      ↓
weather.py
      ↓
brain.py
      ↓
server.py
      ↓
script.js
      ↓
Weather Card
```

---

# FUTURA ARQUITETURA

```text
                         ┌──────────────────────┐
                         │        CELENE        │
                         │         CORE         │
                         └──────────┬───────────┘
                                    │
             ┌──────────────────────┼──────────────────────┐
             │                      │                      │
             ▼                      ▼                      ▼
        INTELLIGENCE             TOOLS                 MEMORY
             │                      │                      │
      ┌──────┼──────┐       ┌───────┼────────┐             │
      ▼      ▼      ▼       ▼       ▼        ▼             ▼
    LLM   Context  Plan   Web    System    Files       Database
                           │
                           ▼
                        Browser
```

---

# VISÃO DE LONGO PRAZO

A visão final da Célene é possuir uma arquitetura semelhante a:

```text
                         ┌──────────────────┐
                         │      CELENE      │
                         │   AI ASSISTANT   │
                         └────────┬─────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
          PERCEPTION         INTELLIGENCE          ACTION
              │                   │                   │
         ┌────┼────┐        ┌─────┼─────┐       ┌─────┼─────┐
         ▼    ▼    ▼        ▼     ▼     ▼       ▼     ▼     ▼
       VOICE SCREEN SYSTEM   LLM MEMORY PLAN   FILES WEB SYSTEM
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  │
                                  ▼
                             USER EXPERIENCE
```

---

# IDENTIDADE

```text
NOME       : CELENE
VERSÃO     : 0.3
TIPO       : Personal AI Assistant
ARQUITETURA: Local AI + Tools + Services + Web Interface
ESTILO     : Retro Futuristic / Terminal / Sci-Fi / ASCII
```

---

# AUTOR

Projeto pessoal desenvolvido por Pablo para estudos, desenvolvimento, automação e experimentação com inteligência artificial local.

---

# LICENÇA

Projeto pessoal.

Uso destinado a:

- Estudos
- Desenvolvimento
- Experimentação
- Automação
- Pesquisa
- Uso pessoal

---

# FIM

```text
╔══════════════════════════════════════════════╗
║                                              ║
║                 C E L E N E                  ║
║                                              ║
║             SYSTEM ONLINE                    ║
║                                              ║
║          PERSONAL AI ASSISTANT               ║
║                                              ║
║              VERSION 0.3                     ║
║                                              ║
╚══════════════════════════════════════════════╝

> SYSTEM READY
> WAITING FOR USER INPUT...
```
