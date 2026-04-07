import pygame

class Button:
    def __init__(self, x, y, width, height, text, font, color, text_color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.text_color = text_color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface):
        current_color = self.hover_color if self.is_hovered else self.color
        # Dibujar rectangulo de fondo del boton con bordes redondeados
        pygame.draw.rect(surface, current_color, self.rect, border_radius=8)
        # Dibujar contorno para el estilo minimalista o 'dibujado'
        pygame.draw.rect(surface, (80, 80, 80), self.rect, width=2, border_radius=8) 
        
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                return True
        return False

def draw_bar(surface, x, y, width, height, value, max_value, color, label, font):
    # Fondo de la barra (Gris)
    bg_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, (210, 210, 210), bg_rect, border_radius=4)
    
    # Relleno de la barra (el color)
    ratio = max(0.0, min(1.0, value / max_value))
    fill_width = int(width * ratio)
    if fill_width > 0:
        fill_rect = pygame.Rect(x, y, fill_width, height)
        pygame.draw.rect(surface, color, fill_rect, border_radius=4)
        
    # Contorno de la barra
    pygame.draw.rect(surface, (80, 80, 80), bg_rect, width=2, border_radius=4)
    
    # Etiqueta de texto de la estadística
    label_surf = font.render(f"{label}: {value}/{max_value}", True, (50, 50, 50))
    surface.blit(label_surf, (x, y - 22))

def draw_text_box(surface, text, x, y, width, height, font, bg_color=(240, 240, 240), text_color=(50, 50, 50)):
    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, bg_color, rect, border_radius=6)
    pygame.draw.rect(surface, (150, 150, 150), rect, width=2, border_radius=6)
    
    # Text wrapping logic para que no se salga del recuadro
    words_by_line = []
    for chunk in str(text).split('\n'):
        if not chunk:
            words_by_line.append([])
        else:
            words_by_line.append(chunk.split(' '))
            
    lines = []
    for line_words in words_by_line:
        if not line_words:
            lines.append("")
            continue
            
        current_line = ""
        for word in line_words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] < width - 20: # Margen de padding
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())
            
    total_height = len(lines) * font.get_height()
    start_y = rect.centery - total_height // 2
    
    for i, line in enumerate(lines):
        text_surf = font.render(line, True, text_color)
        text_rect = text_surf.get_rect(centerx=rect.centerx, top=start_y + i * font.get_height())
        surface.blit(text_surf, text_rect)

def draw_inventory(surface, x, y, width, height, inventory_dict, font_small, title_font):
    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, (50, 50, 50), rect, border_radius=6)
    pygame.draw.rect(surface, (150, 150, 150), rect, width=2, border_radius=6)
    
    title_surf = title_font.render("Inventario", True, (240, 240, 240))
    surface.blit(title_surf, (x + 10, y + 10))
    
    y_offset = y + 40
    slots = []
    for item, qty in inventory_dict.items():
        if qty > 0:
            btn_rect = pygame.Rect(x + 10, y_offset, width - 20, 20)
            pygame.draw.rect(surface, (70, 70, 70), btn_rect, border_radius=4)
            
            item_surf = font_small.render(f"- {item} x{qty}", True, (240, 240, 240))
            surface.blit(item_surf, (x + 15, y_offset + 2))
            slots.append({"rect": btn_rect, "item": item})
            y_offset += 25
            
    return slots

def draw_minimap(surface, world_obj, player, font_main, font_small, x, y, map_px_size):
    # Dibuja un grid basado en world_obj.grid The area is a square of `map_px_size`
    rect = pygame.Rect(x, y, map_px_size, map_px_size)
    pygame.draw.rect(surface, (30, 30, 30), rect, border_radius=8)
    pygame.draw.rect(surface, (100, 100, 100), rect, width=4, border_radius=8)
    
    grid = world_obj.grid
    grid_size = world_obj.grid_size
    cell_px = map_px_size // grid_size
    
    px, py = world_obj.player_x, world_obj.player_y
    # Fog of war radius
    vision_radius = 2.5 + player.search_efficiency # Ojos de Búho gives +0.5, hachas give +0.6
    
    for row_y in range(grid_size):
        for col_x in range(grid_size):
            cell = grid[row_y][col_x]
            
            # Simple distance logic for Fog of War
            dist = ((col_x - px)**2 + (row_y - py)**2)**0.5
            
            cx = x + col_x * cell_px
            cy = y + row_y * cell_px
            
            if dist > vision_radius:
                # Niebla de Guerra
                pygame.draw.rect(surface, (40, 40, 40), (cx, cy, cell_px, cell_px))
            else:
                # Colors based on terrain
                bg_color = (60, 90, 60)
                if cell["type"] == "Agua": bg_color = (70, 130, 180)
                elif cell["type"] == "Montaña": bg_color = (120, 110, 100)
                elif cell["type"] == "Bosque": bg_color = (40, 70, 40)
                elif cell["type"] == "Llanura": bg_color = (100, 140, 90)
                
                if cell["searched"]:
                    bg_color = (max(20, bg_color[0]-30), max(20, bg_color[1]-30), max(20, bg_color[2]-30))
                    
                pygame.draw.rect(surface, bg_color, (cx, cy, cell_px, cell_px))
                pygame.draw.rect(surface, (50, 50, 50), (cx, cy, cell_px, cell_px), width=1)
                
                # Draw special icons
                if cell["icon"] and not cell["searched"]:
                    icon_surf = font_small.render(cell["icon"], True, (200, 200, 200))
                    surface.blit(icon_surf, (cx + 2, cy + 2))
                
                if cell.get("has_plot"):
                    pygame.draw.circle(surface, (100, 255, 100), (cx + cell_px//2, cy + cell_px//2), 2)
                    
    # Draw Player Avatar/Dot on Map
    p_rect = (x + px * cell_px + cell_px//2, y + py * cell_px + cell_px//2)
    # Silueta de cazador esquemático
    pygame.draw.line(surface, (50, 50, 55), (p_rect.centerx, p_rect.top+2), (p_rect.centerx, p_rect.bottom-2), 2) # Cuerpo
    pygame.draw.line(surface, (50, 50, 55), (p_rect.left, p_rect.centery), (p_rect.right, p_rect.centery), 1) # Brazos
    pygame.draw.circle(surface, (50, 50, 55), (p_rect.centerx, p_rect.top+4), 3) # Cabeza
    pygame.draw.line(surface, (120, 80, 20), (p_rect.right, p_rect.top), (p_rect.left, p_rect.bottom), 1) # Lanza

def draw_chronicle_notes(surface, entries, font):
    # Notas al margen, algo inclinadas y con tinte de tinta
    if not entries: return
    sw, sh = surface.get_size()
    color = (40, 50, 80, 160) # Azul tinta tenue
    
    y_offset = 150
    for entry in entries:
        # Renderizar pequeño y algo rotado (Pygame rotate es costoso, simulamos con offset si es necesario)
        txt_surf = font.render(entry, True, color)
        # Rotar ligeramente para realismo
        txt_surf = pygame.transform.rotate(txt_surf, 2)
        surface.blit(txt_surf, (sw - 280, y_offset))
        y_offset += 40

def draw_paper_weather_fx(surface, weather_type, intensity_seed):
    import random
    rng = random.Random(intensity_seed)
    sw, sh = surface.get_size()
    
    if weather_type in ["Lluvia Torrencial", "Lluvia Ácida"]:
        # Manchas de humedad (darkening sutil)
        for _ in range(5):
            wx = rng.randint(50, sw-150)
            wy = rng.randint(50, sh-150)
            w_size = rng.randint(30, 80)
            temp_s = pygame.Surface((w_size*2, w_size*2), pygame.SRCALPHA)
            pygame.draw.ellipse(temp_s, (0, 0, 20, 15), (0, 0, w_size*2, w_size))
            surface.blit(temp_s, (wx, wy))
        # Blur Estético (muy leve alpha smear)
        smear = surface.subsurface((100, 100, 200, 200)).copy()
        smear.set_alpha(40)
        surface.blit(smear, (102, 102))

    elif weather_type == "Tormenta de Arena":
        # Grit/Polvo
        for _ in range(200):
            px = rng.randint(0, sw)
            py = rng.randint(0, sh)
            pygame.draw.circle(surface, (100, 80, 40, 40), (px, py), 1)

def draw_notebook_binding(surface):
    # Lomo de Cuero Antiguo en el margen izquierdo
    sw, sh = surface.get_size()
    leather_color = (100, 60, 40)
    pygame.draw.rect(surface, leather_color, (0, 0, 50, sh))
    # Textura y Sombra del Lomo
    pygame.draw.rect(surface, (80, 50, 35), (45, 0, 5, sh)) # Sombra transicion
    for i in range(0, sh, 50):
        pygame.draw.line(surface, (120, 80, 60), (0, i), (50, i+20), 1) # Grietas cuero
    # Bordes gastados
    pygame.draw.rect(surface, (230, 215, 180), (50, 0, 10, sh))

def draw_worn_edges(surface):
    # Amarilleo y sombras en las esquinas
    sw, sh = surface.get_size()
    for corner in [(0,0), (sw,0), (0,sh), (sw,sh)]:
        # Muy sutil gradiente circular de suciedad/viejera
        pass # Implementado como sombras suaves en el paper_layer

def draw_ritual_smoke(surface, turn_seed):
    import random
    rng = random.Random(turn_seed)
    sw, sh = surface.get_size()
    for _ in range(5):
        sx = rng.randint(50, sw-50)
        sy = rng.randint(sh-100, sh)
        size = rng.randint(10, 35)
        alpha = rng.randint(20, 60)
        # Circulo de humo tenue
        temp_s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.circle(temp_s, (150, 150, 160, alpha), (size, size), size)
        surface.blit(temp_s, (sx-size, sy - (turn_seed % 20) * 2))

def draw_cave_art(surface, ancestral_art):
    # Pinturas rupestres tenues que persisten (carvadas en el fondo)
    # ancestral_art = ["hand", "mammoth", "chief", "fire", "tame"]
    sw, sh = surface.get_size()
    art_color = (200, 190, 180, 100) # Muy tenue
    
    for art in ancestral_art:
        if art == "hand":
            # Silueta de mano (minimalista)
            pygame.draw.circle(surface, art_color, (100, 100), 10)
            for i in range(5):
                pygame.draw.line(surface, art_color, (100, 100), (90 + i*5, 70), 3)
        elif art == "mammoth":
            pygame.draw.ellipse(surface, art_color, (sw//2, sh-150, 100, 60))
            pygame.draw.line(surface, art_color, (sw//2+10, sh-100), (sw//2+10, sh-70), 5) # Pata
        elif art == "chief":
            pygame.draw.line(surface, art_color, (sw-150, 100), (sw-150, 180), 4) # Cuerpo
            pygame.draw.line(surface, art_color, (sw-180, 140), (sw-120, 140), 2) # Brazos
        elif art == "fire":
            pygame.draw.polygon(surface, art_color, [(150, sh-100), (170, sh-140), (190, sh-100)], 0)
        elif art == "tame":
            pygame.draw.circle(surface, art_color, (sw-100, sh-100), 15, 2)
            pygame.draw.circle(surface, art_color, (sw-130, sh-100), 8, 2)

def draw_character_profile(surface, player, x, y):
    # Dibujo dinámico del protagonista en el cuaderno
    # x, y es la esquina superior izquierda del área del personaje
    body_color = (40, 45, 60) # Tinta oscura
    
    # Silueta Base según Era
    if player.era == 1:
        # Encorvado (Neandertal)
        pygame.draw.circle(surface, body_color, (x+40, y+30), 12, 2) # Cabeza
        pygame.draw.lines(surface, body_color, False, [(x+40, y+42), (x+35, y+70), (x+45, y+100)], 3) # Espina
        pygame.draw.line(surface, body_color, (x+35, y+50), (x+15, y+80), 2) # Brazo 1
        pygame.draw.line(surface, body_color, (x+45, y+100), (x+30, y+140), 2) # Pierna 1
        pygame.draw.line(surface, body_color, (x+45, y+100), (x+60, y+140), 2) # Pierna 2
    else:
        # Erguido (Sapiens)
        pygame.draw.circle(surface, body_color, (x+40, y+25), 10, 2) # Cabeza
        pygame.draw.line(surface, body_color, (x+40, y+35), (x+40, y+95), 3) # Espina recta
        pygame.draw.line(surface, body_color, (x+40, y+45), (x+20, y+75), 2) # Brazo 1
        pygame.draw.line(surface, body_color, (x+40, y+45), (x+60, y+75), 2) # Brazo 2
        pygame.draw.line(surface, body_color, (x+40, y+95), (x+30, y+145), 2) # Pierna 1
        pygame.draw.line(surface, body_color, (x+40, y+95), (x+50, y+145), 2) # Pierna 2

    # Equipo Visible
    weapon = player.equipment.get("Weapon")
    if weapon and weapon != "Puños":
        # Dibujar lanza o cuchillo en la mano (x+20, y+75 aprox)
        pygame.draw.line(surface, (100, 70, 40), (x+15, y+60), (x+10, y+110), 2) # Palo
        pygame.draw.polygon(surface, (150, 150, 160), [(x+15, y+50), (x+10, y+65), (x+20, y+65)], 0) # Punta

    body_gear = player.equipment.get("Body")
    if body_gear and body_gear != "Nada":
        # Dibujar túnica/peto
        pygame.draw.rect(surface, (120, 90, 70), (x+30, y+45, 20, 45), 1)
        if "Escamoso" in body_gear:
            for i in range(3):
                pygame.draw.line(surface, (120, 90, 70), (x+30, y+50+i*10), (x+50, y+55+i*10), 1)

    # Feedback de Estado (Heridas)
    if player.hp < player.max_hp * 0.5:
        # Tachones de sangre (tinta roja)
        for _ in range(3):
            rx = x + 30 + (player.turn % 10)
            ry = y + 50 + (player.turn % 20)
            pygame.draw.line(surface, (180, 50, 50), (rx, ry), (rx+15, ry+5), 2)

def draw_blood_splatters(surface, blood_intensity, turn_seed):
    import random
    if blood_intensity <= 0: return
    
    rng = random.Random(turn_seed)
    sw, sh = surface.get_size()
    
    # Manchas de tinta roja procesual
    for _ in range(min(10, blood_intensity // 5)):
        bx = rng.randint(50, sw-50)
        by = rng.randint(50, sh-50)
        size = rng.randint(5, 15)
        
        # Color rojo "tinta vieja"
        s_color = (150, 20, 20, min(180, blood_intensity*2))
        temp_s = pygame.Surface((size*4, size*4), pygame.SRCALPHA)
        pygame.draw.circle(temp_s, s_color, (size*2, size*2), size)
        # Salpicaduras
        for _ in range(3):
            sx = rng.randint(0, size*4)
            sy = rng.randint(0, size*4)
            pygame.draw.circle(temp_s, s_color, (sx, sy), size//3)
            
        surface.blit(temp_s, (bx-size*2, by-size*2))

def draw_bar(surface, x, y, w, h, val, max_val, color, label, font, active=True):
    if not active: return
    pygame.draw.rect(surface, (50, 50, 50), (x, y, w, h))
    fill_w = int((val / max_val) * w)
    pygame.draw.rect(surface, color, (x, y, fill_w, h))
    pygame.draw.rect(surface, (200, 200, 200), (x, y, w, h), 1)
    lbl = font.render(f"{label}: {int(val)}/{int(max_val)}", True, (255, 255, 255))
    surface.blit(lbl, (x, y - 20))

def draw_hallucinations(surface, sanity, seed):
    # Solo aparecen si la sanidad es baja (<60)
    if sanity >= 65: return
    
    import random
    rng = random.Random(seed)
    sw, sh = surface.get_size()
    
    intensity = int((65 - sanity) / 5) # Mas manchas entre mas bajo
    for _ in range(intensity):
        hx = rng.randint(0, sw) if rng.random() < 0.2 else rng.randint(sw-100, sw) # Margenes
        hy = rng.randint(0, sh)
        size = rng.randint(10, 30)
        
        # Manchas tipo "ojo" o "sombra"
        pygame.draw.ellipse(surface, (40, 40, 45, 180), (hx, hy, size*2, size))
        if sanity < 30: # Ojos rojos si esta muy mal
            pygame.draw.circle(surface, (150, 0, 0), (hx+size, hy+size//2), 3)
            
def draw_notebook_bg(surface, time_of_day="Día", ancestral_art=[], blood_intensity=0, turn_seed=0, weather=None, entries=[], font=None, color=(245, 245, 235)):
    sw, sh = surface.get_size()
    
    # Base color (Papel envejecido)
    surface.fill(color)
    
    # Capa 0: Arte Rupestre (Antepasados)
    draw_cave_art(surface, ancestral_art)
    
    # Capa 1: Textura de papel (Líneas muy tenues y manchas)
    for i in range(0, sh, 30):
        pygame.draw.line(surface, (225, 225, 215), (0, i), (sw, i), 1)
        
    # Margen izquierdo (Doble línea roja tenue)
    pygame.draw.line(surface, (220, 170, 170), (70, 0), (70, sh), 1)
    pygame.draw.line(surface, (220, 170, 170), (74, 0), (74, sh), 1)
    
    # Capa 2: Notas de Crónica
    if font and entries:
        draw_chronicle_notes(surface, entries, font)
    
    # Capa 3: Sangre de batalla
    draw_blood_splatters(surface, blood_intensity, turn_seed)
    
    # Capa 4: Efectos de Clima Físico
    if weather:
        draw_paper_weather_fx(surface, weather, turn_seed)
    
    # Capa 5: Encuadernación de Cuero
    draw_notebook_binding(surface)
    
    # Capa 4: Sombra del lomo sobre el papel
    shadow = pygame.Surface((30, sh), pygame.SRCALPHA)
    for x in range(30):
        alpha = int(80 * (1 - x/30))
        pygame.draw.line(shadow, (0, 0, 0, alpha), (x, 0), (x, sh))
    surface.blit(shadow, (60, 0))
    
    # Capa 5: Silueta del Personaje (Esquina Superior Derecha del área de dibujo)
    # player_obj debe pasarse o manejarse en main, pero lo preparamos aquí si se desea
    if time_of_day == "Atardecer":
        tint = pygame.Surface((sw, sh), pygame.SRCALPHA)
        tint.fill((255, 100, 0, 30)) # Naranja tenue
        surface.blit(tint, (0, 0))
    elif time_of_day == "Noche":
        tint = pygame.Surface((sw, sh), pygame.SRCALPHA)
        tint.fill((0, 0, 50, 60)) # Azul oscuro
        surface.blit(tint, (0, 0))
    
    # Bordes "gastados" (Sombra interna)
    pygame.draw.rect(surface, (200, 200, 190), (0, 0, sw, sh), width=10)

def draw_time_icon(surface, x, y, time_of_day, font):
    color = (200, 150, 50) # Sol
    icon_txt = "☀ DÍA"
    if time_of_day == "Atardecer":
        color = (200, 80, 0)
        icon_txt = "🌅 TARDE"
    elif time_of_day == "Noche":
        color = (100, 100, 200)
        icon_txt = "🌙 NOCHE"
        
    txt = font.render(icon_txt, True, color)
    surface.blit(txt, (x, y))

def draw_trophy_sketches(surface, trophies):
    import random
    # Dibujar bocetos permanentes en los margenes (área x < 60 o x > 720)
    # Por simplicidad los pondremos en el margen derecho o inferior
    sw, sh = surface.get_size()
    
    sketch_color = (80, 80, 75)
    
    for idx, t in enumerate(trophies):
        # Posición basada en el índice para que no se encimen
        tx = 750 + (idx % 2) * 80
        ty = 10 + (idx // 2) * 60
        
        if ty > 150: continue # Límite de área para no tapar stats
        
        # Dibujar silueta minimalista (líneas "sucias")
        if "Lobo" in t or "Perro" in t:
            pygame.draw.polygon(surface, sketch_color, [(tx, ty+10), (tx+15, ty), (tx+25, ty+10), (tx+15, ty+20)], 1)
            pygame.draw.line(surface, sketch_color, (tx+5, ty+2), (tx+8, ty-5), 1) # Oreja
        elif "Jaguar" in t or "Puma" in t:
            pygame.draw.circle(surface, sketch_color, (tx+10, ty+10), 10, width=1)
            pygame.draw.circle(surface, sketch_color, (tx+10, ty+10), 2) # Puntos (manchas)
        elif "Búfalo" in t:
            pygame.draw.ellipse(surface, sketch_color, (tx, ty, 30, 20), 1)
            pygame.draw.arc(surface, sketch_color, (tx-5, ty-5, 20, 20), 0, 3.14, 2) # Cuernos
            pygame.draw.arc(surface, sketch_color, (tx+15, ty-5, 20, 20), 0, 3.14, 2)
        elif "Mamut" in t or "Elefante" in t:
            pygame.draw.circle(surface, sketch_color, (tx+15, ty+10), 12, width=1)
            pygame.draw.line(surface, sketch_color, (tx+15, ty+22), (tx+15, ty+35), 2) # Trompa
        elif "Jefe" in t:
            pygame.draw.line(surface, sketch_color, (tx+10, ty), (tx+10, ty+25), 1) # Lanza
            pygame.draw.polygon(surface, sketch_color, [(tx+5, ty+5), (tx+15, ty+5), (tx+10, ty-5)], 1) # Corona/Adorno
def draw_ink_splotches(surface, seed):
    import random
    rng = random.Random(seed)
    sw, sh = surface.get_size()
    
    for _ in range(5):
        ix = rng.randint(0, sw)
        iy = rng.randint(0, sh)
        size = rng.randint(5, 15)
        # Manchas de tinta grisácea/oscura
        points = []
        for i in range(8):
            angle = (i / 8) * 3.14159 * 2
            r = size + rng.randint(-3, 3)
            points.append((ix + r * 3.14159 * 0.1, iy + r * 3.14159 * 0.1)) # Rough circle
            # Actually simpler:
            points.append((ix + r * (i%2+1), iy + r * (i//2%2+1)))
            
        if len(points) > 2:
            # Just small irregular blobs
            pygame.draw.circle(surface, (60, 60, 55), (ix, iy), size, width=0)
            for _ in range(3):
                offset_x = rng.randint(-size, size)
                offset_y = rng.randint(-size, size)
                pygame.draw.circle(surface, (60, 60, 55), (ix + offset_x, iy + offset_y), size // 2)

