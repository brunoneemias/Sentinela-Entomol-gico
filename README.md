# 🦟 Sentinela Entomológico
### Vigilância em Saúde Pública com Inteligência Artificial

> **Desafio:** Identificação e classificação de insetos vetores de doenças para auxílio à vigilância epidemiológica urbana.

---

## 📋 Sobre o Projeto

O **Sentinela Entomológico** é um sistema híbrido de classificação de insetos desenvolvido para apoiar agentes de saúde pública no campo. A ferramenta combina uma **árvore de decisão baseada em regras** (motor determinístico) com **Visão Computacional via IA** (GPT-4o), permitindo identificar insetos vetores de doenças como Dengue, Zika, Chikungunya, Malária e Doença de Chagas de forma rápida e acessível.

---

## 🧠 Lógica de Funcionamento do Algoritmo

O sistema opera com uma abordagem **híbrida de decisão**:

### 1. Motor de Regras (Árvore de Decisão)
Utiliza condicionais aninhadas (`if/elif/else`) para processar características observáveis do inseto. O fluxo percorre perguntas binárias (Sim/Não) sobre morfologia e ambiente até atingir uma classificação final.

**Fluxo simplificado:**
```
tem_asas?
├── SIM → tamanho_pequeno?
│         ├── SIM → patas_listradas? → voa_dia? → agua_parada? → 🚨 AEDES AEGYPTI
│         │         asas_manchas?   → voa_noite? → agua_limpa?  → 🚨 ANOPHELES
│         │         corpo_peludo?   → polen_patas? → flores?    → 🌼 ABELHA
│         │         (outros casos)                               → ✅ BAIXO RISCO
│         └── NÃO → corpo_peludo? → ...                         → ✅ BAIXO RISCO
└── NÃO → corpo_achatado? → habitos_noturnos? → frestas_parede? → 🚨 BARBEIRO
```

### 2. Visão Computacional (IA Generativa)
Integra o modelo **GPT-4o** via API da OpenAI para análise de imagens macroscópicas. O modelo atua como um "entomologista digital", reconhecendo padrões de coloração, morfologia e textura que seriam difíceis de descrever apenas em texto.

---

## 📥 Dados de Entrada Esperados

O sistema é **multimodal** e aceita dois tipos de entrada:

| Tipo | Formato | Exemplos de características |
|---|---|---|
| **Textual** | Respostas binárias Sim/Não | Listras nas patas, corpo achatado, hábito noturno, ambiente de coleta |
| **Imagem** | `.png`, `.jpg`, `.jpeg`, `.bmp` | Foto do inseto capturada por celular ou microscópio digital |

---

## 🤖 Tipo de Aprendizado Adotado

O módulo de IA utiliza **Aprendizado de Máquina Supervisionado** com Redes Neurais Convolucionais (CNN). O modelo GPT-4o foi previamente treinado com milhões de imagens rotuladas por especialistas, permitindo **classificação probabilística** com base nas categorias de risco pré-definidas.

O motor de regras, por sua vez, é **determinístico** — sem treinamento — e garante rastreabilidade e transparência nas decisões, essencial em contextos de saúde pública.

---

## 🏥 Finalidade Prática na Saúde Pública

| Aplicação | Benefício |
|---|---|
| 🗺️ **Mapeamento em Tempo Real** | Identificação e geolocalização imediata de focos de vetores |
| 👷 **Apoio ao Agente de Saúde** | Ferramenta intuitiva para profissionais sem especialização em entomologia |
| 🚨 **Prevenção de Surtos** | Resposta rápida para direcionar fumigação, limpeza e campanhas preventivas |
| 📊 **Vigilância Epidemiológica** | Geração de dados para análise de padrões de incidência por área |

---

## 🦠 Insetos Classificados

| Inseto | Doença(s) | Risco | Características-chave |
|---|---|---|---|
| *Aedes aegypti* | Dengue, Zika, Chikungunya | 🚨 Alto | Patas listradas, voo diurno, água parada |
| *Anopheles* | Malária | 🚨 Alto | Asas manchadas, voo noturno, água limpa |
| *Triatoma* (Barbeiro) | Doença de Chagas | 🚨 Alto | Corpo achatado, hábitos noturnos, frestas de parede |
| Abelha | — | 🌼 Benéfica | Corpo peludo, pólen nas patas, flores |
| Outros | — | ✅ Baixo risco | Não se encaixa nos padrões anteriores |

---

## 🗂️ Estrutura do Projeto

```
sentinela-entomologico/
│
├── main.py                  # Código principal da aplicação
├── README.md                # Este arquivo
│
└── imagens/                 # Assets visuais do quiz
    ├── inseto_asas.png
    ├── inseto_pequeno.png
    ├── aedes_patas.png
    ├── voa_dia.png
    ├── agua_parada.png
    ├── anopheles_asas.png
    ├── voa_noite.png
    ├── agua_limpa.png
    ├── barbeiro_corpo.png
    ├── habitos_noturnos.png
    ├── frestas_parede.png
    ├── abelha_pelos.png
    ├── abelha_polen.png
    ├── flores.png
    ├── resultado_alto_risco.jpg
    ├── resultado_baixo_risco.jpg
    ├── resultado_benefico.jpg
    └── resultado_desconhecido.jpg
```

---

## 🚀 Como Executar

### Pré-requisitos

- Python 3.10+
- Chave de API da OpenAI (para o módulo de IA)

### Instalação

```bash
# Clone o repositório
git clone https://github.com/brunoneemias/Sentinela-Entomol-gico.git
cd Sentinela-Entomol-gico

# Instale as dependências
pip install customtkinter Pillow openai
```

### Configuração da API

Abra o arquivo `main.py` e substitua o valor da variável `OPENAI_API_KEY` pela sua chave:

```python
OPENAI_API_KEY = "sua-chave-aqui"
```


### Execução

```bash
python main.py
```

---

## 🖥️ Telas do Sistema

| Tela | Descrição |
|---|---|
| **Menu Principal** | Escolha entre classificação manual (quiz) ou por IA (foto) |
| **Quiz Interativo** | Perguntas binárias com imagens ilustrativas e barra de progresso |
| **Classificação por IA** | Upload de foto do inseto para análise pelo GPT-4o |

---

## 📦 Dependências

| Biblioteca | Versão | Uso |
|---|---|---|
| `customtkinter` | ≥5.0 | Interface gráfica moderna |
| `Pillow` | ≥9.0 | Manipulação de imagens |
| `openai` | ≥1.0 | Integração com GPT-4o |

---

## 📄 Licença

Projeto desenvolvido para fins acadêmicos 

---

*Desenvolvido como resposta ao desafio de vigilância entomológica com IA aplicada à saúde pública.* 🦟🔬
