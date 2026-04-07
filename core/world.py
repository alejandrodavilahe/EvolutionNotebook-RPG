import random

BIOMES = {
    "Selva Tropical": {"temp_mod": 10, "food_chance": 45, "water_chance": 35, "enemy_chance": 20, "landmark_chance": 12, "mineral_chance": 10},
    "Sabana": {"temp_mod": 15, "food_chance": 30, "water_chance": 15, "enemy_chance": 25, "landmark_chance": 12, "mineral_chance": 10},
    "Pradera": {"temp_mod": 5, "food_chance": 30, "water_chance": 20, "enemy_chance": 10, "landmark_chance": 12, "mineral_chance": 8},
    "Desierto": {"temp_mod": 30, "food_chance": 10, "water_chance": 5, "enemy_chance": 25, "landmark_chance": 15, "mineral_chance": 15},
    "Taiga": {"temp_mod": -10, "food_chance": 25, "water_chance": 20, "enemy_chance": 15, "landmark_chance": 12, "mineral_chance": 20},
    "Matorral": {"temp_mod": 15, "food_chance": 15, "water_chance": 10, "enemy_chance": 18, "landmark_chance": 12, "mineral_chance": 12},
    "Bosque Templado": {"temp_mod": 0, "food_chance": 30, "water_chance": 25, "enemy_chance": 12, "landmark_chance": 15, "mineral_chance": 15},
    "Tundra": {"temp_mod": -25, "food_chance": 5, "water_chance": 15, "enemy_chance": 20, "landmark_chance": 15, "mineral_chance": 15},
    "Pantano Manglar": {"temp_mod": 15, "food_chance": 20, "water_chance": 15, "enemy_chance": 30, "landmark_chance": 10, "mineral_chance": 15},
    "Erial Volcánico": {"temp_mod": 40, "food_chance": 2, "water_chance": 0, "enemy_chance": 35, "landmark_chance": 12, "mineral_chance": 43},
    "Picos Alpinos": {"temp_mod": -30, "food_chance": 5, "water_chance": 10, "enemy_chance": 20, "landmark_chance": 15, "mineral_chance": 20}
}

LANDMARKS = {
    "Selva Tropical": ["Cenote Antiguo", "Árbol Milenario", "Cascada de Selva", "Río Fangoso"],
    "Sabana": ["Baobab Gigante", "Arroyo Seco", "Llanura Alta", "Oasis Menor"],
    "Pradera": ["Lago Sereno", "Colina de Viento", "Madriguera Oculta", "Arroyo Abierto", "Círculo de Piedras Ancestrales"],
    "Desierto": ["Oasis Profundo", "Cañón Rocoso", "Cueva Lúgubre", "Mesa Elevada", "Esqueleto de Gigante"],
    "Taiga": ["Claro de Coníferas", "Lago de Taiga", "Cueva Rocosa", "Río Frío"],
    "Matorral": ["Barranco Espinoso", "Zarza Mayor", "Cueva Polvorienta", "Lecho de Roca"],
    "Bosque Templado": ["Arroyo Fresco", "Cueva del Oso", "Claro Iluminado", "Roble Anciano"],
    "Tundra": ["Cueva de Hielo", "Lago Congelado", "Refugio de Piedra", "Coto de Caza Polar"],
    "Pantano Manglar": ["Aguas Estancadas", "Árbol Podrido", "Cenagal", "Cabaña Abandonada"],
    "Erial Volcánico": ["Río de Lava", "Cráter Humeante", "Géiser", "Páramo de Ceniza"],
    "Picos Alpinos": ["Cima Nevada", "Borde de Acantilado", "Cueva Helada", "Nido de Cóndor"]
}

TRANSITION_PATHS = {
    "Selva Tropical": {"Subir a la Sabana": "Sabana"},
    "Sabana": {"Bajar a la Selva": "Selva Tropical", "Hacia la Pradera": "Pradera", "Buscar Dunas": "Desierto", "Adentrarse al Pantano": "Pantano Manglar"},
    "Pradera": {"Ir a la Sabana": "Sabana", "Adentrarse al Bosque Templado": "Bosque Templado", "Ir al Matorral": "Matorral"},
    "Desierto": {"Volver a la Sabana": "Sabana", "Subir al Matorral": "Matorral", "Caminar al Erial": "Erial Volcánico"},
    "Taiga": {"Avanzar a la Tundra": "Tundra", "Descender al Bosque Templado": "Bosque Templado", "Subir a los Picos": "Picos Alpinos"},
    "Matorral": {"Ir a Pradera": "Pradera", "Adentrarse al Desierto": "Desierto"},
    "Bosque Templado": {"Cruzar a la Pradera": "Pradera", "Subir a la Taiga": "Taiga"},
    "Tundra": {"Retroceder a la Taiga": "Taiga", "Subir a los Picos": "Picos Alpinos"},
    "Pantano Manglar": {"Salir a Sabana": "Sabana", "Ir a Bosque": "Bosque Templado"},
    "Erial Volcánico": {"Huir de vuelta al Desierto": "Desierto"},
    "Picos Alpinos": {"Bajar a la Taiga": "Taiga", "Bajar a la Tundra": "Tundra"}
}

OPPORTUNITIES = [
    {"name": "Restos Frescos", "desc": "Restos de una fiera (Carroña). ¿Tomar la valiosa carne cruda? (Riesgo asqueroso).", "cost": {"energy": 10}, "reward": {"Carne Cruda": (3, 6), "Huesos": (1, 3)}, "risk_disease": "Infección", "risk_chance": 0.20, "special": None},
    {"name": "Árbol Frutal Silvestre", "desc": "Gran árbol exótico. ¿saltar intensamente y recolectar?", "cost": {"energy": 15}, "reward": {}, "boost": {"hunger": 50, "thirst": 30}, "risk_disease": None, "risk_chance": 0, "special": None},
    {"name": "Humo en el Horizonte", "desc": "Ves a otros humanos rústicos... ¿Acercarte para unirte? (Riesgo 30%: Caníbales Emboscadores).", "cost": {"energy": 20}, "reward": {}, "risk_disease": None, "risk_chance": 0, "special": "TRIBU"},
    {"name": "Cazador Herido", "desc": "Un hombre gime en el suelo. ¿Ayudarlo con recursos? (Gasto: Carne Asada x1). Puede unirse a ti.", "cost": {"energy": 5}, "reward": {}, "special": "FOLLOWER_CHANCE"},
    {"name": "Ruinas de Campamento", "desc": "Un fuego apagado y pieles rotas. ¿Buscar restos entre las cenizas?", "cost": {"energy": 10}, "reward": {"Fibra": (2, 5), "Pedernal": (1, 3), "Piel": (0, 1)}, "special": None},
    {"name": "Colmena Silvestre", "desc": "Miel dorada gotea de un tronco ruidoso. ¿Intentar extraerla?", "cost": {"energy": 15}, "reward": {"Miel": (1, 2)}, "boost": {"hunger": 20, "thirst": 10}, "risk_disease": "Infección", "risk_chance": 0.15, "special": None}
]

PLANTS = {
    "Selva Tropical": ["Bejuco Guaco"],
    "Sabana": ["Eucalipto"],
    "Pradera": ["Caléndula", "Milenrama"],
    "Desierto": ["Ajenjo", "Cactus Curativo"],
    "Taiga": ["Musgo de Reno", "Raíz Fuerte"],
    "Matorral": ["Ajenjo", "Salvia"],
    "Bosque Templado": ["Milenrama", "Caléndula"],
    "Tundra": ["Líquen Ártico", "Musgo de Reno"],
    "Pantano Manglar": ["Loto de Agua", "Bejuco Venenoso"],
    "Erial Volcánico": ["Raíz Quemada"],
    "Picos Alpinos": ["Flor de Nieve"]
}

ENEMIES = {
    "Selva Tropical": [
        {"name": "Jaguar", "dmg": 25, "hp": 55, "drops": {"Carne Cruda": (10, 20), "Piel": (1, 2), "Colmillo": (1, 2)}},
        {"name": "Anaconda", "dmg": 18, "hp": 45, "drops": {"Carne Blanca": (5, 10), "Piel Escamosa": (1, 2)}},
        {"name": "Rana Dardo", "dmg": 5, "hp": 10, "drops": {"Veneno": (1, 2)}}
    ],
    "Sabana": [
        {"name": "León Salvaje", "dmg": 30, "hp": 65, "drops": {"Carne Cruda": (15, 25), "Piel": (1, 2), "Huesos": (1, 3)}},
        {"name": "Hiena Moteada", "dmg": 20, "hp": 35, "drops": {"Carne Dura": (5, 15), "Huesos": (1, 2)}},
        {"name": "Mamba Negra", "dmg": 15, "hp": 20, "drops": {"Veneno": (1, 2), "Piel Escamosa": (1, 1)}}
    ],
    "Pradera": [
        {"name": "Búfalo Solitario", "dmg": 35, "hp": 80, "drops": {"Carne Cruda": (25, 40), "Piel": (2, 3), "Cuerno": (1, 2)}},
        {"name": "Perro Salvaje", "dmg": 12, "hp": 25, "drops": {"Carne Dura": (5, 10), "Huesos": (1, 1)}},
        {"name": "Serpiente Cascabel", "dmg": 10, "hp": 15, "drops": {"Veneno": (1, 1), "Piel Escamosa": (1, 1)}}
    ],
    "Desierto": [
        {"name": "Escorpión Gigante", "dmg": 12, "hp": 20, "drops": {"Carne Blanca": (3, 8), "Caparazón": (1, 2), "Veneno": (0, 1)}},
        {"name": "Coyote", "dmg": 15, "hp": 25, "drops": {"Carne Cruda": (4, 10), "Piel": (1, 1), "Huesos": (1, 1)}},
        {"name": "Cobra Real", "dmg": 18, "hp": 25, "drops": {"Veneno": (1, 2), "Piel Escamosa": (1, 1)}}
    ],
    "Taiga": [
        {"name": "Alce Enojado", "dmg": 28, "hp": 75, "drops": {"Carne Cruda": (20, 35), "Piel": (2, 2), "Cuerno": (1, 2)}},
        {"name": "Lobo Gris", "dmg": 20, "hp": 30, "drops": {"Carne Cruda": (8, 15), "Piel": (1, 2), "Huesos": (1, 2)}},
        {"name": "Oso Pardo", "dmg": 35, "hp": 70, "drops": {"Carne Cruda": (15, 30), "Piel": (1, 2), "Grasa": (2, 3)}}
    ],
    "Matorral": [
        {"name": "Lince", "dmg": 18, "hp": 30, "drops": {"Carne Cruda": (5, 12), "Piel": (1, 2), "Huesos": (1, 1)}},
        {"name": "Jabalí Salvaje", "dmg": 25, "hp": 45, "drops": {"Carne Dura": (15, 25), "Piel": (1, 1), "Grasa": (1, 1)}},
        {"name": "Víbora", "dmg": 12, "hp": 15, "drops": {"Veneno": (1, 1), "Piel Escamosa": (1, 1)}}
    ],
    "Bosque Templado": [
        {"name": "Oso Negro", "dmg": 25, "hp": 60, "drops": {"Carne Cruda": (10, 20), "Piel": (1, 1), "Grasa": (1, 2)}},
        {"name": "Jabalí", "dmg": 20, "hp": 40, "drops": {"Carne Dura": (10, 20), "Piel": (1, 2), "Huesos": (1, 2)}},
        {"name": "Lobo Solitario", "dmg": 18, "hp": 30, "drops": {"Carne Cruda": (5, 10), "Piel": (1, 2), "Huesos": (1, 2)}}
    ],
    "Tundra": [
        {"name": "Lobo Ártico", "dmg": 22, "hp": 40, "drops": {"Carne Cruda": (8, 15), "Piel de Invierno": (1, 2), "Huesos": (1, 2)}},
        {"name": "Oso Polar", "dmg": 40, "hp": 90, "drops": {"Carne Cruda": (20, 40), "Piel de Invierno": (2, 3), "Grasa": (3, 4)}},
        {"name": "Zorro Ártico", "dmg": 12, "hp": 20, "drops": {"Carne Blanca": (3, 6), "Piel de Invierno": (1, 2)}}
    ],
    "Pantano Manglar": [
        {"name": "Cocodrilo", "dmg": 45, "hp": 90, "drops": {"Carne Cruda": (10, 20), "Piel Escamosa": (2, 4), "Colmillo": (1, 2)}},
        {"name": "Anaconda Demonio", "dmg": 20, "hp": 50, "drops": {"Carne Blanca": (5, 10), "Piel Escamosa": (1, 3)}},
        {"name": "Enjambre Mosquitos", "dmg": 5, "hp": 15, "drops": {"Fibra": (1, 1)}}
    ],
    "Erial Volcánico": [
        {"name": "Araña Camello", "dmg": 25, "hp": 30, "drops": {"Veneno": (1, 3), "Carne Blanca": (2, 4)}},
        {"name": "Escorpión Rey", "dmg": 30, "hp": 60, "drops": {"Caparazón": (1, 3), "Veneno": (1, 2), "Grasa": (1,2)}}
    ],
    "Picos Alpinos": [
        {"name": "Oso Pardo Feroz", "dmg": 35, "hp": 70, "drops": {"Carne Cruda": (15, 30), "Piel": (1, 2), "Grasa": (2, 3)}},
        {"name": "Cóndor Gigante", "dmg": 20, "hp": 40, "drops": {"Carne Blanca": (5, 10), "Huesos": (1, 2)}},
        {"name": "Leopardo Nieves", "dmg": 30, "hp": 50, "drops": {"Carne Cruda": (10, 15), "Piel de Invierno": (1, 2)}}
    ]
}

WEATHER_EVENTS = {
    "Selva Tropical": [{"name": "Lluvia Torrencial", "warning": "Nubes oscuras y truenos lejanos... se acerca un diluvio.", "min_t": 2, "max_t": 4}],
    "Sabana": [{"name": "Sequía Extrema", "warning": "El sol abrasa y el viento es agobiante...", "min_t": 3, "max_t": 5}],
    "Pradera": [{"name": "Tormenta Eléctrica", "warning": "El cielo se nubla rápido y huele a ozono...", "min_t": 1, "max_t": 2}],
    "Desierto": [{"name": "Tormenta de Arena", "warning": "El viento levanta polvo en el horizonte...", "min_t": 2, "max_t": 4}],
    "Taiga": [{"name": "Ventisca de Nieve", "warning": "La temperatura cae drásticamente y empieza a nevar grueso...", "min_t": 2, "max_t": 3}],
    "Matorral": [{"name": "Incendio Forestal", "warning": "Huele a humo a lo lejos y el aire es seco...", "min_t": 1, "max_t": 3}],
    "Bosque Templado": [{"name": "Niebla Densa", "warning": "Una niebla espesa comienza a cubrir el suelo rápidamente...", "min_t": 2, "max_t": 4}],
    "Tundra": [{"name": "Tormenta Polar", "warning": "Vientos polares rugen a lo lejos acercándose...", "min_t": 3, "max_t": 5}],
    "Pantano Manglar": [{"name": "Lluvia Ácida", "warning": "Un vapor ácido sube del agua estancada...", "min_t": 2, "max_t": 3}],
    "Erial Volcánico": [{"name": "Lluvia de Ceniza", "warning": "El cielo se tiñe de rojo profundo y caen brasas...", "min_t": 2, "max_t": 4}],
    "Picos Alpinos": [{"name": "Ventisca de Hielo", "warning": "Los picos rugen y caen troquelados de granizo...", "min_t": 2, "max_t": 4}]
}

class World:
    def __init__(self):
        safe_biomes = ["Pradera", "Bosque Templado", "Sabana", "Selva Tropical", "Matorral"]
        self.current_biome = random.choice(safe_biomes)
        self.current_location = "Zona Abierta"
        self.has_camp = False
        self.camp_level = 0
        self.era = 1
        
        self.grid_size = 20
        self.player_x = self.grid_size // 2
        self.player_y = self.grid_size // 2
        self.grid = []
        self.active_events = [] # [{"x": x, "y": y, "name": "Manada", "timer": 5}]
        self.generate_grid_for_biome(self.current_biome)

    def generate_grid_for_biome(self, biome_idx):
        self.grid = []
        biome_data = BIOMES[biome_idx]
        
        for y in range(self.grid_size):
            row = []
            for x in range(self.grid_size):
                roll = random.randint(1, 100)
                cell_type = "Llanura"
                cell_icon = "¨"
                special = None
                
                # Basic terrain structure based on chance
                if roll < biome_data["water_chance"]:
                    cell_type = "Agua"
                    cell_icon = "≈"
                elif roll < biome_data["water_chance"] + 15: # Arbitrary tree chance
                    cell_type = "Bosque"
                    cell_icon = "♠"
                elif roll > 100 - biome_data["mineral_chance"]:
                    cell_type = "Montaña"
                    cell_icon = "▲"
                    
                # Seed obvious materials
                rng_special = random.randint(1, 100)
                if rng_special < 5:
                    special = "Mineral"
                    cell_icon = "💎"
                elif rng_special < 10 and cell_type == "Bosque":
                    special = "Planta"
                    cell_icon = "🌿"
                elif rng_special < 12 and cell_type != "Agua":
                    special = "Enemigo Fuerte"
                    cell_icon = "☠️"
                    
                row.append({
                    "type": cell_type, 
                    "icon": cell_icon, 
                    "searched": False, 
                    "special": special, 
                    "has_camp": False,
                    "has_plot": False, 
                    "plot_growth": 0,
                    "trap_loot": None,
                    "has_totem": False
                })
            self.grid.append(row)
            
        # Clear spawn point
        self.grid[self.player_y][self.player_x]["type"] = "Llanura"
        self.grid[self.player_y][self.player_x]["icon"] = "⛺"
        self.grid[self.player_y][self.player_x]["searched"] = True
        self.grid[self.player_y][self.player_x]["has_plot"] = False
        self.grid[self.player_y][self.player_x]["plot_growth"] = 0
        
    def get_weather_events(self):
        return WEATHER_EVENTS.get(self.current_biome, [])
        
    def generate_search_event(self, stance="EXPLORADOR"):
        biome = BIOMES[self.current_biome]
        roll = random.randint(1, 100)
        
        # Buffs based on stance
        if stance == "EXPLORADOR":
            roll = min(100, roll + 15) # higher roll favors later categories (food/water)
        elif stance == "COMBATE":
            roll = max(1, roll - 10) # favors earlier categories (enemies)
            
        current_threshold = biome["enemy_chance"]
        if roll <= current_threshold:
            enemy = random.choice(ENEMIES[self.current_biome]).copy()
            return {"type": "enemy", "data": enemy}
            
        current_threshold += biome["landmark_chance"]
        if roll <= current_threshold:
            if random.random() < 0.25: # Camino a otro bioma
                path_name = random.choice(list(TRANSITION_PATHS[self.current_biome].keys()))
                target_biome = TRANSITION_PATHS[self.current_biome][path_name]
                return {"type": "transition", "data": {"name": path_name, "target": target_biome}}
            else:
                landmark = random.choice(LANDMARKS[self.current_biome])
                return {"type": "landmark", "data": {"name": landmark}}
                
        current_threshold += 8 # Evento de oportunidad
        if roll <= current_threshold:
            opp = random.choice(OPPORTUNITIES)
            return {"type": "opportunity", "data": opp}
            
        current_threshold += biome.get("mineral_chance", 10)
        if roll <= current_threshold:
            if random.random() < 0.15: # Hallazgo Raro RNG
                if self.current_biome in ["Desierto", "Erial Volcánico"]: surf = "Obsidiana"
                elif self.current_biome == "Selva Tropical": surf = "Pepita de Oro"
                elif self.current_biome in ["Pantano Manglar", "Bosque Templado"]: surf = "Arcilla"
                elif self.current_biome == "Picos Alpinos": surf = "Pedazo de Hielo"
                else: surf = "Arena" # Arena es muy comun ahora
                return {"type": "resource", "data": {"name": f"Piedra milagrosamente suelta: {surf}", "amount": 0, "stat": "hunger", "item": surf, "item_amt": random.randint(1, 2)}}
            else:
                if self.current_biome == "Pantano Manglar": yield_n = "Arcilla"
                elif self.current_biome == "Erial Volcánico": yield_n = "Carbón"
                elif self.current_biome == "Taiga": yield_n = "Carbón"
                else: yield_n = "Pedernal"
                amt = random.randint(2, 4)
                if stance == "EXTRACCION": amt += 3 # Big boost
                return {"type": "mineral", "data": {"name": f"Yacimiento de {yield_n}", "tool_req": "Pico de Hueso", "item": yield_n, "amt": amt}}
                
        current_threshold += biome["food_chance"]
        if roll <= current_threshold:
            herb = random.choice(PLANTS[self.current_biome])
            return {"type": "resource", "data": {"name": "Botánica y Frutos", "amount": random.randint(15, 30), "stat": "hunger", "item": "Fibra", "item_amt": random.randint(1, 4), "herb": herb, "herb_amt": random.randint(0, 2)}}
            
        current_threshold += biome["water_chance"]
        if roll <= current_threshold:
            # 10% chance de contraer Disenteria visualmente por agua sucia se hace en el main.
            return {"type": "resource", "data": {"name": "Fuente de Agua", "amount": random.randint(20, 40), "stat": "thirst"}}
            
        return {"type": "nothing", "data": None}

    def update_traps(self):
        # Llamado al pasar el turno en el main
        for row in self.grid:
            for cell in row:
                if cell.get("trap"):
                    cell["trap_turns"] = cell.get("trap_turns", 0) + 1
                    # Probabilidad de captura despues de 5 turnos
                    if cell["trap_turns"] >= 10 and not cell.get("trap_loot"):
                        import random
                        if random.random() < 0.4:
                            if cell["trap"] == "Fosa":
                                cell["trap_loot"] = random.choice(["Carne Cruda", "Piel", "Huesos"])
                            elif cell["trap"] == "Nasa":
                                cell["trap_loot"] = "Carne Cruda" # Representa pescado
                                
    def update_world_events(self):
        # Decay de eventos activos
        new_events = []
        for ev in self.active_events:
            ev["timer"] -= 1
            if ev["timer"] > 0:
                new_events.append(ev)
            else:
                # Al terminar el evento, la celda vuelve a ser normal (Llanura)
                self.grid[ev["y"]][ev["x"]]["special"] = None
                self.grid[ev["y"]][ev["x"]]["icon"] = "¨"
        self.active_events = new_events
        
        # Probabilidad de spawn de nuevo evento (Migración)
        if random.random() < 0.05 and len(self.active_events) < 2:
            ex = random.randint(0, self.grid_size-1)
            ey = random.randint(0, self.grid_size-1)
            if self.grid[ey][ex]["type"] != "Agua":
                e_name = random.choice(["Manada de Mamuts", "Gran Migración Búfalo"])
                self.active_events.append({"x": ex, "y": ey, "name": e_name, "timer": 15})
                self.grid[ey][ex]["special"] = "EVENTO"
                self.grid[ey][ex]["icon"] = "🐘" if "Mamut" in e_name else "🐂"
                                
    def to_dict(self):
        return {
            "current_biome": self.current_biome,
            "current_location": self.current_location,
            "has_camp": self.has_camp,
            "camp_level": self.camp_level,
            "era": self.era,
            "player_x": self.player_x,
            "player_y": self.player_y,
            "grid": self.grid,
            "active_events": self.active_events
        }

    def from_dict(self, data):
        self.current_biome = data.get("current_biome", "Pradera")
        self.current_location = data.get("current_location", "Zona Abierta")
        self.has_camp = data.get("has_camp", False)
        self.camp_level = data.get("camp_level", 0)
        self.era = data.get("era", 1)
        self.player_x = data.get("player_x", 10)
        self.player_y = data.get("player_y", 10)
        self.grid = data.get("grid", [])
        self.active_events = data.get("active_events", [])
