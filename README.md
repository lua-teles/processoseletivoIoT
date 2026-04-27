# Sistema de Monitoramento e Nutrição de Solo
 
| | |
|---|---|
| **Candidato** | Luana Teles Alves |
| **GitHub** | lua-teles |
 
---
 
## 1️⃣ Visão Geral da Solução
 
O projeto simula um sistema embarcado completo de **monitoramento de solo** com ESP32 e MicroPython.
 
- **Objetivo:** monitorar umidade, pH e nível de NPK do solo, acionar irrigação automática e alertar sobre deficiências de nutrientes
- **O que faz:** lê 3 sensores analógicos continuamente; aciona irrigação quando solo está seco; emite alertas sonoros e visuais quando pH ou NPK estão fora do ideal; encerra após 10 ciclos para compatibilidade com CI
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
    ┌─────────────────────────────────┐
    │  Loop de MAX_CICLOS=10 leituras │
    │                                 │
    │  1. Lê 3 sensores (ADC)         │
    │  2. Calcula umidade %           │
    │  3. Converte pH e NPK           │
    │  4. Determina estado umidade    │
    │  5. Aciona irrigação se seco    │
    │  6. Verifica alertas nutrientes │
    │  7. Atualiza LEDs               │
    │  8. Loga no serial              │
    │  9. Aguarda 1 segundo           │
    └─────────────────────────────────┘
               │
               ▼
     Encerra simulação (CI safe)
```
 
### Máquina de estados de umidade (com histerese)
 
```
        adc > 2800
  UMIDO ──────────► SECO ──────► REGANDO
    ▲                                │
    └────────────────────────────────┘
              adc < 1800
```
 
A histerese com dois limiares distintos evita oscilações quando o sensor fica na fronteira.
 
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
| Potenciômetro 1 | 34 (ADC) | Simula sensor de umidade do solo |
| Potenciômetro 2 | 35 (ADC) | Simula sensor de pH do solo |
| Potenciômetro 3 | 32 (ADC) | Simula sensor de NPK do solo |
| LED Verde | 25 | Solo saudável |
| LED Amarelo | 26 | Alerta de nutriente |
| LED Vermelho | 27 | Solo seco / irrigando |
| Buzzer | 33 | Alertas sonoros diferenciados |
| Resistores 220Ω | — | Proteção dos LEDs |
 
> Os potenciômetros simulam sensores analógicos que não estão disponíveis na biblioteca do Wokwi (pH e NPK). O sensor de umidade também é simulado desta forma, gerando valores ADC de 0 a 4095 idênticos aos que um sensor real produziria.
 
---
 
## 4️⃣ Decisões Técnicas Relevantes
 
**Histerese nos limiares de umidade**
Dois limiares distintos (`UMIDADE_SECO = 2800` e `UMIDADE_UMIDO = 1800`) evitam oscilações quando o sensor fica na fronteira entre estados.
 
**Loop finito com MAX_CICLOS**
O programa executa exatamente 5 ciclos de leitura (0.5 segundo cada) e encerra limpo. Isso evita timeout no Wokwi CLI durante o GitHub Actions, que aguarda o encerramento do processo para validar o `expect_text`.
 
**Alertas sonoros diferenciados**
O buzzer usa frequências e padrões distintos: 2 bips agudos (800Hz) para irrigação e 2 bips graves (500/700Hz) para deficiência de nutrientes, permitindo identificar o tipo de alerta sem olhar para a tela.
 
**Funções de diagnóstico isoladas**
`diagnostico_ph()` e `diagnostico_npk()` retornam valor, status e mensagem de recomendação — separando a lógica de avaliação da lógica de exibição e facilitando manutenção.
 
**Três LEDs para três prioridades**
Verde/amarelo/vermelho comunicam visualmente a prioridade: irrigação (vermelho) tem prioridade sobre alerta de nutriente (amarelo), que tem prioridade sobre estado saudável (verde).
 
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
- ✅ Programa encerra após 5 ciclos (2.5s) — sem timeout no GitHub Actions
- ✅ Texto de boot validado pelo Wokwi CLI (`expect_text: 'Monitoramento e Nutricao de Solo'`)
---
 
## 6️⃣ Comentários Adicionais
 
**Limitações atuais:**
- Os potenciômetros são aproximações dos sensores reais — sensores físicos de pH e EC têm comportamento e calibração distintos
- O loop finito (5 ciclos com intervalo de 500ms) é adequado para CI mas em produção real o sistema rodaria continuamente

**Melhorias com mais tempo:**
- Display OLED mostrando painel completo de saúde do solo em tempo real
- Registro de histórico com timestamps para análise de tendências
- Comunicação MQTT para envio dos dados para nuvem
- Tempo mínimo de irrigação para evitar subciclos muito curtos

**Aprendizados:**
- Uso de múltiplos ADCs simultâneos no ESP32 com MicroPython
- Mapeamento de faixas de ADC para grandezas físicas (pH, %)
- Importância de alertas diferenciados (visuais + sonoros) em sistemas embarcados
- Configuração de pipeline CI/CD com Docker + Wokwi CLI + GitHub Actions
 