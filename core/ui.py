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

# draw_bar consolidated at the end of the file to avoid redundancy

def draw_text_box(surface, text, x, y, width, height, font, bg_color=(240, 240, 240, 200), text_color=(25, 30, 45), alpha=255):
    # Efecto "Ink Soak": El texto aparece gradualmente
    rect = pygame.Rect(x, y, width, height)
    
    # Fondo del cuadro con transparencia suave
    bg_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(bg_surface, bg_color, (0, 0, width, height), border_radius=8)
    # Borde "trazado a mano"
    pygame.draw.rect(bg_surface, (50, 50, 55, 100), (0, 0, width, height), width=2, border_radius=8)
    surface.blit(bg_surface, (x, y))
    
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] < width - 40:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)
    
    yy = y + 20
    for line in lines:
        if line:
            # Render con Alpha dinámico (Simula tinta secándose)
            txt_surf = font.render(line, True, text_color)
            if alpha < 255:
                txt_surf.set_alpha(alpha)
                # Pequeño desenfoque/sombra si la tinta está "fresca"
                if alpha < 180:
                    shadow = font.render(line, True, (text_color[0], text_color[1], text_color[2], 50))
                    surface.blit(shadow, (x+21, yy+1))
            surface.blit(txt_surf, (x + 20, yy))
        yy += font.get_linesize()

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
    p_center_x = x + px * cell_px + cell_px // 2
    p_center_y = y + py * cell_px + cell_px // 2
    p_rect = pygame.Rect(p_center_x - cell_px // 2, p_center_y - cell_px // 2, cell_px, cell_px)
    
    # Silueta de cazador esquemático
    pygame.draw.line(surface, (50, 50, 55), (p_rect.centerx, p_rect.top+2), (p_rect.centerx, p_rect.bottom-2), 2) # Cuerpo
    pygame.draw.line(surface, (50, 50, 55), (p_rect.left, p_rect.centery), (p_rect.right, p_rect.centery), 1) # Brazos
    pygame.draw.circle(surface, (50, 50, 55), (p_rect.centerx, p_rect.top+4), 3) # Cabeza
    pygame.draw.line(surface, (120, 80, 20), (p_rect.right, p_rect.top), (p_rect.left, p_rect.bottom), 1) # Lanza

def draw_chronicle_notes(surface, entries, font):
    # Notas al margen, con word-wrap y algo inclinadas
    if not entries: return
    sw, sh = surface.get_size()
    color = (40, 50, 80, 160) # Azul tinta tenue
    
    max_w = 250
    y_offset = 150
    
    for entry in entries:
        # Word wrapping simple
        words = entry.split(' ')
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] < max_w:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))
        
        for line in lines:
            if y_offset > sh - 100: break
            txt_surf = font.render(line, True, color)
            # Rotar ligeramente cada línea de forma distinta para toque humano
            import random
            rot = random.Random(hash(line)).randint(-2, 2)
            txt_surf = pygame.transform.rotate(txt_surf, rot)
            surface.blit(txt_surf, (sw - 300, y_offset))
            y_offset += 25
        y_offset += 15 # Espacio entre entradas completas

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
        elif art == "fire":
            pygame.draw.polygon(surface, art_color, [(150, sh-100), (170, sh-140), (190, sh-100)], 0)
        elif art == "tame":
            pygame.draw.circle(surface, art_color, (sw-100, sh-100), 15, 2)
            pygame.draw.circle(surface, art_color, (sw-130, sh-100), 8, 2)

CHAR_ASSETS = {}

def draw_character_profile(surface, player, x, y):
    # Imagen de alta fidelidad (Boceto arqueológico con transparencia mejorada)
    era_key = f"era{player.era}"
    if era_key not in CHAR_ASSETS:
        path = f"assets/char_{era_key}.png"
        try:
            # Cargar con convert_alpha para manejo real de transparencia
            img = pygame.image.load(path).convert_alpha()
            # Escalar PRIMERO para manejar el anti-aliasing resultante
            img = pygame.transform.smoothscale(img, (160, 180))
            
            # Filtro manual de umbral (Eliminar fondo blanco/grisáceo)
            for i in range(img.get_width()):
                for j in range(img.get_height()):
                    c = img.get_at((i, j))
                    # Umbral más agresivo (>180) para limpiar bordes sucios tras el escalado
                    if c.r > 180 and c.g > 180 and c.b > 180:
                        img.set_at((i, j), (0, 0, 0, 0))
            
            CHAR_ASSETS[era_key] = img
        except:
            # Fallback a un círculo si falla la carga
            pygame.draw.circle(surface, (50, 50, 50), (x+80, y+90), 30)
            return

    # Dibujar la base del personaje
    surface.blit(CHAR_ASSETS[era_key], (x, y))

    # Renderizado común de equipo (estilo adaptado)
    wp = player.equipment.get("Weapon")
    if wp and wp != "Puños":
        # Posición relativa a la mano del dibujo (ajustada a la imagen 160x180)
        hx, hy = x + 30, y + 100
        pygame.draw.line(surface, (80, 60, 40), (hx, hy), (hx-10, hy+40), 4) # Mango
        tip_c = (30, 30, 30) if "Obsidiana" in wp else (180, 180, 160)
        pygame.draw.polygon(surface, tip_c, [(hx, hy-10), (hx-10, hy+5), (hx+10, hy+5)]) # Punta

    # Heridas de Tinta Roja (Visualmente integradas)
    if player.hp < player.max_hp * 0.5:
        # Tachones de sangre en el torso del dibujo
        for i in range(3):
            pygame.draw.line(surface, (150, 20, 20), (x+60, y+70+i*10), (x+100, y+80+i*10), 3)

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

def draw_bar(surface, x, y, width, height, value, max_value, color, label, font):
    # Consolidación final: Fondo, Relleno, Contorno y Etiqueta Negra
    # Fondo (Gris suave para que no resalte demasiado sobre el papel)
    bg_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, (210, 210, 210), bg_rect, border_radius=4)
    
    # Relleno de la barra (Color basado en el tipo de stat)
    ratio = max(0.0, min(1.0, value / (max_value if max_value > 0 else 1)))
    fill_width = int(width * ratio)
    if fill_width > 0:
        fill_rect = pygame.Rect(x, y, fill_width, height)
        pygame.draw.rect(surface, color, fill_rect, border_radius=4)
        
    # Contorno "Ink-style" sutil
    pygame.draw.rect(surface, (50, 50, 55), bg_rect, width=1, border_radius=4)
    
    # Etiqueta de texto de la estadística (NEGRO para legibilidad)
    label_txt = f"{label}: {int(value)}/{int(max_value)}"
    label_surf = font.render(label_txt, True, (25, 30, 45))
    surface.blit(label_surf, (x, y - 22))

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
            
def draw_ambient_flicker(surface, time_ticks):
    # Capa de luz de fogata (warm orange glow)
    import math
    sw, sh = surface.get_size()
    flicker = 15 + int(math.sin(time_ticks / 200) * 10) + int(math.cos(time_ticks / 500) * 5)
    
    # Overlay sutil en los bordes
    overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
    # Gradiente radial o esquinas (más eficiente)
    glow_color = (255, 160, 50, flicker)
    # Solo en las esquinas para no saturar el centro
    pygame.draw.circle(overlay, glow_color, (0, 0), 150)
    pygame.draw.circle(overlay, glow_color, (sw, 0), 100)
    pygame.draw.circle(overlay, glow_color, (0, sh), 200)
    pygame.draw.circle(overlay, glow_color, (sw, sh), 120)
    surface.blit(overlay, (0, 0))

def draw_discovery_sketches(surface, discoveries):
    # Bocetos en el margen izquierdo conforme descubrimos la era
    sketch_color = (40, 40, 45, 120)
    for idx, d in enumerate(discoveries):
        dx = 20 + (idx % 2) * 25
        dy = 250 + (idx // 2) * 50
        if dy > 600: continue
        
        # Dibujos simples icónicos
        if "Fuego" in d or "fire" in d:
             pygame.draw.polygon(surface, sketch_color, [(dx, dy+15), (dx+10, dy), (dx+20, dy+15)], 1)
             pygame.draw.line(surface, sketch_color, (dx+10, dy+5), (dx+10, dy+15), 1)
        elif "Herramientas" in d:
             pygame.draw.line(surface, sketch_color, (dx, dy), (dx+20, dy+20), 1)
             pygame.draw.polygon(surface, sketch_color, [(dx+15, dy+15), (dx+25, dy+25), (dx+15, dy+25)], 1)
        elif "Puntería" in d or "Arco" in d:
             pygame.draw.arc(surface, sketch_color, (dx, dy, 20, 30), -1.5, 1.5, 1)
             pygame.draw.line(surface, sketch_color, (dx+10, dy), (dx+10, dy+30), 1)

def draw_notebook_bg(surface, time_now, ancestral_art, blood_intensity, turn, weather_active, entries, font, discoveries=[]):
    sw, sh = surface.get_size()
    
    # Base color (Papel envejecido - Tono hueso)
    color = (245, 245, 235)
    surface.fill(color)
    
    # Arte Rupestre
    draw_cave_art(surface, ancestral_art)
    
    # Líneas de libreta (Ink style sutil)
    for i in range(0, sh, 30):
        pygame.draw.line(surface, (225, 225, 215), (0, i), (sw, i), 1)
        
    # Margen izquierdo (Doble línea roja tenue)
    pygame.draw.line(surface, (230, 180, 180, 120), (70, 0), (70, sh), 1)
    pygame.draw.line(surface, (230, 180, 180, 120), (74, 0), (74, sh), 1)
    
    # Bocetos de descubrimiento en los márgenes
    draw_discovery_sketches(surface, discoveries)
    
    # Capa 3: Sangre y Trophies
    draw_chronicle_notes(surface, entries, font)
    draw_blood_splatters(surface, blood_intensity, turn)
    draw_trophy_sketches(surface, []) # Aquí irían trofeos de caza
    
    # Clima
    if weather_active:
        draw_paper_weather_fx(surface, weather_active, turn)
    
    # Encuadernación y Lomo
    draw_notebook_binding(surface)
    
    # Sombra del lomo
    shadow = pygame.Surface((30, sh), pygame.SRCALPHA)
    for x in range(30):
        alpha = int(100 * (1 - x/30)) # Sombra más intensa cerca del lomo
        pygame.draw.line(shadow, (0, 0, 0, alpha), (x, 0), (x, sh))
    surface.blit(shadow, (60, 0))
    
    # Esquina doblada animada (Paper Corner)
    import math
    corner_w = 40
    # Wiggle sutil basado en el turno
    wiggle = math.sin(turn * 0.5) * 5
    corner_points = [(sw, sh), (sw - corner_w + wiggle, sh), (sw, sh - corner_w - wiggle)]
    pygame.draw.polygon(surface, (220, 220, 210), corner_points)
    pygame.draw.polygon(surface, (150, 150, 140), corner_points, 1) # Borde de la sombra de la esquina
    
    # Tintes de hora del día
    if time_now == "Atardecer":
        tint = pygame.Surface((sw, sh), pygame.SRCALPHA)
        tint.fill((255, 100, 0, 35))
        surface.blit(tint, (0, 0))
    elif time_now == "Noche":
        tint = pygame.Surface((sw, sh), pygame.SRCALPHA)
        tint.fill((0, 0, 50, 75))
        surface.blit(tint, (0, 0))
    
    # Iluminación de hoguera (Premium Ambience)
    draw_ambient_flicker(surface, pygame.time.get_ticks())
    
    # Bordes "gastados"
    pygame.draw.rect(surface, (210, 210, 200), (0, 0, sw, sh), width=4)

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

