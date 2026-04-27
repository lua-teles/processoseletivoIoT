"""
Sistema de Irrigacao Automatica de Plantas
Simula um sensor de umidade do solo que ativa o regador
quando a umidade estiver abaixo do nivel minimo.
 
Hardware simulado (ESP32):
- Potenciometro no pino 34 (simula sensor de umidade)
- LED verde  no pino 25  (solo umido - planta OK)
- LED vermelho no pino 26 (solo seco  - regando)
- Buzzer no pino 27       (alerta sonoro)
"""
 
from machine import Pin, ADC, PWM
import time
 
# ── Pinos ───────────────────────────────────────────────────────
SOIL_PIN      = 34
LED_GREEN_PIN = 25
LED_RED_PIN   = 26
BUZZER_PIN    = 27
 
# ── Limiares de umidade (ADC 0-4095) ───────────────────────────
# Alto  = seco  (pouca condutividade)
# Baixo = umido (alta condutividade)
LIMIAR_SECO  = 2800   # acima  -> acionar irrigacao
LIMIAR_UMIDO = 1800   # abaixo -> desligar irrigacao
 
# ── Estados ─────────────────────────────────────────────────────
UMIDO   = "UMIDO"
SECO    = "SECO"
REGANDO = "REGANDO"
 
# ── Inicializacao ───────────────────────────────────────────────
sensor = ADC(Pin(SOIL_PIN))
sensor.atten(ADC.ATTN_11DB)
 
led_verde    = Pin(LED_GREEN_PIN, Pin.OUT)
led_vermelho = Pin(LED_RED_PIN,   Pin.OUT)
buzzer       = PWM(Pin(BUZZER_PIN), freq=1000, duty=0)
 
 
# ── Helpers ─────────────────────────────────────────────────────
def beep(freq=1000, ms=200):
    buzzer.freq(freq)
    buzzer.duty(512)
    time.sleep_ms(ms)
    buzzer.duty(0)
 
 
def silencio():
    buzzer.duty(0)
 
 
def atualizar_leds(estado):
    if estado == UMIDO:
        led_verde.on()
        led_vermelho.off()
    else:
        led_verde.off()
        led_vermelho.on()
 
 
def umidade_pct(adc):
    """Converte leitura ADC em percentual de umidade (0-100%)."""
    return max(0, min(100, 100 - int((adc / 4095) * 100)))
 
 
def proximo_estado(adc, atual):
    """Maquina de estados com histerese."""
    if atual == UMIDO and adc > LIMIAR_SECO:
        return SECO
    if atual in (SECO, REGANDO):
        if adc < LIMIAR_UMIDO:
            return UMIDO
        return REGANDO
    return atual
 
 
# ── Boot ────────────────────────────────────────────────────────
print("Irrigacao Automatica de Plantas")
print("ESP32 + MicroPython | Wokwi")
print("Monitorando umidade do solo...")
 
beep(1000, 200)
time.sleep_ms(100)
beep(1200, 200)
 
estado  = UMIDO
ciclos  = 0
 
# ── Loop principal ───────────────────────────────────────────────
while True:
    adc   = sensor.read()
    pct   = umidade_pct(adc)
    novo  = proximo_estado(adc, estado)
 
    if novo != estado:
        if novo == SECO:
            print("ALERTA: Solo seco! Iniciando irrigacao...")
            beep(800, 150)
            time.sleep_ms(80)
            beep(800, 150)
 
        elif novo == REGANDO:
            ciclos += 1
            buzzer.freq(440)
            buzzer.duty(300)
            print("Regando... ciclo #{}".format(ciclos))
 
        elif novo == UMIDO:
            silencio()
            print("Solo umido. Irrigacao encerrada.")
 
        estado = novo
 
    atualizar_leds(estado)
 
    print("[Umidade: {:3d}%]  [ADC: {:4d}]  [Estado: {}]".format(pct, adc, estado))
 
    time.sleep(1)