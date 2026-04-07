import random

RECIPES = {
    "Cuchillo Óseo": {"Huesos": 1, "Fibra": 1},
    "Lanza Caza": {"Huesos": 2, "Fibra": 2},
    "Hacha Primitiva": {"Huesos": 2, "Fibra": 3},
    "Pico de Hueso": {"Huesos": 3, "Fibra": 2},
    "Cuchillo de Pedernal": {"Pedernal": 1, "Fibra": 1},
    "Lanza de Obsidiana": {"Obsidiana": 1, "Huesos": 2},
    "Odre de Agua": {"Piel": 1, "Fibra": 1},
    "Filtro Grava": {"Arena": 1, "Fibra": 1},
    "Filtro Cerámico": {"Arcilla": 2, "Carbón": 1},
    "Filtro Purificador": {"Obsidiana": 2, "Carbón": 3},
    "Mochila de Cuero": {"Piel": 3, "Fibra": 3},
    "Abrigo Básico": {"Piel": 3, "Fibra": 1},
    "Peto Escamoso": {"Piel Escamosa": 4, "Fibra": 2},
    "Casco de Hueso": {"Huesos": 3, "Piel": 1},
    "Botas de Piel": {"Piel": 2, "Fibra": 1},
    "Trampa de Lazo": {"Fibra": 4, "Huesos": 1},
    "Abrigo de Invierno": {"Piel de Invierno": 2, "Grasa": 1}, 
    "Cataplasma Hemática": {"Milenrama": 2},
    "Antídoto de Guaco": {"Bejuco Guaco": 1, "Veneno": 1}, 
    "Antídoto de Escorpión": {"Ajenjo": 1, "Veneno": 1}, 
    "Infusión de Eucalipto": {"Eucalipto": 1, "Fibra": 1}, 
    "Pasta Disentería": {"Ajenjo": 1, "Milenrama": 1},
    "Té de Caléndula": {"Caléndula": 2}, 
    "Ungüento Térmico": {"Musgo de Reno": 1, "Grasa": 1},
    "Correa de Cuero": {"Piel": 2, "Fibra": 2},
    "Huerto de Piedra": {"Pedernal": 4, "Fibra": 3},
    "Soga de Fibra": {"Fibra": 3},
    "Antorcha": {"Fibra": 2, "Grasa": 1},
    "Lanza de Piedra": {"Piedra": 1, "Fibra": 2, "Huesos": 1},
    "Arco Primitivo": {"Soga de Fibra": 1, "Huesos": 2},
    "Flecha de Madera": {"Fibra": 1, "Huesos": 1},
    "Flecha de Piedra": {"Pedernal": 1, "Fibra": 1},
    "Cuenco de Barro": {"Arcilla": 2, "Fibra": 1},
    "Cuenco de Cerámica": {"Arcilla": 3, "Carbón": 2},
    "Caldo Fortificante": {"Agua Turbia": 1, "Huesos": 2, "Milenrama": 1},
    "Guiso de Miel": {"Carne Cruda": 1, "Miel": 1, "Agua Turbia": 1},
    "Trampa de Fosa": {"Fibra": 4, "Huesos": 2, "concept": "Trampeo"},
    "Nasa de Pesca": {"Soga de Fibra": 1, "Piedra": 2, "concept": "Trampeo"},
    "Tótem de Piedra": {"Piedra": 10, "Carbón": 2, "concept": "Espiritualidad"},
    "Ofrenda de Lobo": {"Piel": 1, "Huesos": 2, "concept": "Espiritualidad"},
    "Ofrenda de Búfalo": {"Piel": 1, "Grasa": 2, "concept": "Espiritualidad"},
    "Forja de Piedra": {"Pedernal": 5, "Huesos": 10, "concept": "Manejo del Fuego"}
}

class Player:
    def __init__(self):
        self.generation = 1
        self.evolution_stage = "Neandertal"
        
        self.base_dmg = 8
        self.defense = 0
        self.known_recipes = []
        self.sickness = []
        self.search_efficiency = 1
        self.in_tribe = False
        self.tribe_rep = 0
        self.is_chief = False
        self.era = 1
        
        self.equipment = {"Head": None, "Body": None, "Boots": None, "Weapon": None, "Offhand": None}
        self.traps_active = 0
        self.tribute_timer = 0
        self.follower = None # {"species": "Perro", "bonus_type": "DMG", "bonus_val": 5}
        self.follower_timer = 0 # Para produccion de recursos (Buffalo)
        
        self.torch_uses = 0
        self.pot_uses = 0
        self.arrows_fired = 0
        self.trophies = []
        self.ancestral_art = []
        self.active_buffs = [] # [{"name": "Lobo", "val": 8, "timer": 5}]
        self.chronic_entries = [] # ["Handwritten notes"]
        self.discovered_concepts = ["Recolección Básica"] # Ideas aprendidas
        
        # Meta-roguelite
        import json, os
        self.generation = 1
        self.perks_active = []
        if os.path.exists("savegame.json"):
            try:
                with open("savegame.json", "r") as f:
                    d = json.load(f)
                    self.generation = d.get("generation", 1)
                    self.perks_active = d.get("perks", [])
            except: pass
        
        # Stats maximos
        self.max_hp = 100
        self.max_hunger = 100
        self.max_thirst = 100
        self.max_energy = 100
        self.max_sanity = 100
        self.defense = 0
        
        if "METABOLISMO" in self.perks_active:
            self.max_hunger = 140
            self.max_thirst = 140
        if "PIEL_GRUESA" in self.perks_active:
            self.defense += 5
        if "BRAZOS_GORILA" in self.perks_active:
            self.base_dmg += 3
        
        # Stats actuales
        self.hp = self.max_hp
        self.hunger = self.max_hunger
        self.thirst = self.max_thirst
        self.energy = self.max_energy
        self.sanity = self.max_sanity
        
        self.inventory = {}
        self.turn = 1
        self.alive = True
        self.cause_of_death = ""
        
        self.update_stats_from_gear()

    def update_stats_from_gear(self):
        # Base stats iniciales
        self.base_dmg = 8
        self.defense = 0
        self.search_efficiency = 1.0
        
        # Meta perks
        if "PIEL_GRUESA" in self.perks_active:
            self.defense += 5
        if "BRAZOS_GORILA" in self.perks_active:
            self.base_dmg += 3
        if "OJOS_BUHO" in self.perks_active:
            self.search_efficiency += 0.5
            
        # Armas (Weapon)
        wep = self.equipment["Weapon"]
        if wep == "Cuchillo Óseo": self.base_dmg += 10
        elif wep == "Lanza Caza": self.base_dmg += 20
        elif wep == "Hacha Primitiva": self.base_dmg += 12; self.search_efficiency += 0.6
        elif wep == "Pico de Hueso": self.base_dmg += 15
        elif wep == "Cuchillo de Pedernal": self.base_dmg += 30
        elif wep == "Lanza de Obsidiana": self.base_dmg += 67
        elif wep == "Lanza de Piedra": self.base_dmg += 25

        # Armaduras (Body, Head, Boots)
        body = self.equipment["Body"]
        if body == "Abrigo Básico": self.defense += 8
        elif body == "Abrigo de Invierno": self.defense += 8
        elif body == "Peto Escamoso": self.defense += 15
        
        head = self.equipment["Head"]
        if head == "Casco de Hueso": self.defense += 5
        
        boots = self.equipment["Boots"]
        if boots == "Botas de Piel": self.defense += 3
        
        # Buffs de Tótems (Stackables entre diferentes tipos)
        for b in self.active_buffs:
            if b["name"] == "Lobo": self.base_dmg += b["val"]
            elif b["name"] == "Búfalo": self.defense += b["val"]
            elif b["name"] == "Águila": self.search_efficiency += b["val"]
            
        # Seguidores (Followers)
        if self.follower:
            sp = self.follower["species"]
            if sp == "Perro Salvaje": self.base_dmg += 5
            elif sp == "Lobo": self.defense += 10
            elif sp == "Zorro": 
                self.max_hunger += 20
                self.max_thirst += 20
            elif sp == "Lince": self.search_efficiency += 0.5

    def pass_turn(self, action_cost={"hunger": 5, "thirst": 5, "energy": 5}):
        self.update_stats_from_gear()
        self.turn += 1
        
        time = self.get_time_of_day()
        
        base_cost = dict(action_cost)
        if self.equipment["Body"] == "Peto Escamoso":
            base_cost["energy"] = base_cost.get("energy", 0) + 10
        elif self.equipment["Weapon"] == "Lanza de Obsidiana":
            base_cost["energy"] = base_cost.get("energy", 0) + 5
            
            if self.torch_uses > 0:
                self.torch_uses -= 1
            # Sanidad solo empieza a drenar pasivamente en Era 2+ o en Noche/Tormentas
            if self.era > 1:
                self.sanity = max(0, self.sanity - (self.era - 1))
        
        # Decay de Buffs de Tótems
        new_buffs = []
        for b in self.active_buffs:
            b["timer"] -= 1
            if b["timer"] > 0:
                new_buffs.append(b)
        self.active_buffs = new_buffs
            
        self.hunger = max(0, self.hunger - base_cost.get("hunger", 0))
        self.thirst = max(0, self.thirst - base_cost.get("thirst", 0))
        self.energy = max(0, self.energy - base_cost.get("energy", 0))
        
        self.check_vital_signs()
        
    def check_vital_signs(self):
        # Stats at 0 drain HP
        hp_drain = 0
        if self.hunger <= 0:
            hp_drain += 10
        if self.thirst <= 0:
            hp_drain += 15
            
        if hp_drain > 0:
            self.hp = max(0, self.hp - hp_drain)
            
        # Check if dead
        if self.hp <= 0:
            self.alive = False
            if self.hunger <= 0:
                self.cause_of_death = "Inanición"
            elif self.thirst <= 0:
                self.cause_of_death = "Deshidratación"
            else:
                self.cause_of_death = "Causas naturales/Daño"

    def check_disease_damage(self):
        dmg_msg = ""
        if "Envenenamiento" in self.sickness:
            self.hp -= 15
            dmg_msg += "[Veneno -15HP] "
        if "Infección" in self.sickness:
            self.energy = max(0, self.energy - 10)
            self.hp -= 5
            dmg_msg += "[Infección -10E -5HP] "
        if "Disentería" in self.sickness:
            self.thirst = max(0, self.thirst - 20)
            self.hunger = max(0, self.hunger - 10)
            dmg_msg += "[Disentería Drena Líquidos] "
        if "Hipotermia" in self.sickness:
            self.hp -= 10
            self.energy = max(0, self.energy - 15)
            dmg_msg += "[Hipotermia -10HP -15E] "
            
        if self.hp <= 0 and self.alive:
            self.alive = False
            self.cause_of_death = f"Sucumbió por: {', '.join(self.sickness)}"
            
        return dmg_msg.strip()

    def rest(self, camp_level=0):
        if camp_level == 3:
            self.energy = min(self.max_energy, self.energy + 100)
            self.heal_stat("hp", 30)
            self.pass_turn(action_cost={"hunger": 0, "thirst": 0, "energy": 0})
        elif camp_level == 2:
            self.energy = min(self.max_energy, self.energy + 80)
            self.heal_stat("hp", 20)
            self.pass_turn(action_cost={"hunger": 1, "thirst": 1, "energy": 0})
        elif camp_level == 1:
            self.energy = min(self.max_energy, self.energy + 60)
            self.heal_stat("hp", 15)
            self.pass_turn(action_cost={"hunger": 3, "thirst": 3, "energy": 0})
        else:
            self.energy = min(self.max_energy, self.energy + 30)
            self.pass_turn(action_cost={"hunger": 8, "thirst": 8, "energy": 0})
        
    def search(self):
        # Buscar consume energía escalada por herramientas
        time = self.get_time_of_day()
        energy_cost = int(25 / self.search_efficiency)
        
        # Penalizador nocturno
        if time == "Noche" and self.torch_uses <= 0:
            energy_cost = int(energy_cost * 1.3)
            
        self.consume_energy(energy_cost)
        return self.pass_turn(action_cost={"hunger": 5, "thirst": 5, "energy": 0})
        
    def get_time_of_day(self):
        cycle_pos = self.turn % 20
        if 1 <= cycle_pos <= 10: return "Día"
        if 11 <= cycle_pos <= 13: return "Atardecer"
        return "Noche" # 14-20 y 0
        
    def take_enemy_hit(self, enemy_name, dmg_raw, multiplier=1.0):
        import random
        dmg_received = max(1, int(dmg_raw * multiplier) - self.defense)
        self.hp -= dmg_received
        
        # Probabilidades de infecciones al recibir daños medianos/graves
        if dmg_received > 4:
            e_name_l = enemy_name.lower()
            if any(k in e_name_l for k in ["cobra", "cascabel", "mamba", "dardo", "escorp", "víbora", "anaconda"]):
                if random.random() < 0.4 and "Envenenamiento" not in self.sickness:
                    self.sickness.append("Envenenamiento")
            if any(k in e_name_l for k in ["hiena", "perro", "zorro", "jabalí"]):
                if random.random() < 0.3 and "Infección" not in self.sickness:
                    self.sickness.append("Infección")
                    
        if self.hp <= 0:
            self.alive = False
            self.cause_of_death = f"Asesinado salvajemente por {enemy_name}"
            
        return dmg_received
        
    def heal_stat(self, stat, amount):
        if stat == "hunger":
            self.hunger = min(self.max_hunger, self.hunger + amount)
        elif stat == "thirst":
            self.thirst = min(self.max_thirst, self.thirst + amount)
        elif stat == "hp":
            self.hp = min(self.max_hp, self.hp + amount)

    def consume_energy(self, amount):
        self.energy = max(0, self.energy - amount)

    def add_to_inventory(self, item, amount):
        if amount > 0:
            if item in self.inventory:
                self.inventory[item] += amount
            else:
                self.inventory[item] = amount

    def apply_item_benefits(self, item_name):
        ext = ""
        
        # Equipables ahora van al inventario físico para equiparse
        equippables = ["Cuchillo Óseo", "Lanza Caza", "Hacha Primitiva", "Pico de Hueso", 
                       "Cuchillo de Pedernal", "Lanza de Obsidiana", "Abrigo Básico", 
                       "Abrigo de Invierno", "Peto Escamoso", "Casco de Hueso", "Botas de Piel", "Mochila de Cuero"]
                       
        if item_name in equippables:
            self.inventory[item_name] = self.inventory.get(item_name, 0) + 1
            if item_name == "Abrigo de Invierno" and "Hipotermia" in self.sickness:
                self.sickness.remove("Hipotermia")
            if item_name == "Mochila de Cuero":
                self.max_energy = 150
            return "(Obtuviste la pieza físicamente. Ve a 'Modificar Set y Armas' para equiparla y usarla)"

        if item_name == "Correa de Cuero":
            self.inventory["Correa de Cuero"] = self.inventory.get("Correa de Cuero", 0) + 1
            return "(Herramienta de domesticación lista)"
        
        if item_name == "Huerto de Piedra":
            # Esto se manejaría en el main para colocarlo en la grid
            return "HUERTO_READY"

        if item_name == "Soga de Fibra":
            self.inventory["Soga de Fibra"] = self.inventory.get("Soga de Fibra", 0) + 1
            return "(Herramienta versátil de amarre obtenida)"
        
        if item_name == "Antorcha":
            self.inventory["Antorcha"] = self.inventory.get("Antorcha", 0) + 1
            self.torch_uses = 10
            return "(Luz portátil de 10 turnos de duración para la noche)"
            
        if item_name == "Lanza de Piedra":
            self.inventory["Lanza de Piedra"] = self.inventory.get("Lanza de Piedra", 0) + 1
            return "(Arma de piedra más pesada que la de hueso)"

        if item_name == "Trampa de Lazo":
            self.traps_active += 1
            ext = "(Armaste una trampa fija en el mundo. Cazará sola.)"
        elif item_name == "Filtro Grava":
            self.inventory["Filtros Grava"] = self.inventory.get("Filtros Grava", 0) + 3
            ext = "(Creaste 3 filtros sueltos para mezclar con Agua Turbia)"
        elif item_name == "Filtro Cerámico":
            self.inventory["Filtros Cerámicos"] = 1
            self.inventory["Usos Cerámicos"] = 15
            ext = "(Filtro macizo de 15 usos creado)"
        elif item_name == "Filtro Purificador":
            self.inventory["Filtro Infinipurificador"] = 1
            ext = "(Purificación infinita para usar en crafteo)"
        elif item_name == "Odre de Agua":
            self.inventory["Cargas Agua"] = 3
            ext = "(Contenedor fabricado y lleno de agua 3/3)"
        elif item_name == "Mochila de Cuero":
            self.max_energy = 150
            ext = "(Energía Máxima +50)"
        elif item_name == "Carne Asada":
            self.heal_stat("hunger", 35)
            self.heal_stat("hp", 15)
            ext = "(Consumible Rico: Cura Hambre y Vida)"
        elif item_name == "Cataplasma Hemática":
            self.heal_stat("hp", 40)
            ext = "(Cura 40 HP)"
        elif item_name in ["Antídoto de Guaco", "Antídoto de Escorpión"]:
            if "Envenenamiento" in self.sickness:
                self.sickness.remove("Envenenamiento")
            ext = "(Curó Envenenamiento)"
        elif item_name in ["Infusión de Eucalipto", "Té de Caléndula"]:
            if "Infección" in self.sickness:
                self.sickness.remove("Infección")
            ext = "(Curó Infección/Fiebre)"
        elif item_name == "Pasta Disentería":
            if "Disentería" in self.sickness:
                self.sickness.remove("Disentería")
            ext = "(Curó Disentería)"
        elif item_name == "Ungüento Térmico":
            if "Hipotermia" in self.sickness:
                self.sickness.remove("Hipotermia")
            ext = "(Curó Hipotermia extrema)"
            
        elif item_name == "Arco Primitivo":
            self.inventory["Arco Primitivo"] = self.inventory.get("Arco Primitivo", 0) + 1
            ext = "(Arma de rango lista. Necesita flechas.)"
        elif item_name == "Flecha de Madera":
            self.inventory["Flechas"] = self.inventory.get("Flechas", 0) + 5
            ext = "(Crafteaste 5 flechas básicas de madera)"
        elif item_name == "Flecha de Piedra":
            self.inventory["Flechas"] = self.inventory.get("Flechas", 0) + 5
            ext = "(Crafteaste 5 flechas de punta pétrea)"
        elif item_name == "Cuenco de Barro":
            self.inventory["Cuenco de Barro"] = self.inventory.get("Cuenco de Barro", 0) + 1
            self.pot_uses = 15
            ext = "(Recipiente frágil: 15 usos restantes)"
        elif item_name == "Cuenco de Cerámica":
            self.inventory["Cuenco de Cerámica"] = self.inventory.get("Cuenco de Cerámica", 0) + 1
            ext = "(Recipiente de alta calidad: Permanente)"
            
        elif item_name == "Caldo Fortificante":
            # Requiere cuenco
            if self.inventory.get("Cuenco de Barro", 0) > 0 or self.inventory.get("Cuenco de Cerámica", 0) > 0:
                self.heal_stat("hp", 25)
                self.heal_stat("energy", 30)
                if self.inventory.get("Cuenco de Barro", 0) > 0:
                    self.pot_uses -= 1
                    if self.pot_uses <= 0:
                        self.inventory["Cuenco de Barro"] -= 1
                        ext = "(¡El cuenco se agrietó y se rompió! Pero el Caldo te dio +25HP +30E)"
                    else: ext = f"(Sopa caliente: +25HP +30E. Cuenco: {self.pot_uses} usos)"
                else: ext = "(Sopa caliente en cerámica: +25HP +30E)"
            else:
                return "Necesitas un Cuenco para contener y cocinar el Caldo."
                
        elif item_name == "Guiso de Miel":
            if self.inventory.get("Cuenco de Barro", 0) > 0 or self.inventory.get("Cuenco de Cerámica", 0) > 0:
                self.heal_stat("hunger", 60)
                self.heal_stat("thirst", 40)
                if self.inventory.get("Cuenco de Barro", 0) > 0:
                    self.pot_uses -= 1
                    if self.pot_uses <= 0:
                        self.inventory["Cuenco de Barro"] -= 1
                        ext = "(¡Cuenco roto! El Guiso fue excelente: +60H +40S)"
                    else: ext = f"(Guiso dulce y denso: +60H +40S. Cuenco: {self.pot_uses} usos)"
                else: ext = "(Guiso en cerámica: +60H +40S)"
            else:
                return "Sin un Cuenco no puedes mezclar ni servir este Guiso."
                
        elif item_name == "Trampa de Fosa":
            self.inventory["Trampa de Fosa"] = self.inventory.get("Trampa de Fosa", 0) + 1
            ext = "(Herramienta de caza pasiva cargada al inventario. Colócala en tierra firme.)"
        elif item_name == "Nasa de Pesca":
            self.inventory["Nasa de Pesca"] = self.inventory.get("Nasa de Pesca", 0) + 1
            ext = "(Trampa de agua ligera. Colócala cerca de fuentes de agua.)"
        
        elif item_name == "Tótem de Piedra":
            self.inventory["Tótem de Piedra"] = self.inventory.get("Tótem de Piedra", 0) + 1
            ext = "(Estructura ritual lista para colocar en el campamento)"
            
        return ext

    def add_chronicle(self, text):
        import random
        # 25% de mencionar ancestros si gen > 1
        if self.generation > 1 and random.random() < 0.25:
            prefixes = ["Los antiguos decían: ", "Sabiduría del clan: ", "Mis abuelos sabían que "]
            text = random.choice(prefixes) + text
            
        self.chronic_entries.append(text)
        if len(self.chronic_entries) > 5:
            self.chronic_entries.pop(0)

    def discover(self, concept):
        if concept not in self.discovered_concepts:
            self.discovered_concepts.append(concept)
            return True
        return False

    def think_and_invent(self):
        if self.energy < 15:
            return "Estás muy cansado para pensar en nuevas ideas."
        self.pass_turn(action_cost={"hunger": 5, "thirst": 5, "energy": 15})
        
    def manual_craft(self, items_list):
        if len(items_list) < 2: return "Selecciona exactamente 2 ítems del inventario clickeando sobre ellos."
        
        # Especial logic for water filtering dynamically on the go:
        if "Agua Turbia" in items_list:
            if "Filtro Infinipurificador" in items_list:
                self.inventory["Agua Turbia"] -= 1
                self.inventory["Cargas Agua"] = self.inventory.get("Cargas Agua", 0) + 1
                return "Filtraste el cieno del agua instantaneamente con tu Purificador Permanente."
            elif "Filtros Cerámicos" in items_list:
                if self.inventory.get("Usos Cerámicos", 0) > 0:
                    self.inventory["Agua Turbia"] -= 1
                    self.inventory["Usos Cerámicos"] -= 1
                    self.inventory["Cargas Agua"] = self.inventory.get("Cargas Agua", 0) + 1
                    msg = f"Filtro cerámico exitoso. Le quedan {self.inventory['Usos Cerámicos']} usos al bloque."
                    if self.inventory["Usos Cerámicos"] <= 0:
                        self.inventory["Filtros Cerámicos"] = 0
                    return msg
            elif "Filtros Grava" in items_list:
                if self.inventory.get("Filtros Grava", 0) > 0:
                    self.inventory["Agua Turbia"] -= 1
                    self.inventory["Filtros Grava"] -= 1
                    self.inventory["Cargas Agua"] = self.inventory.get("Cargas Agua", 0) + 1
                    return "El filtro de grava deshizo el barro, obteniendo agua potable (E 1 Uso)."
        
        match_found = None
        for r_name, reqs in RECIPES.items():
            req_keys = list(reqs.keys())
            
            # Checar si los dos ítems concuerdan con la receta (que pede 1 o 2 ingredientes distintos)
            if len(req_keys) == 1:
                if req_keys[0] == items_list[0] and req_keys[0] == items_list[1] and reqs[req_keys[0]] <= 2:
                    match_found = r_name
            elif len(req_keys) == 2:
                if (req_keys[0] in items_list and req_keys[1] in items_list):
                    match_found = r_name
                    
            if match_found:
                # Verificar cantidad
                for k, v in reqs.items():
                    if self.inventory.get(k, 0) < v:
                        return f"Descubriste la lógica de {r_name}, pero te faltan materiales ({k} x{v})."
                break
                
        if match_found:
            for k, v in RECIPES[match_found].items():
                self.inventory[k] -= v
            
            msg = self.apply_item_benefits(match_found)
            
            if match_found not in self.known_recipes:
                self.known_recipes.append(match_found)
                return f"¡EUREKA MACGYVER! Mezclaste descubriendo: {match_found}. {msg}"
            else:
                return f"Fabricaste nuevamente: {match_found}. {msg}"
        else:
            return "Majaste los dos materiales con una piedra pero no ocurrió nada útil. Intenta otra lógica."
        
    def craft_recipe(self, recipe_name):
        if recipe_name not in self.known_recipes:
            return "Aún no descubres esto."
        reqs = RECIPES[recipe_name]
        has_enough = all(self.inventory.get(k, 0) >= v for k, v in reqs.items())
        if has_enough:
            for k, v in reqs.items():
                self.inventory[k] -= v
            ext = self.apply_item_benefits(recipe_name)
            return f"Crafteaste {recipe_name} usando tus inventos. {ext}"
        else:
            return f"Faltan materiales para fabricar {recipe_name}."

    def save_pantheon(self, puntos, perks, gen):
        import json
        with open("savegame.json", "w") as f:
            json.dump({"puntos": puntos, "perks": perks, "generation": gen}, f)

    def to_dict(self):
        return {
            "generation": self.generation,
            "evolution_stage": self.evolution_stage,
            "turn": self.turn,
            "hp": self.hp,
            "hunger": self.hunger,
            "thirst": self.thirst,
            "energy": self.energy,
            "inventory": self.inventory,
            "known_recipes": self.known_recipes,
            "equipment": self.equipment,
            "sickness": self.sickness,
            "in_tribe": self.in_tribe,
            "tribe_rep": self.tribe_rep,
            "is_chief": self.is_chief,
            "era": self.era,
            "perks_active": self.perks_active,
            "follower": self.follower,
            "follower_timer": self.follower_timer,
            "pot_uses": self.pot_uses,
            "arrows_fired": self.arrows_fired,
            "torch_uses": self.torch_uses,
            "trophies": self.trophies,
            "sanity": self.sanity,
            "ancestral_art": self.ancestral_art,
            "active_buffs": self.active_buffs,
            "chronic_entries": self.chronic_entries,
            "discovered_concepts": self.discovered_concepts
        }

    def from_dict(self, data):
        self.generation = data.get("generation", 1)
        self.evolution_stage = data.get("evolution_stage", "Neandertal")
        self.turn = data.get("turn", 1)
        self.hp = data.get("hp", 100)
        self.hunger = data.get("hunger", 100)
        self.thirst = data.get("thirst", 100)
        self.energy = data.get("energy", 100)
        self.inventory = data.get("inventory", {})
        self.known_recipes = data.get("known_recipes", [])
        self.equipment = data.get("equipment", {"Head": None, "Body": None, "Boots": None, "Weapon": None})
        self.sickness = data.get("sickness", [])
        self.in_tribe = data.get("in_tribe", False)
        self.tribe_rep = data.get("tribe_rep", 0)
        self.is_chief = data.get("is_chief", False)
        self.era = data.get("era", 1)
        self.perks_active = data.get("perks_active", [])
        self.follower = data.get("follower", None)
        self.follower_timer = data.get("follower_timer", 0)
        self.pot_uses = data.get("pot_uses", 0)
        self.arrows_fired = data.get("arrows_fired", 0)
        self.torch_uses = data.get("torch_uses", 0)
        self.trophies = data.get("trophies", [])
        self.sanity = data.get("sanity", 100)
        self.ancestral_art = data.get("ancestral_art", [])
        self.active_buffs = data.get("active_buffs", [])
        self.chronic_entries = data.get("chronic_entries", [])
        self.discovered_concepts = data.get("discovered_concepts", ["Recolección Básica"])
        self.update_stats_from_gear()
