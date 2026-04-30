import pygame
from collections import deque

BRUSH_SIZES = {1: 2, 2: 5, 3: 10}

class PencilTool:
    def __init__(self):
        self.drawing  = False
        self.last_pos = None

    def on_mouse_down(self, pos):
        self.drawing  = True
        self.last_pos = pos

    def on_mouse_move(self, surface, pos, color, size):
        if self.drawing and self.last_pos:
            pygame.draw.line(surface, color, self.last_pos, pos, size)
            pygame.draw.circle(surface, color, pos, size // 2)
        self.last_pos = pos

    def on_mouse_up(self):
        self.drawing  = False
        self.last_pos = None

class LineTool:
    def __init__(self):
        self.active    = False
        self.start_pos = None

    def on_mouse_down(self, pos):
        self.active    = True
        self.start_pos = pos

    def draw_preview(self, display_surface, canvas_snapshot,
                     current_pos, color, size, canvas_rect):
        
        display_surface.blit(canvas_snapshot, canvas_rect.topleft)
        if self.active and self.start_pos:
            pygame.draw.line(display_surface, color,
                             self.start_pos, current_pos, size)

    def on_mouse_up(self, surface, pos, color, size):
        
        if self.active and self.start_pos:
            pygame.draw.line(surface, color, self.start_pos, pos, size)
        self.active    = False
        self.start_pos = None

def flood_fill(surface: pygame.Surface, pos: tuple,
               fill_color: tuple):
    
    x0, y0 = int(pos[0]), int(pos[1])
    w, h   = surface.get_size()

    if not (0 <= x0 < w and 0 <= y0 < h):
        return

    target = surface.get_at((x0, y0))[:3]
    fill   = fill_color[:3]

    if target == fill:
        return

    surface.lock()
    queue   = deque()
    queue.append((x0, y0))
    visited = set()
    visited.add((x0, y0))

    while queue:
        cx, cy = queue.popleft()
        surface.set_at((cx, cy), fill)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = cx + dx, cy + dy
            if (0 <= nx < w and 0 <= ny < h
                    and (nx, ny) not in visited
                    and surface.get_at((nx, ny))[:3] == target):
                visited.add((nx, ny))
                queue.append((nx, ny))

    surface.unlock()

class TextTool:
    FONT_SIZE = 24

    def __init__(self):
        self.active   = False
        self.pos      = (0, 0)
        self.text     = ""
        self._font    = None

    def _get_font(self):
        if self._font is None:
            self._font = pygame.font.SysFont("monospace", self.FONT_SIZE)
        return self._font

    def on_click(self, pos):
        
        self.active = True
        self.pos    = pos
        self.text   = ""

    def on_key(self, event):
        
        if not self.active:
            return None
        if event.key == pygame.K_RETURN:
            return "commit"
        elif event.key == pygame.K_ESCAPE:
            self.active = False
            self.text   = ""
            return "cancel"
        elif event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        else:
            ch = event.unicode
            if ch and ch.isprintable():
                self.text += ch
        return "typing"

    def commit(self, surface, color):
        
        if self.text:
            font    = self._get_font()
            rendered = font.render(self.text, True, color)
            surface.blit(rendered, self.pos)
        self.active = False
        self.text   = ""

    def draw_preview(self, display_surface, color):
        
        if not self.active:
            return
        font      = self._get_font()
        preview   = self.text + "|"
        rendered  = font.render(preview, True, color)
        display_surface.blit(rendered, self.pos)
