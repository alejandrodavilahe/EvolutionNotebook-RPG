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
    "Ungüento Térmico": {"Musgo de Reno": 1, "Grasa": 1}
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

        # Armaduras (Body, Head, Boots)
        body = self.equipment["Body"]
        if body == "Abrigo Básico": self.defense += 8
        elif body == "Abrigo de Invierno": self.defense += 8
        elif body == "Peto Escamoso": self.defense += 15
        
        head = self.equipment["Head"]
        if head == "Casco de Hueso": self.defense += 5
        
        boots = self.equipment["Boots"]
        if boots == "Botas de Piel": self.defense += 3

    def pass_turn(self, action_cost={"hunger": 5, "thirst": 5, "energy": 5}):
        self.update_stats_from_gear()
        self.turn += 1
        
        base_cost = dict(action_cost)
        if self.equipment["Body"] == "Peto Escamoso":
            base_cost["energy"] = base_cost.get("energy", 0) + 10
        elif self.equipment["Weapon"] == "Lanza de Obsidiana":
            base_cost["energy"] = base_cost.get("energy", 0) + 5
            
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
        energy_cost = int(25 / self.search_efficiency)
        self.consume_energy(energy_cost)
        return self.pass_turn(action_cost={"hunger": 5, "thirst": 5, "energy": 0})
        
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
        return ext

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
