import pygame
import sys
import random
import os
from core.player import Player
from core.ui import Button, draw_bar, draw_text_box, draw_inventory, draw_minimap, draw_character_profile, draw_hallucinations
from core.world import World

# Colores estéticos limpios/minimalistas
BG_COLOR = (245, 245, 240)  # Tono hueso / libreta clara
TEXT_COLOR = (25, 30, 45) # Carbon/Marino muy oscuro (Realista)
BTN_COLOR = (240, 235, 230)
BTN_HOVER = (200, 200, 195)

BAR_COLORS = {
    "hp": (200, 50, 50),
    "hunger": (200, 150, 50),
    "thirst": (50, 150, 200),
    "energy": (100, 100, 100),
    "sanity": (180, 100, 200)
}

def get_next_equip(current, possible, inv):
    available = [i for i in possible if inv.get(i, 0) > 0]
    available.insert(0, None)
    try:
        idx = available.index(current)
        return available[(idx + 1) % len(available)]
    except ValueError:
        return available[0]

def save_game(player, world):
    import json
    data = {
        "player": player.to_dict(),
        "world": world.to_dict()
    }
    with open("current_run.json", "w") as f:
        json.dump(data, f)

def load_game():
    import json
    import os
    if os.path.exists("current_run.json"):
        try:
            with open("current_run.json", "r") as f:
                return json.load(f)
        except: return None
    return None

class WeatherParticle:
    def __init__(self, screen_width, screen_height, weather_type):
        self.sw = screen_width
        self.sh = screen_height
        self.type = weather_type
        self.reset()
        
    def reset(self):
        self.x = random.randint(0, self.sw)
        self.y = random.randint(-self.sh, 0)
        if self.type == "Lluvia Torrencial":
            self.vy = random.randint(10, 15)
            self.vx = -2
            self.color = (100, 100, 255, 150)
            self.length = random.randint(10, 20)
        elif self.type == "Ventisca de Nieve" or self.type == "Tormenta Polar" or self.type == "Ventisca de Hielo":
            self.vy = random.randint(2, 5)
            self.vx = random.randint(1, 3)
            self.color = (255, 255, 255, 200)
            self.length = random.randint(2, 4)
        elif self.type == "Tormenta de Arena" or self.type == "Lluvia de Ceniza":
            self.vy = random.randint(1, 3)
            self.vx = random.randint(5, 10)
            self.color = (200, 150, 100, 100) if "Arena" in self.type else (100, 100, 100, 150)
            self.length = random.randint(15, 30)
        else:
            self.vy = 5
            self.vx = 0
            self.color = (200, 200, 200, 50)
            self.length = 5

    def update(self):
        self.y += self.vy
        self.x += self.vx
        if self.y > self.sh or self.x > self.sw or self.x < 0:
            self.reset()

    def draw(self, surface):
        if self.type == "Lluvia Torrencial":
            pygame.draw.line(surface, self.color, (self.x, self.y), (self.x + self.vx, self.y + self.length), 1)
        elif "Ventisca" in self.type or "Polar" in self.type:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.length // 2)
        else:
            pygame.draw.line(surface, self.color, (self.x, self.y), (self.x + self.length, self.y + self.vy), 1)

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
    
    # Check for saved run
    save_data = load_game()
    if save_data:
        # Prompt logic would be nice, but for now we just auto-load if it exists
        # In a real game we would have a Menu state
        player.from_dict(save_data["player"])
        world.from_dict(save_data["world"])

    game_state = "MAP"
    current_message = f"Te encuentras en el bioma: {world.current_biome}."
    current_enemy = None

    # Instanciacion de botones Map (Botones más anchos para evitar desbordamiento)
    btn_search = Button(110, 555, 230, 50, "Buscar / Explorar", font_main, BTN_COLOR, TEXT_COLOR, BTN_HOVER)
    btn_rest = Button(350, 555, 230, 50, "Descansar", font_main, BTN_COLOR, TEXT_COLOR, BTN_HOVER)
    btn_craft = Button(600, 555, 120, 50, "Crafteo", font_main, (210, 230, 210), TEXT_COLOR, (190, 210, 190))
    
    btn_equip = Button(110, 615, 230, 50, "🎒 Equipo", font_main, (200, 220, 240), TEXT_COLOR, (180, 200, 220))
    btn_camp = Button(350, 615, 230, 50, "⛺ Campamento", font_main, (240, 230, 180), TEXT_COLOR, (220, 210, 160))
    
    btn_craft_mix = Button(570, 555, 120, 50, "Mezclar", font_small, (200, 150, 150), TEXT_COLOR, (180, 130, 130))
    btn_craft_cancel = Button(570, 615, 120, 50, "Salir", font_small, (150, 150, 150), TEXT_COLOR, (130, 130, 130))

    btn_fight_atk = Button(110, 555, 230, 50, "Atacar", font_main, (210, 100, 100), TEXT_COLOR, (190, 80, 80))
    btn_shoot = Button(350, 555, 230, 50, "Arco", font_main, (140, 180, 140), TEXT_COLOR, (120, 160, 120))
    btn_fight_def = Button(570, 555, 120, 50, "Cubrir", font_main, (140, 160, 220), TEXT_COLOR, (120, 140, 200))
    btn_flee = Button(110, 615, 230, 50, "Huir", font_main, (180, 180, 150), TEXT_COLOR, (160, 160, 130))

    btn_travel = Button(50, 555, 330, 50, "Avanzar a la Zona", font_main, (160, 200, 160), TEXT_COLOR, (140, 180, 140))
    btn_ignore = Button(400, 555, 330, 50, "Ignorar / Seguir", font_main, (200, 180, 160), TEXT_COLOR, (180, 160, 140))
    btn_tribe = Button(180, 480, 160, 25, "Tribu", font_small, (150, 150, 200), TEXT_COLOR, (130, 130, 180))
    btn_honey = Button(350, 370, 190, 25, "Comer Miel", font_small, (255, 220, 100), TEXT_COLOR, (230, 200, 80))
    btn_trap_fosa = Button(50, 310, 160, 25, "Trampa Fosa", font_small, (140, 100, 80), TEXT_COLOR, (120, 80, 60))
    btn_trap_nasa = Button(220, 310, 160, 25, "Nasa Pesca", font_small, (80, 140, 180), TEXT_COLOR, (60, 120, 160))
    btn_harvest_trap = Button(50, 310, 330, 25, "📥 Recoger Trampa", font_small, (100, 200, 100), TEXT_COLOR, (80, 180, 80))
    
    btn_meditate = Button(50, 340, 160, 25, "🧘 Ritual Base", font_small, (200, 200, 250), TEXT_COLOR, (180, 180, 230))
    btn_offer_wolf = Button(220, 340, 160, 25, "🐺 Rit. Lobo", font_small, (130, 200, 130), TEXT_COLOR, (110, 180, 110))
    btn_offer_buffalo = Button(390, 340, 160, 25, "🐂 Rit. Búfalo", font_small, (200, 180, 150), TEXT_COLOR, (180, 160, 130))

    btn_opp_take = Button(50, 555, 330, 50, "Aprovechar (-Ene)", font_main, (210, 200, 120), TEXT_COLOR, (190, 180, 100))
    
    btn_tame = Button(50, 615, 220, 50, "🐾 Domesticar", font_main, (180, 240, 180), TEXT_COLOR, (160, 220, 160))
    btn_plant = Button(50, 500, 220, 40, "🌱 Plantar Huerto", font_small, (180, 220, 180), TEXT_COLOR, (160, 200, 160))
    btn_harvest = Button(280, 500, 220, 40, "🧺 Cosechar", font_small, (220, 220, 150), TEXT_COLOR, (200, 200, 130))
    
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
        "Weapon": ["Cuchillo Óseo", "Cuchillo de Pedernal", "Hacha Primitiva", "Pico de Hueso", "Lanza Caza", "Lanza de Obsidiana", "Lanza de Piedra"],
        "Boots": ["Botas de Piel"]
    }
    
    pending_landmark = ""
    pending_biome = None
    pending_opp = None
    pantheon_data = {"puntos": 0, "perks": [], "generation": 1, "ancestral_art": []}
    
    blood_intensity = 0
    screen_shake = 0
    shake_offset_x = 0
    shake_offset_y = 0
    
    crafting_selected = []
    inv_slots = []
    
    weather_timer = 0
    weather_active = None
    weather_warning = False
    weather_pending_type = None
    weather_pending_time = 0
    
    floating_texts = []
    particles = []
    weather_particles = []
    
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
                        # Avance procedural orgánico en vez de tecla WASD
                        choices = [(0,-1), (0,1), (-1,0), (1,0)]
                        dx, dy = random.choice(choices)
                        nx = max(0, min(world.grid_size-1, world.player_x + dx))
                        ny = max(0, min(world.grid_size-1, world.player_y + dy))
                        world.player_x, world.player_y = nx, ny
                        cell = world.grid[world.player_y][world.player_x]
                        
                        cell["searched"] = True
                        pas_msg = player.search()
                        if cell["type"] == "Agua": player.consume_energy(4) # extra penalidad
                        
                        if cell["special"] == "Mineral": evt = {"type": "mineral", "data": {"name": "Yacimiento expuesto", "tool_req": "Pico de Hueso", "item": "Piedra", "amt": 5}}
                        elif cell["special"] == "Planta": evt = {"type": "resource", "data": {"name": "Flora expuesta", "amount": 20, "stat": "hunger", "item": "Fibra", "item_amt": 2, "herb": "Ajenjo", "herb_amt": 1}}
                        elif cell["special"] == "Enemigo Fuerte": evt = {"type": "enemy", "data": {"name": "Guardián de Zona", "dmg": 30, "hp": 55, "drops": {"Huesos": (1,2)}}}
                        else: evt = world.generate_search_event()
                        if evt["type"] == "nothing":
                            current_message = "Buscaste exhaustivamente pero no encontraste nada útil."
                        elif evt["type"] == "resource":
                            player.heal_stat(evt["data"]["stat"], evt["data"]["amount"])
                            floating_texts.append({"text": f"+{evt['data']['amount']}", "x": 500, "y": 300, "color": (100, 255, 100), "life": 60})
                            for _ in range(5): particles.append({"x": 500, "y": 450, "vx": random.uniform(-2,2), "vy": random.uniform(-4,-1), "color": (100, 255, 100), "life": 30})
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
                            current_enemy["max_hp"] = current_enemy["hp"]
                            player.arrows_fired = 0
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
                        if world.camp_level == 0:
                            player.sanity = max(0, player.sanity - 10) # Dormir mal baja sanidad
                        else:
                            player.sanity = min(player.max_sanity, player.sanity + 20) # Camping cura mente
                        
                        # Art Milestone: First Camp
                        if "fire" not in player.ancestral_art: player.ancestral_art.append("fire")
                            
                        turn_taken = True
                        if world.camp_level > 0:
                            if turn_taken:
                                save_game(player, world)
                                world.update_traps()
                            current_message = f"Descansas profundamente en tu Campamento Lvl {world.camp_level}. ¡Partida Guardada!"
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
                                player.add_chronicle("Al fin, el secreto del fuego es mío. La piedra se rinde al calor.")
                                if "hand" not in player.ancestral_art: player.ancestral_art.append("hand")
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
                            
                    if player.inventory.get("Miel", 0) > 0:
                        if btn_honey.handle_event(event):
                            player.inventory["Miel"] -= 1
                            player.heal_stat("hunger", 20)
                            player.heal_stat("thirst", 10)
                            player.sanity = min(player.max_sanity, player.sanity + 15)
                            current_message = f"Dulzura nutritiva: +20H +10S +15Sanidad. (Miel restante: {player.inventory.get('Miel', 0)})"
                            turn_taken = True
                            
                elif game_state == "ENCOUNTER":
                    if btn_fight_atk.handle_event(event):
                        en_name = current_enemy["name"]
                        # Tu turno
                        current_enemy["hp"] -= player.base_dmg
                        screen_shake = 5
                        floating_texts.append({"text": f"-{player.base_dmg}", "x": 600, "y": 200, "color": (200, 50, 50), "life": 40})
                        for _ in range(8): particles.append({"x": 600, "y": 200, "vx": random.uniform(-4, 4), "vy": random.uniform(-4, 4), "color": (200, 50, 50), "life": 30})
                        
                        if current_enemy["hp"] <= 0:
                            # Finalizacion de combate Melee
                            if en_name == "Jefe Tribal Alpha":
                                player.is_chief = True
                                player.evolution_stage = "Supremo Tribal"
                                if "Jefe Tribal" not in player.trophies: player.trophies.append("Jefe Tribal")
                                if "chief" not in player.ancestral_art: player.ancestral_art.append("chief")
                                player.discover("Espiritualidad")
                                player.add_chronicle("El Jefe ha caído. Ahora el clan escucha mis susurros.")
                                current_message = "¡LO CORTASTE AL EJE! La tribu te jura lealtad. Eres Jefe."
                            else:
                                if en_name not in player.trophies and en_name in ["Lobo", "Jaguar", "Sabertooth", "Búfalo Solitario", "Mamut", "Oso"]:
                                    player.trophies.append(en_name)
                                    
                                dropped = []
                                for i_name, (min_amt, max_amt) in current_enemy.get("drops", {}).items():
                                    amt = random.randint(min_amt, max_amt)
                                    if amt > 0:
                                        player.add_to_inventory(i_name, amt)
                                        dropped.append(f"{amt}x {i_name}")
                                player.heal_stat("hunger", 15)
                                
                                # Recuperacion de Flechas RNG (aunque sea melee, pudiste disparar antes)
                                recov = 0
                                for _ in range(player.arrows_fired):
                                    if random.random() < 0.5: recov += 1
                                if recov > 0:
                                    player.inventory["Flechas"] = player.inventory.get("Flechas", 0) + recov
                                    dropped.append(f"{recov}x Flechas (Rescatadas)")
                                
                                current_message = f"¡Masacraste al {en_name}! Ganaste: {', '.join(dropped)}"
                            game_state = "MAP"
                        else:
                            # Turno enemigo (Contraataque Melee)
                            recibido = player.take_enemy_hit(en_name, current_enemy["dmg"], 1.0)
                            if recibido > 15: blood_intensity = min(100, blood_intensity + recibido)
                            if recibido > 0:
                                screen_shake = 10
                                floating_texts.append({"text": f"-{recibido}", "x": 500, "y": 300, "color": (250, 0, 0), "life": 50})
                                for _ in range(12): particles.append({"x": 500, "y": 300, "vx": random.uniform(-5, 5), "vy": random.uniform(-5, 5), "color": (250, 0, 0), "life": 40})
                            if player.alive:
                                current_message = f"Hiciste {player.base_dmg} de daño. ¡El {en_name} sangra pero sobrevive! Te embiste por {recibido} de daño."
                            
                    if player.inventory.get("Arco Primitivo", 0) > 0 and player.inventory.get("Flechas", 0) > 0:
                        if btn_shoot.handle_event(event):
                            en_name = current_enemy["name"]
                            dmg = int(player.base_dmg * 1.5)
                            current_enemy["hp"] -= dmg
                            player.inventory["Flechas"] -= 1
                            player.arrows_fired += 1
                            screen_shake = 5
                            floating_texts.append({"text": f"-{dmg}", "x": 600, "y": 200, "color": (150, 200, 150), "life": 40})
                            for _ in range(5): particles.append({"x": 600, "y": 200, "vx": random.uniform(3, 8), "vy": random.uniform(-2, 2), "color": (150, 200, 150), "life": 30})
                            
                            if current_enemy["hp"] <= 0:
                                # Finalizacion de combate Rango
                                if en_name not in player.trophies and en_name in ["Lobo", "Jaguar", "Sabertooth", "Búfalo Solitario", "Mamut", "Oso"]:
                                    player.trophies.append(en_name)
                                    
                                dropped = []
                                for i_name, (min_amt, max_amt) in current_enemy.get("drops", {}).items():
                                    amt = random.randint(min_amt, max_amt)
                                    if amt > 0:
                                        player.add_to_inventory(i_name, amt)
                                        dropped.append(f"{amt}x {i_name}")
                                player.heal_stat("hunger", 15)
                                
                                recov = 0
                                for _ in range(player.arrows_fired):
                                    if random.random() < 0.5: recov += 1
                                if recov > 0:
                                    player.inventory["Flechas"] = player.inventory.get("Flechas", 0) + recov
                                    dropped.append(f"{recov}x Flechas (Rescatadas)")
                                    
                                current_message = f"¡Abatiste al {en_name} desde lejos! Ganaste: {', '.join(dropped)}"
                                game_state = "MAP"
                            else:
                                # Turno enemigo (Contraataque Rango - menos daño al estar lejos)
                                recibido = player.take_enemy_hit(en_name, current_enemy["dmg"], 0.8)
                                if player.alive:
                                    current_message = f"Disparaste una flecha al {en_name} por {dmg}. ¡Se acerca furioso y te golpea por {recibido}!"
                                
                    if player.inventory.get("Correa de Cuero", 0) > 0 and current_enemy["hp"] < current_enemy.get("max_hp", 100) * 0.4:
                        if btn_tame.handle_event(event):
                            en_name = current_enemy["name"]
                            tamables = ["Perro Salvaje", "Lobo", "Zorro", "Lince", "Búfalo Solitario"]
                            if en_name in tamables:
                                player.inventory["Correa de Cuero"] -= 1
                                player.follower = {"species": en_name}
                                current_message = f"¡HAS DOMESTICADO AL {en_name.upper()}! Ahora te sigue fielmente."
                                game_state = "MAP"
                            else:
                                current_message = f"El {en_name} es demasiado salvaje para ser domesticado."
                                
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
                            world.generate_grid_for_biome(pending_biome)
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
                        elif pending_opp.get("special") == "FOLLOWER_CHANCE":
                            if player.inventory.get("Carne Asada", 0) >= 1:
                                player.inventory["Carne Asada"] -= 1
                                if random.random() < 0.7:
                                    player.follower = {"species": "Cazador Leal", "bonus_type": "DMG", "bonus_val": 10}
                                    current_message = "¡El cazador se recupera y decide seguirte para pagar su deuda!"
                                else:
                                    current_message = "El cazador te agradece y se aleja cojeando hacia el horizonte."
                            else:
                                current_message = "No tienes comida para ayudarlo... lo dejas a su suerte."
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
                                
                    if btn_craft_cancel.handle_event(event):
                        current_message = "Adversión retractada. Vuelves al mapa."
                        game_state = "MAP"
                        crafting_selected = []
                    
                    if btn_craft_mix.handle_event(event):
                        if not crafting_selected:
                            current_message = "No has seleccionado materiales."
                        else:
                            # Intentar crafteo manual por combinación
                            res = player.manual_craft(crafting_selected)
                            current_message = res
                            if "EXITOSO" in res:
                                turn_taken = True
                                game_state = "MAP"
                                crafting_selected = []
                            # Chequeo de descubrimiento por combinacion
                            if "Milenrama" in crafting_selected and "Agua" in crafting_selected:
                                if player.discover("Curación"):
                                    current_message += "\n¡HITO! Has descubierto los principios de la Medicina Ancestral."
                        
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
                        old_art = player.ancestral_art[:] # Mantener arte ancestral
                        player = Player()
                        player.ancestral_art = old_art
                        world = World()
                        game_state = "MAP"
                        current_message = f"Has reencarnado (Generación {player.generation}). Un nuevo comienzo con el legado de tus ancestros..."
                        

        if turn_taken and player.alive and game_state == "MAP":
            w_msg = ""
            if player.turn % 2 == 0:
                world.update_traps()
                world.update_world_events()
            
            # Chronicle de Supervivencia
            if player.turn % 20 == 0:
                entries = [
                    "El hambre es un lobo que nunca duerme.",
                    "He visto estrellas caer sobre la montaña.",
                    "El tiempo corre como el agua entre mis manos.",
                    "Mis manos están endurecidas por la roca."
                ]
                player.add_chronicle(random.choice(entries))
                
            blood_intensity = max(0, blood_intensity - 5)
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
                    weather_particles = []
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
                        
                        # Init particles for the new weather
                        weather_particles = [WeatherParticle(screen_width, screen_height, weather_pending_type) for _ in range(100)]
            
            # Crecimiento de Huertos
            for row in world.grid:
                for cell in row:
                    if cell.get("has_plot"):
                        cell["plot_growth"] = min(100, cell["plot_growth"] + 10)
                        
            # Produccion de Seguidores (Buffalo/Vaca)
            if player.follower and player.follower["species"] == "Búfalo Solitario":
                player.follower_timer += 1
                if player.follower_timer >= 10:
                    player.follower_timer = 0
                    player.add_to_inventory("Carne Asada", 1)
                    w_msg += "\n[Tu Búfalo encontró algo de sustento para ti: +1 Carne Asada]"
            
            sick_msg = player.check_disease_damage()
            if sick_msg:
                w_msg += f"\n{sick_msg}"
                
            current_message += w_msg

        # Renderizado de Paisaje con Game Juice Screen Shake
        if screen_shake > 0:
            shake_offset_x = random.randint(-5, 5)
            shake_offset_y = random.randint(-5, 5)
            screen_shake -= 1
        else:
            shake_offset_x, shake_offset_y = 0, 0
            
        # Update weather
        for p in weather_particles:
            p.update()

        from core.ui import draw_notebook_bg, draw_ink_splotches, draw_time_icon, draw_trophy_sketches, draw_ritual_smoke
        time_now = player.get_time_of_day()
        draw_notebook_bg(screen, time_now, player.ancestral_art, blood_intensity, player.turn, weather_active, player.chronic_entries, font_small)
        # Capas de Humo Ritual si hay buffs activos
        if player.active_buffs:
            draw_ritual_smoke(screen, player.turn)
            
        draw_ink_splotches(screen, player.turn + player.generation)
        draw_trophy_sketches(screen, player.trophies)
        draw_hallucinations(screen, player.sanity, player.turn)
        draw_character_profile(screen, player, 780, 40)
        
        draw_time_icon(screen, 120, 20, time_now, font_main)
        
        # Stats Sidebar (Reposicionados para mayor claridad)
        stats_x = 750
        draw_bar(screen, stats_x, 250, 220, 15, player.hp, player.max_hp, BAR_COLORS["hp"], "Vida", font_small)
            
        # Draw Active Buffs
        bx, by = 750, 200
        for b in player.active_buffs:
            b_txt = font_small.render(f"✨ {b['name']}: {b['timer']}t", True, (100, 255, 150))
            screen.blit(b_txt, (bx, by))
            by += 20
        
        # Superposición de la matriz minimapa (Reposicionado para que no choque con HUD)
        if game_state in ["MAP", "ENCOUNTER", "DECISION", "OPPORTUNITY"]:
            draw_minimap(screen, world, player, font_main, font_small, 110 + shake_offset_x, 210 + shake_offset_y, 200)

        def take_enemy_hit(self, enemy_name, dmg_raw, multiplier=1.0):
            # Wrapper local para main para trigger de sangre visual
            nonlocal blood_intensity
            recibido = player.take_enemy_hit(enemy_name, dmg_raw, multiplier)
            if recibido > 15: blood_intensity = min(100, blood_intensity + recibido)
            return recibido

        # Renderizado de Textos Principales y Localizacion
        # HUD de Supervivencia y Era (Espaciado uniformemente)
        hud_x = 120
        title_surf = font_title.render(f"{player.evolution_stage} [ERA {world.era}]", True, TEXT_COLOR)
        gen_surf = font_main.render(f"Generación {player.generation}", True, TEXT_COLOR)
        camp_txt = "⛺ (Seguro)" if world.has_camp else "(A la intemperie)"
        loc_surf = font_main.render(f"Zona: {world.current_location} {camp_txt}", True, (50, 120, 160) if world.has_camp else TEXT_COLOR)
        turn_surf = font_main.render(f"Supervivencia: {player.turn} Días", True, TEXT_COLOR)
        disc_surf = font_main.render(f"Descubrimiento: {len(player.discovered_concepts) * 10} PA", True, (160, 140, 40))
        
        screen.blit(title_surf, (hud_x, 35))
        screen.blit(gen_surf, (hud_x, 65))
        screen.blit(loc_surf, (hud_x, 90))
        screen.blit(turn_surf, (hud_x, 115))
        screen.blit(disc_surf, (hud_x, 140))

        # El dibujo central del jugador ahora es manejado por draw_character_profile (llamado arriba)
        # pero podemos dejar una version "sketchy" central si el usuario prefiere
        pass
        
        # Render Seguidores Visual
        if player.follower:
            f_color = (100, 100, 110)
            fx, fy = 780, 200
            pygame.draw.circle(screen, f_color, (fx, fy), 10, width=1) # Cabeza mascota
            pygame.draw.line(screen, f_color, (fx, fy+10), (fx-10, fy+25), 1) 
            pygame.draw.line(screen, f_color, (fx, fy+10), (fx+10, fy+25), 1)
            f_name = font_small.render(f"🐾 {player.follower['species']}", True, f_color)
            screen.blit(f_name, (fx + 20, fy - 10))
        
        # Eliminamos el dibujo central redundante para limpiar la 'página'
        pass

        # Renderizado de Estadísticas Sidebar Mid (Uniforme)
        stats_x = 750
        # No repetimos HP porque se llamó arriba, pero ajustamos el resto
        draw_bar(screen, stats_x, 290, 220, 15, player.hunger, player.max_hunger, BAR_COLORS["hunger"], "Hambre", font_small)
        draw_bar(screen, stats_x, 330, 220, 15, player.thirst, player.max_thirst, BAR_COLORS["thirst"], "Sed", font_small)
        draw_bar(screen, stats_x, 370, 220, 15, player.energy, player.max_energy, BAR_COLORS["energy"], "Energía", font_small)
        
        # UI Sanity Dinámica
        if player.era > 1 or player.sanity < 95:
            draw_bar(screen, stats_x, 410, 220, 15, player.sanity, player.max_sanity, BAR_COLORS["sanity"], "Mente", font_small)
            
        # Draw weather particles (overlay)
        for p in weather_particles:
            p.draw(screen)

        # Update one-off particles
        for p in particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 1
            if p["life"] <= 0:
                particles.remove(p)
            else:
                pygame.draw.circle(screen, p["color"], (int(p["x"]), int(p["y"])), 3)

        # Renderizado interactivo y sub-paneles Sidebar Bottom
        inv_slots = draw_inventory(screen, 740, 430, 240, 250, player.inventory, font_small, font_main)

        # Etiqueta visual para climas/estados especiales
        if weather_active:
            weather_surf = font_main.render(f"CLIMA ACTIVO: {weather_active}", True, (200, 100, 100))
            screen.blit(weather_surf, (30, 310))
        if player.sickness:
            sick_surf = font_small.render(f"Pestes: {', '.join(player.sickness)}", True, (150, 60, 180))
            screen.blit(sick_surf, (50, 400))

        if player.alive:
            draw_text_box(screen, current_message, 100, 430, 630, 120, font_small)
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
                        
                cell = world.grid[world.player_y][world.player_x]
                
                # Narrative Fluff basado en Bioma
                if turn_taken:
                    fluff = ""
                    if cell["type"] == "Agua": fluff = "\nEl agua murmura historias antiguas a tus pies..."
                    elif cell["type"] == "Bosque": fluff = "\nLas sombras de los árboles parecen vigilarte."
                    elif world.current_biome == "Tundra": fluff = "\nEl viento corta como un cuchillo de obsidiana el aire gélido."
                    current_message += fluff

                # Gestión de Rituales en Campamento
                if world.has_camp:
                    btn_meditate.draw(screen)
                    if btn_meditate.handle_event(event):
                        player.sanity = min(player.max_sanity, player.sanity + 25)
                        current_message = "Meditas frente al fuego. Tu mente se aclara. (+25 Sanidad)"
                        # Art Milestone: Meditation
                        if "fire" not in player.ancestral_art: player.ancestral_art.append("fire")
                        turn_taken = True
                    
                    if player.inventory.get("Ofrenda de Lobo", 0) > 0:
                        btn_offer_wolf.draw(screen)
                        if btn_offer_wolf.handle_event(event):
                            player.inventory["Ofrenda de Lobo"] -= 1
                            player.active_buffs.append({"name": "Lobo", "val": 8, "timer": 8})
                            current_message = "Ritual del Lobo completado. Tu danza infunde ferocidad. (+8 Daño, 8 Turnos)"
                            turn_taken = True
                    
                    if player.inventory.get("Ofrenda de Búfalo", 0) > 0:
                        btn_offer_buffalo.draw(screen)
                        if btn_offer_buffalo.handle_event(event):
                            player.inventory["Ofrenda de Búfalo"] -= 1
                            player.active_buffs.append({"name": "Búfalo", "val": 15, "timer": 10})
                            current_message = "Ritual del Búfalo completado. Piel curtida y voluntad de acero. (+15 Defensa, 10 Turnos)"
                            turn_taken = True
                # Gestión de Trampas
                if cell.get("trap") and cell.get("trap_loot"):
                    btn_harvest_trap.draw(screen)
                    if btn_harvest_trap.handle_event(event):
                        player.add_to_inventory(cell["trap_loot"], 1)
                        current_message = f"¡Trampa activada! Obtuviste: {cell['trap_loot']}. La trampa se ha roto."
                        cell["trap"] = None
                        cell["trap_loot"] = None
                        cell["trap_turns"] = 0
                elif not cell.get("trap") and not cell.get("has_camp"):
                    if player.inventory.get("Trampa de Fosa", 0) > 0 and cell["type"] != "Agua":
                        btn_trap_fosa.draw(screen)
                        if btn_trap_fosa.handle_event(event):
                            player.inventory["Trampa de Fosa"] -= 1
                            cell["trap"] = "Fosa"
                            current_message = "Has excavado una fosa y la has cubierto de hojas."
                    if player.inventory.get("Nasa de Pesca", 0) > 0 and cell["type"] == "Agua":
                        btn_trap_nasa.draw(screen)
                        if btn_trap_nasa.handle_event(event):
                            player.inventory["Nasa de Pesca"] -= 1
                            cell["trap"] = "Nasa"
                            current_message = "Has colocado la nasa de pesca sumergida entre juncos."

                if not cell["has_plot"] and world.has_camp and player.inventory.get("Huerto de Piedra", 0) > 0:
                    btn_plant.draw(screen)
                    if btn_plant.handle_event(event):
                        player.inventory["Huerto de Piedra"] -= 1
                        cell["has_plot"] = True
                        cell["plot_growth"] = 0
                        current_message = "Has preparado la tierra y rodeado el área con piedras. El cultivo ha comenzado."
                
                if cell["has_plot"] and cell["plot_growth"] >= 100:
                    btn_harvest.draw(screen)
                    if btn_harvest.handle_event(event):
                        cell["plot_growth"] = 0
                        yield_amt = random.randint(3, 8)
                        player.add_to_inventory("Carne Asada", yield_amt // 2) # Representa vegetales nutritivos
                        player.add_to_inventory("Fibra", yield_amt)
                        current_message = f"¡Cosecha exitosa! Obtuviste nutrientes y fibras del huerto."
                        # Particulas de cosecha
                        for _ in range(15): particles.append({"x": 400, "y": 430, "vx": random.uniform(-3,3), "vy": random.uniform(-6,-2), "color": (100, 200, 100), "life": 40})
                    
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
                en_hp_txt = font_main.render(f"VIDA RIVAL: {current_enemy.get('hp', 0)} / {current_enemy.get('max_hp', 100)}", True, (150, 50, 50))
                screen.blit(en_hp_txt, (50, 420))
                
                btn_fight_atk.draw(screen)
                if player.inventory.get("Arco Primitivo", 0) > 0 and player.inventory.get("Flechas", 0) > 0:
                    btn_shoot.draw(screen)
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

        # ACTUALIZACION Y DIBUJO DE GAME JUICE
        for ft in floating_texts[:]:
            ft["y"] -= 1.5
            ft["life"] -= 1
            if ft["life"] <= 0: floating_texts.remove(ft)
            else:
                alpha = min(255, max(0, ft["life"] * 5))
                f_surf = font_main.render(ft["text"], True, ft["color"])
                f_surf.set_alpha(alpha)
                screen.blit(f_surf, (ft["x"], ft["y"]))
                
        for pt in particles[:]:
            pt["x"] += pt["vx"]
            pt["y"] += pt["vy"]
            pt["vy"] += 0.2  # Gravedad
            pt["life"] -= 1
            if pt["life"] <= 0: particles.remove(pt)
            else:
                pygame.draw.circle(screen, pt["color"], (int(pt["x"]), int(pt["y"])), max(1, pt["life"]//10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
