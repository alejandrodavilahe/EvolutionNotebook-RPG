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
                    
    # Draw Player Avatar/Dot on Map
    p_rect = (x + px * cell_px + cell_px//2, y + py * cell_px + cell_px//2)
    pygame.draw.circle(surface, (250, 100, 100), p_rect, cell_px//2 - 2)
    pygame.draw.circle(surface, (255, 255, 255), p_rect, cell_px//2 - 2, width=1)

