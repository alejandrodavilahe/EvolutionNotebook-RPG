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
    "Pradera": ["Lago Sereno", "Colina de Viento", "Madriguera Oculta", "Arroyo Abierto"],
    "Desierto": ["Oasis Profundo", "Cañón Rocoso", "Cueva Lúgubre", "Mesa Elevada"],
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
    {"name": "Humo en el Horizonte", "desc": "Ves a otros humanos rústicos... ¿Acercarte para unirte? (Riesgo 30%: Caníbales Emboscadores).", "cost": {"energy": 20}, "reward": {}, "risk_disease": None, "risk_chance": 0, "special": "TRIBU"}
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
