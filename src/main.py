"""
Sistema de Monitoramento e Nutricao de Solo
Monitora umidade, pH e nivel de NPK do solo.
Aciona irrigacao e emite alertas de nutrientes automaticamente.
 
Hardware simulado (ESP32):
- Potenciometro 1 (IO34) -> Sensor de umidade
- Potenciometro 2 (IO35) -> Sensor de pH
- Potenciometro 3 (IO32) -> Sensor de NPK
- LED Verde  (IO25) -> Solo saudavel
- LED Amarelo (IO26) -> Alerta de nutriente
- LED Vermelho (IO27) -> Irrigando
- Buzzer (IO33)       -> Alertas sonoros
"""
 
from machine import Pin, ADC, PWM
import time
 
# ── Pinos ───────────────────────────────────────────────────────
SOLO_UMIDADE_PIN = 34
SOLO_PH_PIN      = 35
SOLO_NPK_PIN     = 32
LED_VERDE_PIN    = 25
LED_AMARELO_PIN  = 26
LED_VERMELHO_PIN = 27
BUZZER_PIN       = 33
 
# ── Limiares de umidade ─────────────────────────────────────────
UMIDADE_SECO     = 2800
UMIDADE_UMIDO    = 1800
 
# ── Limiares de pH (ADC 0-4095 mapeado para pH 0-14) ───────────
PH_ACIDO_MAX     = 1170   # pH < 4.0 -> muito acido
PH_IDEAL_MIN     = 1750   # pH 6.0
PH_IDEAL_MAX     = 2330   # pH 8.0
PH_ALCALINO_MIN  = 2916   # pH > 10.0 -> muito alcalino
 
# ── Limiares de NPK (ADC 0-4095) ───────────────────────────────
NPK_BAIXO        = 1365   # abaixo de 33% -> deficiente
NPK_ALTO         = 2730   # acima de 66%  -> excesso
 
# ── Estados do solo ─────────────────────────────────────────────
UMIDO    = "UMIDO"
SECO     = "SECO"
REGANDO  = "REGANDO"
 
# ── Inicializacao ───────────────────────────────────────────────
sensor_umidade = ADC(Pin(SOLO_UMIDADE_PIN))
sensor_ph      = ADC(Pin(SOLO_PH_PIN))
sensor_npk     = ADC(Pin(SOLO_NPK_PIN))
 
for s in (sensor_umidade, sensor_ph, sensor_npk):
    s.atten(ADC.ATTN_11DB)
 
led_verde    = Pin(LED_VERDE_PIN,    Pin.OUT)
led_amarelo  = Pin(LED_AMARELO_PIN,  Pin.OUT)
led_vermelho = Pin(LED_VERMELHO_PIN, Pin.OUT)
buzzer       = PWM(Pin(BUZZER_PIN), freq=1000, duty=0)
 
 
# ── Helpers de audio ────────────────────────────────────────────
def beep(freq=1000, ms=200):
    buzzer.freq(freq)
    buzzer.duty(512)
    time.sleep_ms(ms)
    buzzer.duty(0)
 
def silencio():
    buzzer.duty(0)
 
def beep_irrigacao():
    beep(800, 150)
    time.sleep_ms(80)
    beep(800, 150)
 
def beep_nutriente():
    beep(500, 300)
    time.sleep_ms(100)
    beep(700, 300)
 
 
# ── Conversoes ──────────────────────────────────────────────────
def umidade_pct(adc):
    return max(0, min(100, 100 - int((adc / 4095) * 100)))
 
def adc_para_ph(adc):
    """Mapeia ADC 0-4095 para pH 0.0-14.0"""
    return round((adc / 4095) * 14.0, 1)
 
def npk_pct(adc):
    return max(0, min(100, int((adc / 4095) * 100)))
 
 
# ── Diagnostico de pH ───────────────────────────────────────────
def diagnostico_ph(adc):
    ph = adc_para_ph(adc)
    if adc < PH_ACIDO_MAX:
        return ph, "CRITICO", "Solo muito acido! Aplicar calcario urgente."
    elif adc < PH_IDEAL_MIN:
        return ph, "ALERTA",  "Solo acido. Recomendado aplicar calcario."
    elif adc <= PH_IDEAL_MAX:
        return ph, "IDEAL",   "pH ideal para a maioria das culturas."
    elif adc <= PH_ALCALINO_MIN:
        return ph, "ALERTA",  "Solo alcalino. Recomendado aplicar enxofre."
    else:
        return ph, "CRITICO", "Solo muito alcalino! Aplicar enxofre urgente."
 
 
# ── Diagnostico de NPK ──────────────────────────────────────────
def diagnostico_npk(adc):
    pct = npk_pct(adc)
    if adc < NPK_BAIXO:
        return pct, "BAIXO",  "Deficiencia de NPK! Aplicar adubo completo."
    elif adc > NPK_ALTO:
        return pct, "EXCESSO","Excesso de NPK! Reduzir adubacao."
    else:
        return pct, "IDEAL",  "Nivel de nutrientes adequado."
 
 
# ── Maquina de estados de umidade ───────────────────────────────
def proximo_estado_umidade(adc, atual):
    if atual == UMIDO and adc > UMIDADE_SECO:
        return SECO
    if atual in (SECO, REGANDO):
        if adc < UMIDADE_UMIDO:
            return UMIDO
        return REGANDO
    return atual
 
 
# ── Atualiza LEDs ───────────────────────────────────────────────
def atualizar_leds(estado_umidade, alerta_nutriente):
    led_verde.off()
    led_amarelo.off()
    led_vermelho.off()
 
    if estado_umidade in (SECO, REGANDO):
        led_vermelho.on()
    elif alerta_nutriente:
        led_amarelo.on()
    else:
        led_verde.on()
 
 
# ── Boot ────────────────────────────────────────────────────────
print("=" * 48)
print("  Monitoramento e Nutricao de Solo")
print("  ESP32 + MicroPython | Wokwi")
print("=" * 48)
print("Sensores: Umidade | pH | NPK")
print("Iniciando monitoramento...\n")
 
beep(1000, 150)
time.sleep_ms(80)
beep(1200, 150)
time.sleep_ms(80)
beep(1500, 150)
 
estado_umidade = UMIDO
ciclos         = 0
 
# ── Loop principal ───────────────────────────────────────────────
while True:
    # Leituras
    adc_umid = sensor_umidade.read()
    adc_ph   = sensor_ph.read()
    adc_npk  = sensor_npk.read()
 
    # Calculos
    umid_pct              = umidade_pct(adc_umid)
    ph_val, ph_status, ph_msg   = diagnostico_ph(adc_ph)
    npk_val, npk_status, npk_msg = diagnostico_npk(adc_npk)
 
    # Estado de umidade
    novo_estado = proximo_estado_umidade(adc_umid, estado_umidade)
 
    # Mudanca de estado de irrigacao
    if novo_estado != estado_umidade:
        if novo_estado == SECO:
            print("\n[IRRIGACAO] Solo seco! Iniciando irrigacao...")
            beep_irrigacao()
        elif novo_estado == REGANDO:
            ciclos += 1
            buzzer.freq(440)
            buzzer.duty(300)
            print("[IRRIGACAO] Regando... ciclo #{}".format(ciclos))
        elif novo_estado == UMIDO:
            silencio()
            print("[IRRIGACAO] Solo umido. Irrigacao encerrada.\n")
        estado_umidade = novo_estado
 
    # Alertas de nutrientes
    alerta_nutriente = False
 
    if ph_status in ("ALERTA", "CRITICO"):
        alerta_nutriente = True
        print("[pH {}] {} -> {}".format(ph_val, ph_status, ph_msg))
        if ph_status == "CRITICO":
            beep_nutriente()
 
    if npk_status in ("BAIXO", "EXCESSO"):
        alerta_nutriente = True
        print("[NPK {}%] {} -> {}".format(npk_val, npk_status, npk_msg))
        if npk_status == "BAIXO":
            beep_nutriente()
 
    # Atualiza LEDs
    atualizar_leds(estado_umidade, alerta_nutriente)
 
    # Log geral
    print(
        "[Umidade: {:3d}%] [pH: {:4.1f} {}] [NPK: {:3d}% {}] [Estado: {}]".format(
            umid_pct, ph_val, ph_status, npk_val, npk_status, estado_umidade
        )
    )
 
    time.sleep(1)