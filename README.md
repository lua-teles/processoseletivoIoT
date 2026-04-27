# Sistema de Monitoramento e Nutrição de Solo
 
| | |
|---|---|
| **Candidato** | Luana Teles Alves |
| **GitHub** | lua-teles |
 
---
 
## 1️⃣ Visão Geral da Solução
 
O projeto simula um sistema embarcado completo de **monitoramento de solo** com ESP32 e MicroPython.
 
- **Objetivo:** monitorar umidade, pH e nível de NPK do solo, acionar irrigação automática e alertar sobre deficiências de nutrientes
- **O que faz:** lê 3 sensores analógicos continuamente; aciona irrigação quando solo está seco; emite alertas sonoros e visuais quando pH ou NPK estão fora do ideal
- **Interação:** o usuário gira os potenciômetros no Wokwi para simular variações de umidade, acidez e nutrientes do solo
---
 
## 2️⃣ Arquitetura do Sistema Embarcado
 
### Fluxo principal (`main.py`)
 
```
Inicializa periféricos (ADC x3, LEDs x3, Buzzer)
               │
               ▼
     Imprime mensagem de boot
               │
               ▼
    ┌──────────────────────────┐
    │     Loop infinito (1s)   │
    │                          │
    │  1. Lê 3 sensores (ADC)  │
    │  2. Calcula umidade %    │
    │  3. Converte pH e NPK    │
    │  4. Determina estados    │
    │  5. Aciona irrigação     │
    │  6. Verifica nutrientes  │
    │  7. Atualiza LEDs        │
    │  8. Loga no serial       │
    └──────────────────────────┘
```
 
### Máquina de estados de umidade (com histerese)
 
```
        adc > 2800
  UMIDO ──────────► SECO ──────► REGANDO
    ▲                                │
    └────────────────────────────────┘
              adc < 1800
```
 
### Lógica de nutrientes
 
```
pH  < 4.0  → CRITICO → aplicar calcário urgente
pH  4–6    → ALERTA  → solo ácido
pH  6–8    → IDEAL
pH  8–10   → ALERTA  → solo alcalino
pH  > 10   → CRITICO → aplicar enxofre urgente
 
NPK < 33%  → BAIXO   → aplicar adubo NPK
NPK 33–66% → IDEAL
NPK > 66%  → EXCESSO → reduzir adubação
```
 
### LEDs
 
| LED | Cor | Condição |
|---|---|---|
| Verde | 🟢 | Solo saudável — tudo ideal |
| Amarelo | 🟡 | Alerta de nutriente (pH ou NPK fora do ideal) |
| Vermelho | 🔴 | Solo seco — irrigação ativa |
 
---
 
## 3️⃣ Componentes Utilizados na Simulação
 
| Componente | Pino | Função |
|---|---|---|
| ESP32 DevKit C v4 | — | Microcontrolador principal |
| Potenciômetro 1 | IO34 (ADC) | Simula sensor de umidade do solo |
| Potenciômetro 2 | IO35 (ADC) | Simula sensor de pH do solo |
| Potenciômetro 3 | IO32 (ADC) | Simula sensor de NPK do solo |
| LED Verde | IO25 | Solo saudável |
| LED Amarelo | IO26 | Alerta de nutriente |
| LED Vermelho | IO27 | Solo seco / irrigando |
| Buzzer | IO33 | Alertas sonoros diferenciados |
| Resistores 220Ω | — | Proteção dos LEDs |
 
---
 
## 4️⃣ Decisões Técnicas Relevantes
 
**Histerese nos limiares de umidade**
Dois limiares distintos (`LIMIAR_SECO = 2800` e `LIMIAR_UMIDO = 1800`) evitam oscilações quando o sensor fica na fronteira entre estados.
 
**Alertas sonoros diferenciados**
O buzzer usa frequências e padrões distintos para irrigação (2 bips agudos) e deficiência de nutrientes (2 bips graves), permitindo identificar o tipo de alerta sem olhar para a tela.
 
**Funções de diagnóstico isoladas**
`diagnostico_ph()` e `diagnostico_npk()` retornam valor, status e mensagem de recomendação — separando a lógica de avaliação da lógica de exibição.
 
**Três LEDs para três estados**
Em vez de apenas ligado/desligado, o sistema usa verde/amarelo/vermelho para comunicar visualmente a prioridade: irrigação (vermelho) tem prioridade sobre alerta de nutriente (amarelo), que tem prioridade sobre estado saudável (verde).
 
**Compatibilidade com o pipeline Docker**
Apenas bibliotecas padrão do MicroPython (`machine`, `time`) — sem dependências externas — garantindo que o `fs.bin` gerado pelo Dockerfile funcione sem modificações.
 
---
 
## 5️⃣ Resultados Obtidos
 
- ✅ Irrigação automática ativa ao detectar solo seco
- ✅ Alertas de pH ácido, alcalino e crítico com recomendação de correção
- ✅ Alertas de NPK baixo e excesso com recomendação de adubação
- ✅ LEDs verde/amarelo/vermelho indicando estado de prioridade
- ✅ Buzzer com sons distintos para cada tipo de alerta
- ✅ Log completo no serial com umidade, pH, NPK e estado atual
- ✅ Texto de boot `"Monitoramento e Nutricao de Solo"` validado pelo Wokwi CI
---
 
## 6️⃣ Comentários Adicionais
 
**Limitações atuais:**
- Os potenciômetros são aproximações dos sensores reais — sensores físicos de pH e EC têm comportamento e calibração distintos
- Não há persistência de dados (histórico de leituras é perdido ao reiniciar)

**Melhorias com mais tempo:**
- Display OLED mostrando painel completo de saúde do solo
- Registro de histórico com timestamps para análise de tendências
- Comunicação MQTT para envio dos dados para nuvem
- Tempo mínimo de irrigação para evitar subciclos

**Aprendizados:**
- Uso de múltiplos ADCs simultâneos no ESP32 com MicroPython
- Mapeamento de faixas de ADC para grandezas físicas (pH, %)
- Importância de alertas diferenciados (visuais + sonoros) em sistemas embarcados