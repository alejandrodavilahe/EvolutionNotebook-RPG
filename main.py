import pygame
import sys
import random
import os
from core.player import Player
from core.ui import Button, draw_bar, draw_text_box, draw_inventory
from core.world import World

# Colores estéticos limpios/minimalistas
BG_COLOR = (245, 245, 240)  # Tono hueso / libreta clara
TEXT_COLOR = (40, 40, 40)
BTN_COLOR = (220, 220, 215)
BTN_HOVER = (200, 200, 195)

BAR_COLORS = {
    "hp": (220, 90, 90),       # Rojo desaturado
    "hunger": (210, 150, 70),  # Naranja desaturado
    "thirst": (90, 160, 210),  # Azul desaturado
    "energy": (230, 210, 80)   # Amarillo quemado
}

def get_next_equip(current, possible, inv):
    available = [i for i in possible if inv.get(i, 0) > 0]
    available.insert(0, None)
    try:
        idx = available.index(current)
        return available[(idx + 1) % len(available)]
    except ValueError:
        return available[0]

def main():
    pygame.init()
    pygame.mixer.init()
    if os.path.exists("assets/bgm.wav"):
        try:
            pygame.mixer.music.load("assets/bgm.wav")
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)
        except: pass

    screen_width, screen_height = 1000, 720
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Evolution Notebook")
    clock = pygame.time.Clock()

    # Fuentes limpias del sistema
    font_main = pygame.font.SysFont("couriernew", 22, bold=True)
    font_small = pygame.font.SysFont("couriernew", 16)
    font_title = pygame.font.SysFont("couriernew", 28, bold=True)

    player = Player()
    world = World()
    game_state = "MAP"
    current_message = f"Te encuentras en el bioma: {world.current_biome}."
    current_enemy = None

    # Instanciacion de botones Map
    btn_search = Button(50, 555, 220, 50, "Buscar / Explorar", font_main, BTN_COLOR, TEXT_COLOR, BTN_HOVER)
    btn_rest = Button(280, 555, 220, 50, "Descansar", font_main, BTN_COLOR, TEXT_COLOR, BTN_HOVER)
    btn_craft = Button(510, 555, 220, 50, "Crafteo / Ideas", font_main, (210, 230, 210), TEXT_COLOR, (190, 210, 190))
    
    btn_equip = Button(50, 615, 220, 50, "🎒 Equipo", font_main, (200, 220, 240), TEXT_COLOR, (180, 200, 220))
    btn_tribe = Button(280, 615, 220, 50, "Manejar Tribu", font_main, (240, 230, 180), TEXT_COLOR, (220, 210, 160))
    btn_camp = Button(510, 615, 220, 50, "⛺ Campamento", font_main, (240, 230, 180), TEXT_COLOR, (220, 210, 160))
    
    btn_craft_mix = Button(510, 555, 220, 50, "Mezclar Ítems", font_small, (200, 150, 150), TEXT_COLOR, (180, 130, 130))
    btn_craft_cancel = Button(510, 615, 220, 50, "Cancelar", font_small, (150, 150, 150), TEXT_COLOR, (130, 130, 130))

    btn_fight_atk = Button(50, 555, 220, 50, "Atacar", font_main, (210, 100, 100), TEXT_COLOR, (190, 80, 80))
    btn_fight_def = Button(280, 555, 220, 50, "Cubrirse", font_main, (140, 160, 220), TEXT_COLOR, (120, 140, 200))
    btn_flee = Button(510, 555, 220, 50, "Huir (-Ene)", font_main, (180, 180, 150), TEXT_COLOR, (160, 160, 130))

    btn_travel = Button(50, 555, 330, 50, "Avanzar a la Zona", font_main, (160, 200, 160), TEXT_COLOR, (140, 180, 140))
    btn_ignore = Button(400, 555, 330, 50, "Ignorar / Seguir", font_main, (200, 180, 160), TEXT_COLOR, (180, 160, 140))

    btn_opp_take = Button(50, 555, 330, 50, "Aprovechar (-Ene)", font_main, (210, 200, 120), TEXT_COLOR, (190, 180, 100))
    
    btn_drink_clean = Button(350, 280, 190, 25, "Beber Agua Pura", font_small, (100, 160, 220), TEXT_COLOR, (80, 140, 200))
    btn_drink_dirty = Button(350, 310, 190, 25, "Beber A. Turbia", font_small, (150, 160, 130), TEXT_COLOR, (130, 140, 110))
    btn_boil = Button(350, 340, 190, 25, "🔥 Hervir Líquido", font_small, (220, 140, 100), TEXT_COLOR, (200, 120, 80))
    
    btn_restart = Button(380, 600, 240, 50, "Mudar al Panteón", font_title, (220, 200, 200), TEXT_COLOR, (200, 180, 180))
    btn_reincarnate = Button(700, 650, 260, 50, "REENCARNAR", font_title, (250, 220, 150), TEXT_COLOR, (230, 200, 130))
    btn_perk_meta = Button(200, 200, 600, 40, "MUTAR: Súper Metabolismo (+40 Max Hambre/Sed) [Coste: 30 PA]", font_small, (180, 220, 180), TEXT_COLOR, (160, 200, 160))
    btn_perk_skin = Button(200, 250, 600, 40, "MUTAR: Piel Rinoceronte (+5 Defensa Perpetua) [Coste: 50 PA]", font_small, (220, 180, 180), TEXT_COLOR, (200, 160, 160))
    btn_perk_dmg = Button(200, 300, 600, 40, "MUTAR: Brazos de Gorila (+3 Daño Base Perpetuo) [Coste: 60 PA]", font_small, (220, 200, 150), TEXT_COLOR, (200, 180, 130))
    btn_perk_eff = Button(200, 350, 600, 40, "MUTAR: Ojos de Búho (Menos cansancio/Más suerte) [Coste: 45 PA]", font_small, (190, 200, 220), TEXT_COLOR, (170, 180, 200))
    btn_perk_res = Button(200, 400, 600, 40, "MUTAR: Anticuerpos (Anti-Disentería Perpetua) [Coste: 80 PA]", font_small, (150, 220, 190), TEXT_COLOR, (130, 200, 170))
    btn_eq_head = Button(50, 100, 300, 40, "Cabeza: Nada", font_main, BTN_COLOR, TEXT_COLOR, BTN_HOVER)
    btn_eq_body = Button(50, 150, 300, 40, "Tórax: Nada", font_main, BTN_COLOR, TEXT_COLOR, BTN_HOVER)
    btn_eq_weapon = Button(50, 200, 300, 40, "Arma: Puños", font_main, BTN_COLOR, TEXT_COLOR, BTN_HOVER)
    btn_eq_boots = Button(50, 250, 300, 40, "Pies: Nada", font_main, BTN_COLOR, TEXT_COLOR, BTN_HOVER)
    btn_eq_back = Button(50, 320, 300, 40, "<- Volver al Mapa", font_main, (250, 200, 200), TEXT_COLOR, (230, 180, 180))

    GEAR_TYPES = {
        "Head": ["Casco de Hueso"],
        "Body": ["Abrigo Básico", "Peto Escamoso", "Abrigo de Invierno"],
        "Weapon": ["Cuchillo Óseo", "Cuchillo de Pedernal", "Hacha Primitiva", "Pico de Hueso", "Lanza Caza", "Lanza de Obsidiana"],
        "Boots": ["Botas de Piel"]
    }
    
    pending_landmark = ""
    pending_biome = None
    pending_opp = None
    pantheon_data = {"puntos": 0, "perks": [], "generation": 1}
    
    crafting_selected = []
    inv_slots = []
    
    weather_timer = 0
    weather_active = None
    weather_warning = False
    weather_pending_type = None
    weather_pending_time = 0
    
    running = True
    while running:
        turn_taken = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Eventos unicamente activos si estamos vivos
            if player.alive:
                if game_state == "MAP":
                    if btn_search.handle_event(event):
                        pas_msg = player.search()
                        evt = world.generate_search_event()
                        if evt["type"] == "nothing":
                            current_message = "Buscaste exhaustivamente pero no encontraste nada útil."
                        elif evt["type"] == "resource":
                            player.heal_stat(evt["data"]["stat"], evt["data"]["amount"])
                            if "item" in evt["data"]:
                                player.add_to_inventory(evt["data"]["item"], evt["data"]["item_amt"])
                            if "herb" in evt["data"] and evt["data"]["herb_amt"] > 0:
                                player.add_to_inventory(evt["data"]["herb"], evt["data"]["herb_amt"])
                            current_message = f"Encontraste {evt['data']['name']}. "
                            if evt["data"]["stat"] == "thirst":
                                if "Odre de Agua" in player.known_recipes:
                                    player.inventory["Agua Turbia"] = 3
                                    current_message += "¡Recargaste tu Odre con Agua Turbia de lugar!"
                                if random.random() < 0.15 and "Disentería" not in player.sickness:
                                    if "ANTICUERPOS" not in player.perks_active:
                                        player.sickness.append("Disentería")
                                        current_message += " (Tragaste un bicho asqueroso de la cuenca... contrajiste Disentería al usar tus manos)"
                        elif evt["type"] == "enemy":
                            current_enemy = evt["data"]
                            current_message = f"¡PELIGRO! Un {current_enemy['name']} salvaje (Daño: {current_enemy['dmg']})."
                            game_state = "ENCOUNTER"
                        elif evt["type"] == "landmark":
                            pending_landmark = evt["data"]["name"]
                            pending_biome = None
                            current_message = f"Avistaste un lugar persistente: {pending_landmark}. ¿Deseas explorar?"
                            game_state = "DECISION"
                        elif evt["type"] == "transition":
                            pending_landmark = evt["data"]["name"]
                            pending_biome = evt["data"]["target"]
                            current_message = f"Hallaste un sendero largo: {pending_landmark}. ¿Deseas viajar/migrar?"
                            game_state = "DECISION"
                        elif evt["type"] == "opportunity":
                            pending_opp = evt["data"]
                            current_message = f"Evento Oportuno: {pending_opp['name']}\n{pending_opp['desc']}"
                            game_state = "OPPORTUNITY"
                        elif evt["type"] == "mineral":
                            if evt["data"]["tool_req"] in player.known_recipes:
                                player.add_to_inventory(evt["data"]["item"], evt["data"]["amt"])
                                current_message = f"Minaste con éxito: {evt['data']['name']}. (+{evt['data']['item']} x{evt['data']['amt']})"
                            else:
                                current_message = f"Topaste un {evt['data']['name']}, necesitas el Craft <{evt['data']['tool_req']}> para extraer mineral."
                        turn_taken = True
                            
                    if btn_rest.handle_event(event):
                        player.rest(world.camp_level)
                        turn_taken = True
                        if world.camp_level > 0:
                            current_message = f"Descansas profundamente y cocinas en tu Campamento Lvl {world.camp_level}."
                        else:
                            current_message = "Has descansado en la intemperie desprotegido."
                            
                    if btn_equip.handle_event(event):
                        game_state = "EQUIP"
                        current_message = "Te miras a ti mismo... (Pulsa en los huecos para ciclar el equipo que posees en la mochila)."
                            
                    if player.inventory.get("Cargas Agua", 0) > 0 and btn_drink_clean.handle_event(event):
                        player.inventory["Cargas Agua"] -= 1
                        player.heal_stat("thirst", 40)
                        current_message = f"Diste un fuerte sorbo P U R O. Te restan {player.inventory['Cargas Agua']} cargas Limpias."
                    
                    if player.inventory.get("Agua Turbia", 0) > 0 and btn_drink_dirty.handle_event(event):
                        player.inventory["Agua Turbia"] -= 1
                        player.heal_stat("thirst", 40)
                        current_message = "Bebiste un trago lodoso para evitar la deshidratación..."
                        if random.random() < 0.35 and "Disentería" not in player.sickness:
                            if "ANTICUERPOS" not in player.perks_active:
                                player.sickness.append("Disentería")
                                current_message += " ¡La porquería microbiana te causó Disentería aguda!"
                            
                    if world.camp_level > 0 and player.inventory.get("Agua Turbia", 0) > 0 and btn_boil.handle_event(event):
                        if player.inventory.get("Fibra", 0) > 0 or player.inventory.get("Carbón", 0) > 0:
                            if player.inventory.get("Carbón", 0) > 0: player.inventory["Carbón"] -= 1
                            else: player.inventory["Fibra"] -= 1
                            player.inventory["Agua Turbia"] -= 1
                            player.inventory["Cargas Agua"] = player.inventory.get("Cargas Agua", 0) + 1
                            current_message = "Metiste piedras al fuego y purificaste biológicamente con vapor 1 Carga Turbia hacia Limpia."
                        else:
                            current_message = "Para hervir y aniquilar patógenos ocupas combustible en el fuego (Fibra o Carbón)."

                    if btn_camp.handle_event(event):
                        if not world.has_camp:
                            if player.inventory.get("Fibra", 0) >= 2:
                                if player.energy < 25:
                                    current_message = "Estás cansado para levantar un campamento básico (req 25 Ene)."
                                else:
                                    player.inventory["Fibra"] -= 2
                                    player.consume_energy(25)
                                    world.has_camp = True
                                    world.camp_level = 1
                                    current_message = f"¡Excelente! Armaste yesca cruzada e iniciaste un campamento fogata en {world.current_location}."
                            else:
                                current_message = "Para fundar el primer campamento con fogata necesitas [Fibra x2] o leña inicial."
                        elif world.camp_level == 1:
                            if player.inventory.get("Fibra", 0) >= 3 and player.inventory.get("Huesos", 0) >= 2:
                                player.inventory["Fibra"] -= 3
                                player.inventory["Huesos"] -= 2
                                world.camp_level = 2
                                current_message = "Construyes estacas y muros rudimentarios. ¡Campamento Nivel 2!"
                            else:
                                current_message = "Para mejorar necesitas [Fibra x3] y [Huesos x2]."
                        elif world.camp_level == 2:
                            if player.inventory.get("Piel", 0) >= 3 and player.inventory.get("Fibra", 0) >= 2:
                                player.inventory["Piel"] -= 3
                                player.inventory["Fibra"] -= 2
                                world.camp_level = 3
                                current_message = "Construiste una imponente tienda. ¡Campamento Nivel 3!"
                            else:
                                current_message = "Para la tienda pesada requieres [Piel x3] y [Fibra x2]."
                        elif world.camp_level == 3 and world.era == 1:
                            if player.inventory.get("Pedernal", 0) >= 5 and player.inventory.get("Huesos", 0) >= 10:
                                player.inventory["Pedernal"] -= 5
                                player.inventory["Huesos"] -= 10
                                world.era = 2
                                player.era = 2
                                player.evolution_stage = "Asentado (Era 2)"
                                current_message = "¡GRAN HITO! Levantaste tu primera Forja Humana. Avanzaste a la ERA DE LOS METALES (Era 2)."
                            else:
                                current_message = "Requiere [Pedernal x5] y [Huesos x10] para hacer la Forja de Piedra e inaugurar la Era."

                    if btn_craft.handle_event(event):
                        game_state = "CRAFTING"
                        crafting_selected = []
                        current_message = "MODO DE CRAFTEO: Selecciona dos ítems del inventario dándoles click y pulsa 'Mezclar Ítems'."
                    if player.in_tribe and btn_tribe.handle_event(event):
                        if player.is_chief:
                            current_message = "Los pobladores asienten y te dejan gobernar."
                        else:
                            if player.tribe_rep >= 100:
                                current_enemy = {"name": "Jefe Tribal Alpha", "dmg": 40, "hp": 150, "drops": {"Pedernal": (3, 6), "Milenrama": (2, 5), "Carne Asada": (2, 4)}}
                                current_message = "¡RUGES EXIGIENDO EL CONTRAL! El Jefe Alpha se abalanza y comienza un duelo a muerte."
                                game_state = "ENCOUNTER"
                            else:
                                if player.inventory.get("Carne Cruda", 0) >= 5:
                                    player.inventory["Carne Cruda"] -= 5
                                    player.tribe_rep += 15
                                    current_message = f"Donas carne para la Tribu. Rep. Tribal sube a {player.tribe_rep}."
                                else:
                                    current_message = "Gánate el respeto como Jefe donando 5 de Carne Cruda a tu Tribu."
                            
                elif game_state == "ENCOUNTER":
                    if btn_fight_atk.handle_event(event):
                        en_name = current_enemy["name"]
                        # Tu turno
                        current_enemy["hp"] -= player.base_dmg
                        if current_enemy["hp"] <= 0:
                            if en_name == "Jefe Tribal Alpha":
                                player.is_chief = True
                                player.evolution_stage = "Supremo Tribal"
                                current_message = "¡LO CORTASTE AL EJE! La tribu te jura lealtad. Eres Jefe."
                            else:
                                dropped = []
                                for i_name, (min_amt, max_amt) in current_enemy.get("drops", {}).items():
                                    amt = random.randint(min_amt, max_amt)
                                    if amt > 0:
                                        player.add_to_inventory(i_name, amt)
                                        dropped.append(f"{amt}x {i_name}")
                                player.heal_stat("hunger", 15)
                                drops_txt = ", ".join(dropped)
                                current_message = f"¡Masacraste al {en_name}! Ganaste: {drops_txt}"
                            game_state = "MAP"
                        else:
                            # Turno enemigo
                            recibido = player.take_enemy_hit(en_name, current_enemy["dmg"], 1.0)
                            if player.alive:
                                current_message = f"Hiciste {player.base_dmg} de daño. ¡El {en_name} sangra pero sobrevive! Te embiste por {recibido} de daño."
                                
                    if btn_fight_def.handle_event(event):
                        en_name = current_enemy["name"]
                        recibido = player.take_enemy_hit(en_name, current_enemy["dmg"], 0.4)
                        if player.alive:
                            current_message = f"Te cubres ferozmente. El {en_name} rompe en tu defensa para {recibido} de daño."
                        
                    if btn_flee.handle_event(event):
                        player.consume_energy(15)
                        if random.random() < 0.6:
                            current_message = "¡Logras deshacerte del conflicto temblando y corres de la zona!"
                            game_state = "MAP"
                        else:
                            en_name = current_enemy["name"]
                            recibido = player.take_enemy_hit(en_name, current_enemy["dmg"], 0.75)
                            if player.alive:
                                current_message = f"¡Tropezaste huyendo! El {en_name} te rasga la espalda causándote {recibido} daño."

                elif game_state == "DECISION":
                    if btn_travel.handle_event(event):
                        pas_msg = player.pass_turn(action_cost={"hunger": 8, "thirst": 8, "energy": 20})
                        if pending_biome:
                            world.current_biome = pending_biome
                            world.current_location = "Zona Abierta"
                            current_message = f"Pasaron los días... Bienvenidos al nuevo bioma: {pending_biome}. {pas_msg}"
                        else:
                            world.current_location = pending_landmark
                            current_message = f"Has migrado tu expedición hacia: {pending_landmark}. {pas_msg}"
                            
                        world.has_camp = False
                        pending_biome = None
                        game_state = "MAP"
                        turn_taken = True
                    if btn_ignore.handle_event(event):
                        current_message = "Decidiste ignorarlo y quedarte en tu área designada."
                        game_state = "MAP"

                elif game_state == "OPPORTUNITY":
                    if btn_opp_take.handle_event(event):
                        cost = pending_opp.get("cost", {})
                        player.consume_energy(cost.get("energy", 0))
                        
                        rew_str = []
                        if "reward" in pending_opp:
                            for item, (min_amt, max_amt) in pending_opp["reward"].items():
                                if min_amt > 0 or max_amt > 0:
                                    amt = random.randint(min_amt, max_amt)
                                    player.add_to_inventory(item, amt)
                                    rew_str.append(f"{item} x{amt}")
                                    
                        if "boost" in pending_opp:
                            for stat, amt in pending_opp["boost"].items():
                                player.heal_stat(stat, amt)
                                
                        current_message = "¡Lograste aprovechar la oportunidad nutritiva!"
                        if rew_str:
                            current_message += " Extraídos: " + ", ".join(rew_str) + "."
                            
                        if pending_opp.get("risk_disease"):
                            if random.random() < pending_opp["risk_chance"]:
                                if pending_opp["risk_disease"] not in player.sickness:
                                    player.sickness.append(pending_opp["risk_disease"])
                                    current_message += f"\n(Te duele... Contrajiste {pending_opp['risk_disease']})"
                                    
                        if pending_opp.get("special") == "TRIBU":
                            if random.random() < 0.3:
                                current_message = "¡El humo era carnada caníbal! Te emboscan sin piedad de inmediato."
                                current_enemy = {"name": "Guerrero Caníbal", "dmg": 35, "hp": 80, "drops": {"Carne Cruda": (5, 10), "Huesos": (2, 5)}}
                                game_state = "ENCOUNTER"
                            else:
                                player.in_tribe = True
                                player.tribe_rep = 10
                                world.has_camp = True
                                world.camp_level = 3
                                world.current_location = "Asentamiento Tribal"
                                current_message = "Muestras sumisión dando ramas y te adhieren a su eslabón más bajo social. Tienes Aldea."
                                game_state = "MAP"
                        else:
                            game_state = "MAP"
                        turn_taken = True
                    if btn_ignore.handle_event(event):
                        current_message = "Pasas de largo el evento extraño cautelosamente."
                        game_state = "MAP"
                        turn_taken = True
                
                elif game_state == "CRAFTING":
                    # Detectar clicks en slots del inventario
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        for slot in inv_slots:
                            if slot["rect"].collidepoint(event.pos):
                                if slot["item"] in crafting_selected:
                                    crafting_selected.remove(slot["item"])
                                elif len(crafting_selected) < 2:
                                    crafting_selected.append(slot["item"])
                                
                    if btn_craft_mix.handle_event(event):
                        current_message = player.manual_craft(crafting_selected)
                        game_state = "MAP"
                        turn_taken = True
                        crafting_selected = []
                    if btn_craft_cancel.handle_event(event):
                        current_message = "Adversión retractada. Vuelves al mapa."
                        game_state = "MAP"
                        crafting_selected = []
                        
                elif game_state == "EQUIP":
                    if btn_eq_back.handle_event(event):
                        game_state = "MAP"
                        current_message = "Reajustaste tu carga táctica. Estás listo."
                    if btn_eq_head.handle_event(event):
                        player.equipment["Head"] = get_next_equip(player.equipment.get("Head"), GEAR_TYPES["Head"], player.inventory)
                    if btn_eq_body.handle_event(event):
                        player.equipment["Body"] = get_next_equip(player.equipment.get("Body"), GEAR_TYPES["Body"], player.inventory)
                    if btn_eq_weapon.handle_event(event):
                        player.equipment["Weapon"] = get_next_equip(player.equipment.get("Weapon"), GEAR_TYPES["Weapon"], player.inventory)
                    if btn_eq_boots.handle_event(event):
                        player.equipment["Boots"] = get_next_equip(player.equipment.get("Boots"), GEAR_TYPES["Boots"], player.inventory)
                    player.update_stats_from_gear()
                    
            else:
                if game_state != "PANTHEON":
                    if btn_restart.handle_event(event):
                        game_state = "PANTHEON"
                        # Generate or fetch points upon entering Pantheon (Rebalanced)
                        pts_gained = (player.turn * 15) + (50 if player.era > 1 else 0)
                        try:
                            import json
                            with open("savegame.json", "r") as f:
                                dt = json.load(f)
                                pd = dt.get("puntos", 0)
                                pk = dt.get("perks", [])
                                gen = dt.get("generation", 1)
                        except:
                            pd, pk, gen = 0, [], 1
                        
                        pantheon_data["puntos"] = pd + pts_gained
                        pantheon_data["perks"] = pk
                        pantheon_data["generation"] = gen
                        player.save_pantheon(pantheon_data["puntos"], pk, gen)
                else:
                    if btn_perk_meta.handle_event(event) and "METABOLISMO" not in pantheon_data["perks"]:
                        if pantheon_data["puntos"] >= 30:
                            pantheon_data["puntos"] -= 30
                            pantheon_data["perks"].append("METABOLISMO")
                            player.save_pantheon(pantheon_data["puntos"], pantheon_data["perks"], pantheon_data["generation"])
                            
                    if btn_perk_skin.handle_event(event) and "PIEL_GRUESA" not in pantheon_data["perks"]:
                        if pantheon_data["puntos"] >= 50:
                            pantheon_data["puntos"] -= 50
                            pantheon_data["perks"].append("PIEL_GRUESA")
                            player.save_pantheon(pantheon_data["puntos"], pantheon_data["perks"], pantheon_data["generation"])
                            
                    if btn_perk_dmg.handle_event(event) and "BRAZOS_GORILA" not in pantheon_data["perks"]:
                        if pantheon_data["puntos"] >= 60:
                            pantheon_data["puntos"] -= 60
                            pantheon_data["perks"].append("BRAZOS_GORILA")
                            player.save_pantheon(pantheon_data["puntos"], pantheon_data["perks"], pantheon_data["generation"])

                    if btn_perk_eff.handle_event(event) and "OJOS_BUHO" not in pantheon_data["perks"]:
                        if pantheon_data["puntos"] >= 45:
                            pantheon_data["puntos"] -= 45
                            pantheon_data["perks"].append("OJOS_BUHO")
                            player.save_pantheon(pantheon_data["puntos"], pantheon_data["perks"], pantheon_data["generation"])

                    if btn_perk_res.handle_event(event) and "ANTICUERPOS" not in pantheon_data["perks"]:
                        if pantheon_data["puntos"] >= 80:
                            pantheon_data["puntos"] -= 80
                            pantheon_data["perks"].append("ANTICUERPOS")
                            player.save_pantheon(pantheon_data["puntos"], pantheon_data["perks"], pantheon_data["generation"])
                            
                    if btn_reincarnate.handle_event(event):
                        player = Player()
                        world = World()
                        game_state = "MAP"
                        current_message = f"Has reencarnado (Generación {player.generation}). Un nuevo comienzo..."
                        

        if turn_taken and player.alive and game_state == "MAP":
            w_msg = ""
            
            # Hipotermia en biomas frios
            if world.current_biome in ["Tundra", "Taiga"] and not "Hipotermia" in player.sickness:
                if player.defense < 8 and random.random() < 0.15:
                    player.sickness.append("Hipotermia")
                    w_msg += "\n(El frío congelante entra en tus huesos... Hipotermia)"
                    
            if weather_warning:
                weather_active = weather_pending_type
                weather_timer = weather_pending_time
                w_msg += f"\n¡Ha comenzado: {weather_active}!"
                weather_warning = False
            elif weather_active:
                weather_timer -= 1
                if weather_timer <= 0:
                    w_msg += f"\n{weather_active} se ha disipado. Todo vuelve a la normalidad."
                    weather_active = None
                else:
                    if world.camp_level == 0:
                        player.hp -= 15
                        player.energy = max(0, player.energy - 15)
                        w_msg += f"\n[Intemperie Brutal por {weather_active} -15HP -15E]"
                    elif world.camp_level == 1:
                        player.hp -= 5
                        w_msg += f"\n[El viento colapsa tu campamento... daño leve -5HP]"
                    else:
                        w_msg += f"\n(Te resguardas seguro del {weather_active} en tu Refugio Nivel {world.camp_level})"
            else:
                if random.random() < 0.08:
                    evt_list = world.get_weather_events()
                    if evt_list:
                        ev = random.choice(evt_list)
                        weather_warning = True
                        weather_pending_type = ev["name"]
                        weather_pending_time = random.randint(ev["min_t"], ev["max_t"])
                        w_msg += f"\n⚠️ {ev['warning']}"
            
            sick_msg = player.check_disease_damage()
            if sick_msg:
                w_msg += f"\n{sick_msg}"
                
            current_message += w_msg

        # Renderizado de Paisaje y Fondo
        screen.fill(BG_COLOR)
        
        bio = world.current_biome
        if bio == "Desierto":
            pygame.draw.polygon(screen, (240, 230, 200), [(0, 480), (300, 390), (600, 440), (800, 350), (800, 600), (0, 600)])
            pygame.draw.circle(screen, (250, 220, 140), (650, 150), 40)
        elif bio == "Selva Tropical" or bio == "Pantano Manglar":
            pygame.draw.polygon(screen, (200, 230, 200), [(0, 400), (200, 350), (450, 420), (800, 300), (800, 600), (0, 600)])
            pygame.draw.rect(screen, (170, 210, 170) if bio == "Selva Tropical" else (160, 180, 160), (0, 500, 800, 100))
        elif bio == "Tundra" or bio == "Picos Alpinos":
            pygame.draw.polygon(screen, (230, 245, 255), [(0, 300), (150, 150), (350, 320), (550, 120), (800, 350), (800, 600), (0, 600)])
        elif bio == "Erial Volcánico":
            pygame.draw.polygon(screen, (200, 180, 180), [(0, 500), (200, 450), (400, 300), (500, 460), (800, 420), (800, 600), (0, 600)])
            pygame.draw.line(screen, (220, 80, 80), (400, 300), (450, 600), 10)
        else: # Bosques, Praderas
            pygame.draw.polygon(screen, (215, 235, 205), [(0, 450), (400, 400), (800, 420), (800, 600), (0, 600)])

        # Renderizado de Textos Principales y Localizacion
        title_surf = font_title.render(f"Gen {player.generation} - {player.evolution_stage} [ERA {world.era}]", True, TEXT_COLOR)
        
        camp_txt = "⛺ (Seguro)" if world.has_camp else "(A la intemperie)"
        loc_surf = font_main.render(f"Zona: {world.current_location} {camp_txt}", True, (50, 120, 160) if world.has_camp else TEXT_COLOR)
        
        turn_surf = font_main.render(f"Días de Supervivencia: {player.turn}", True, TEXT_COLOR)
        
        screen.blit(title_surf, (30, 20))
        screen.blit(loc_surf, (30, 50))
        screen.blit(turn_surf, (30, 80))

        # Dibujo rudimentario del jugador usando formas limpias y minimalistas
        center_x, center_y = 500, 300
        
        # Color dinámico por estado de salud
        base_color = TEXT_COLOR
        if "Envenenamiento" in player.sickness:
            base_color = (60, 180, 60) # Verde lima oscuro
        elif "Hipotermia" in player.sickness:
            base_color = (130, 180, 250) # Azul hieloso
        elif "Disentería" in player.sickness:
            base_color = (200, 200, 90) # Amarillo amarillento
        
        pygame.draw.circle(screen, base_color, (center_x, center_y), 30, width=3) # Cabeza
        pygame.draw.line(screen, base_color, (center_x, center_y + 30), (center_x, center_y + 100), 3) # Torso
        pygame.draw.line(screen, base_color, (center_x, center_y + 50), (center_x - 30, center_y + 80), 3) # Brazo izq
        pygame.draw.line(screen, base_color, (center_x, center_y + 50), (center_x + 30, center_y + 80), 3) # Brazo der
        pygame.draw.line(screen, base_color, (center_x, center_y + 100), (center_x - 20, center_y + 150), 3) # Pierna izq
        pygame.draw.line(screen, base_color, (center_x, center_y + 100), (center_x + 20, center_y + 150), 3) # Pierna der
        
        # Superposicion de piezas modulares del RPG Equipment System
        bg_eq = player.equipment.get("Body")
        if bg_eq == "Peto Escamoso":
            pygame.draw.polygon(screen, (80, 140, 90), [(center_x-15, center_y+40), (center_x+15, center_y+40), (center_x+10, center_y+90), (center_x-10, center_y+90)])
        elif bg_eq == "Abrigo Básico" or bg_eq == "Abrigo de Invierno":
            pygame.draw.polygon(screen, (130, 90, 60), [(center_x-18, center_y+30), (center_x+18, center_y+30), (center_x+25, center_y+110), (center_x-25, center_y+110)])
            
        hd_eq = player.equipment.get("Head")
        if hd_eq == "Casco de Hueso":
            pygame.draw.arc(screen, (240, 240, 230), [center_x-35, center_y-35, 70, 70], 0, 3.14, 5) # Medio circulo superior extra
            
        bt_eq = player.equipment.get("Boots")
        if bt_eq == "Botas de Piel":
            pygame.draw.rect(screen, (100, 60, 40), (center_x-25, center_y+140, 15, 15))
            pygame.draw.rect(screen, (100, 60, 40), (center_x+10, center_y+140, 15, 15))
            
        wp_eq = player.equipment.get("Weapon")
        if wp_eq == "Lanza de Obsidiana" or wp_eq == "Lanza Caza":
            color_L = (40, 40, 40) if wp_eq == "Lanza de Obsidiana" else (200, 150, 100)
            pygame.draw.line(screen, color_L, (center_x + 20, center_y + 110), (center_x + 50, center_y - 20), 6) # Larga lanza
            pygame.draw.circle(screen, (200, 50, 50) if wp_eq == "Lanza de Obsidiana" else (220, 220, 200), (center_x + 52, center_y - 25), 5) # Punta
        elif wp_eq == "Hacha Primitiva" or wp_eq == "Pico de Hueso":
            pygame.draw.line(screen, (130, 90, 50), (center_x + 30, center_y + 80), (center_x + 30, center_y + 30), 5) # Mango
            pygame.draw.line(screen, (220, 220, 220), (center_x + 20, center_y + 30), (center_x + 40, center_y + 30), 8) # Cabezal
        elif wp_eq == "Cuchillo de Pedernal" or wp_eq == "Cuchillo Óseo":
            pygame.draw.line(screen, (180, 180, 170), (center_x + 30, center_y + 80), (center_x + 35, center_y + 60), 4)

        # Renderizado de Estadísticas a un lado
        stats_x = 740
        draw_bar(screen, stats_x, 150, 220, 20, player.hp, player.max_hp, BAR_COLORS["hp"], "Vida", font_small)
        draw_bar(screen, stats_x, 210, 220, 20, player.hunger, player.max_hunger, BAR_COLORS["hunger"], "Hambre (Comida)", font_small)
        draw_bar(screen, stats_x, 270, 220, 20, player.thirst, player.max_thirst, BAR_COLORS["thirst"], "Sed (Agua)", font_small)
        draw_bar(screen, stats_x, 330, 220, 20, player.energy, player.max_energy, BAR_COLORS["energy"], "Energía", font_small)

        # Renderizado interactivo y sub-paneles
        # UI global que siempre se ve
        inv_slots = draw_inventory(screen, 740, 400, 240, 250, player.inventory, font_small, font_main)

        # Etiqueta visual para climas/estados especiales
        if weather_active:
            weather_surf = font_main.render(f"CLIMA ACTIVO: {weather_active}", True, (200, 100, 100))
            screen.blit(weather_surf, (30, 310))
        if player.sickness:
            sick_surf = font_small.render(f"Pestes: {', '.join(player.sickness)}", True, (150, 60, 180))
            screen.blit(sick_surf, (50, 400))

        if player.alive:
            draw_text_box(screen, current_message, 50, 430, 680, 120, font_small)
            if game_state == "MAP":
                btn_search.draw(screen)
                btn_rest.draw(screen)
                btn_craft.draw(screen)
                btn_equip.draw(screen)
                
                if player.inventory.get("Cargas Agua", 0) > 0:
                        btn_drink_clean.draw(screen)
                if player.inventory.get("Agua Turbia", 0) > 0:
                        btn_drink_dirty.draw(screen)
                if world.camp_level > 0 and player.inventory.get("Agua Turbia", 0) > 0:
                        btn_boil.draw(screen)
                    
                if not world.has_camp:
                    btn_camp.text = "⛺ Campamento"
                    btn_camp.color = (240, 230, 180)
                elif world.camp_level == 1:
                    btn_camp.text = "⛺ Mejorar Nvl 2"
                    btn_camp.color = (210, 220, 180)
                elif world.camp_level == 2:
                    btn_camp.text = "⛺ Tienda Nvl 3"
                    btn_camp.color = (180, 210, 180)
                else:
                    if world.era == 1:
                        btn_camp.text = "🌋 Eregir Forja"
                        btn_camp.color = (250, 150, 150)
                    else:
                        btn_camp.text = "🏕️ Base Élite"
                        btn_camp.color = (150, 200, 150)
                btn_camp.draw(screen)
                
                if player.in_tribe:
                    if player.is_chief:
                        btn_tribe.text = "👑 Eres el Jefe"
                        btn_tribe.color = (255, 235, 120)
                    else:
                        if player.tribe_rep >= 100:
                            btn_tribe.text = "Retar al Alpha"
                            btn_tribe.color = (200, 100, 100)
                        else:
                            btn_tribe.text = f"Donar 5 Carne"
                            btn_tribe.color = (150, 150, 200)
                    btn_tribe.draw(screen)
                    
            elif game_state == "EQUIP":
                btn_eq_head.text = f"Cabeza: {player.equipment.get('Head') or 'Nada'}"
                btn_eq_body.text = f"Tórax: {player.equipment.get('Body') or 'Nada'}"
                btn_eq_weapon.text = f"Arma: {player.equipment.get('Weapon') or 'Puños'}"
                btn_eq_boots.text = f"Pies: {player.equipment.get('Boots') or 'Nada'}"
                
                btn_eq_head.draw(screen)
                btn_eq_body.draw(screen)
                btn_eq_weapon.draw(screen)
                btn_eq_boots.draw(screen)
                btn_eq_back.draw(screen)
                
            elif game_state == "ENCOUNTER":
                # Draw Enemy HP overlay
                en_hp_txt = font_main.render(f"PUNTOS DE VIDA RIVAL: {current_enemy.get('hp', 0)} HP", True, (250, 100, 100))
                screen.blit(en_hp_txt, (50, 420))
                
                btn_fight_atk.draw(screen)
                btn_fight_def.draw(screen)
                btn_flee.draw(screen)
                
            elif game_state == "CRAFTING":
                # Resaltar items seleccionados flotando un string?
                sel_str = " + ".join(crafting_selected) if crafting_selected else "Nada"
                sel_surf = font_main.render(f"En las manos: {sel_str}", True, (250, 200, 100))
                screen.blit(sel_surf, (50, 480))
                
                btn_craft_mix.draw(screen)
                btn_craft_cancel.draw(screen)
                
            elif game_state == "DECISION":
                btn_travel.draw(screen)
                btn_ignore.draw(screen)
                
            elif game_state == "OPPORTUNITY":
                btn_opp_take.draw(screen)
                btn_ignore.draw(screen)
                
            elif game_state == "PANTHEON":
                pant_surf = font_title.render("PANTEÓN DE LA DINASTÍA", True, (250, 200, 100))
                pts_surf = font_title.render(f"Puntos Ancestrales (PA) Ganados: {pantheon_data['puntos']}", True, (200, 220, 200))
                screen.blit(pant_surf, (220, 50))
                screen.blit(pts_surf, (150, 150))
                
                # Check button states
                if "METABOLISMO" in pantheon_data["perks"]: btn_perk_meta.text = "MUTAR: Súper Metabolismo [ADQUIRIDO]"
                else: btn_perk_meta.text = "MUTAR: Súper Metabolismo (+40 Max Hambre/Sed) [Coste: 30 PA]"
                
                if "PIEL_GRUESA" in pantheon_data["perks"]: btn_perk_skin.text = "MUTAR: Piel Rinoceronte [ADQUIRIDA]"
                else: btn_perk_skin.text = "MUTAR: Piel Rinoceronte (+5 Defensa Perpetua) [Coste: 50 PA]"
                
                if "BRAZOS_GORILA" in pantheon_data["perks"]: btn_perk_dmg.text = "MUTAR: Brazos de Gorila [ADQUIRIDA]"
                else: btn_perk_dmg.text = "MUTAR: Brazos de Gorila (+3 Daño Base Perpetuo) [Coste: 60 PA]"

                if "OJOS_BUHO" in pantheon_data["perks"]: btn_perk_eff.text = "MUTAR: Ojos de Búho [ADQUIRIDA]"
                else: btn_perk_eff.text = "MUTAR: Ojos de Búho (Menos cansancio/Más suerte explorando) [Coste: 45 PA]"

                if "ANTICUERPOS" in pantheon_data["perks"]: btn_perk_res.text = "MUTAR: Anticuerpos [ADQUIRIDA]"
                else: btn_perk_res.text = "MUTAR: Anticuerpos (Inmunidad Intestinal) [Coste: 80 PA]"
                
                btn_perk_meta.draw(screen)
                btn_perk_skin.draw(screen)
                btn_perk_dmg.draw(screen)
                btn_perk_eff.draw(screen)
                btn_perk_res.draw(screen)
                btn_reincarnate.draw(screen)
                
        else:
            if game_state == "MAP" or game_state == "ENCOUNTER" or game_state == "DECISION":
                game_over_surf = font_title.render("ESTÁS MUERTO", True, (200, 60, 60))
                cause_surf = font_main.render(f"Causa de muerte: {player.cause_of_death}", True, TEXT_COLOR)
                screen.blit(game_over_surf, (50, 430))
                screen.blit(cause_surf, (50, 470))
                btn_restart.draw(screen)
            elif game_state == "PANTHEON":
                # Draw pantheon since player is technically dead
                pant_surf = font_title.render("PANTEÓN DE LA DINASTÍA", True, (250, 200, 100))
                pts_surf = font_title.render(f"Puntos Ancestrales (PA) Ganados: {pantheon_data['puntos']}", True, (200, 220, 200))
                screen.blit(pant_surf, (220, 50))
                screen.blit(pts_surf, (150, 150))
                
                # Check button states
                if "METABOLISMO" in pantheon_data["perks"]: btn_perk_meta.text = "MUTAR: Súper Metabolismo [ADQUIRIDO]"
                else: btn_perk_meta.text = "MUTAR: Súper Metabolismo (+40 Max Hambre/Sed) [Coste: 30 PA]"
                
                if "PIEL_GRUESA" in pantheon_data["perks"]: btn_perk_skin.text = "MUTAR: Piel Rinoceronte [ADQUIRIDA]"
                else: btn_perk_skin.text = "MUTAR: Piel Rinoceronte (+5 Defensa Perpetua) [Coste: 50 PA]"
                
                if "BRAZOS_GORILA" in pantheon_data["perks"]: btn_perk_dmg.text = "MUTAR: Brazos de Gorila [ADQUIRIDA]"
                else: btn_perk_dmg.text = "MUTAR: Brazos de Gorila (+3 Daño Base Perpetuo) [Coste: 60 PA]"

                if "OJOS_BUHO" in pantheon_data["perks"]: btn_perk_eff.text = "MUTAR: Ojos de Búho [ADQUIRIDA]"
                else: btn_perk_eff.text = "MUTAR: Ojos de Búho (Menos cansancio/Más suerte explorando) [Coste: 45 PA]"

                if "ANTICUERPOS" in pantheon_data["perks"]: btn_perk_res.text = "MUTAR: Anticuerpos [ADQUIRIDA]"
                else: btn_perk_res.text = "MUTAR: Anticuerpos (Inmunidad Intestinal) [Coste: 80 PA]"
                
                btn_perk_meta.draw(screen)
                btn_perk_skin.draw(screen)
                btn_perk_dmg.draw(screen)
                btn_perk_eff.draw(screen)
                btn_perk_res.draw(screen)
                btn_reincarnate.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
