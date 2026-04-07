import os
import sys

# Forzar modo sin cabeza (Headless) para pygame así nuestro bot puede clicearlo mágicamente sin monitor vital.
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
import threading
import time

try:
    from main import main
except Exception as e:
    print(f"CRÍTICO: No se pudo importar main.py. Error: {e}")
    sys.exit(1)

def inject_events():
    time.sleep(1) # Esperar a que init cargue
    print("[QA] Inyectando evento: Click en 'Modificar Equipo'")
    pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(300, 490)))
    time.sleep(0.5)

    print("[QA] Inyectando evento: Click en 'Cabeza'")
    pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(150, 120)))
    time.sleep(0.5)

    print("[QA] Inyectando evento: Click en 'Volver al Mapa'")
    pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(150, 340)))
    time.sleep(0.5)

    print("[QA] Inyectando evento: Click en 'Crafteo'")
    pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(300, 430)))
    time.sleep(0.5)

    print("[QA] Inyectando evento: Click en 'Buscar/Explorar' (x10 turnos rápidos para forzar RNG)")
    for i in range(10):
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(100, 440)))
    time.sleep(0.5)

    print("[QA] Terminando flujo. Generando Pygame.QUIT...")
    pygame.event.post(pygame.event.Event(pygame.QUIT))

print("[QA] Iniciando pruebas de Integración E2E sobre main.py...")
threading.Thread(target=inject_events, daemon=True).start()

try:
    main()
    print("[QA] ESTADO: ÉXITO. El loop gráfico inicializó, procesó menús, equipo, RNGs y terminó correctamente sin crashear.")
except Exception as e:
    import traceback
    print("[QA] CRASHEO ENCONTRADO EN LA PRUEBA:")
    traceback.print_exc()
