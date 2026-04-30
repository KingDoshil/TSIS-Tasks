import pygame
import sys
from datetime import datetime

from tools import (
    PencilTool, LineTool, TextTool,
    flood_fill, BRUSH_SIZES,
)

WIN_W,  WIN_H   = 900, 650
TOOLBAR_H       = 60
CANVAS_TOP      = TOOLBAR_H
CANVAS_RECT     = pygame.Rect(0, CANVAS_TOP, WIN_W, WIN_H - CANVAS_TOP)

WHITE   = (255, 255, 255)
BLACK   = (  0,   0,   0)
GRAY    = (200, 200, 200)
DARK    = ( 50,  50,  50)
RED     = (220,  50,  50)
GREEN   = ( 50, 200,  50)
BLUE    = ( 50,  50, 220)
YELLOW  = (240, 200,   0)
CYAN    = (  0, 200, 220)
MAGENTA = (200,   0, 200)

PALETTE = [BLACK, WHITE, RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA,
           (255,165,0), (128,0,128), (0,128,128), (165,42,42)]

TOOL_PENCIL   = "pencil"
TOOL_LINE     = "line"
TOOL_RECT     = "rect"
TOOL_CIRCLE   = "circle"
TOOL_ERASER   = "eraser"
TOOL_FILL     = "fill"
TOOL_TEXT     = "text"
TOOL_SQUARE   = "square"
TOOL_RTRI     = "rtri"
TOOL_ETRI     = "etri"
TOOL_RHOMBUS  = "rhombus"

ALL_TOOLS = [
    TOOL_PENCIL, TOOL_LINE, TOOL_RECT, TOOL_CIRCLE,
    TOOL_ERASER, TOOL_FILL, TOOL_TEXT,
    TOOL_SQUARE, TOOL_RTRI, TOOL_ETRI, TOOL_RHOMBUS,
]
TOOL_LABELS = {
    TOOL_PENCIL:  "Pencil",
    TOOL_LINE:    "Line",
    TOOL_RECT:    "Rect",
    TOOL_CIRCLE:  "Circle",
    TOOL_ERASER:  "Eraser",
    TOOL_FILL:    "Fill",
    TOOL_TEXT:    "Text",
    TOOL_SQUARE:  "Square",
    TOOL_RTRI:    "R-Tri",
    TOOL_ETRI:    "E-Tri",
    TOOL_RHOMBUS: "Rhombus",
}

def draw_shape(surface, tool, start, end, color, size):
    
    x1, y1 = start
    x2, y2 = end
    rect = pygame.Rect(min(x1,x2), min(y1,y2), abs(x2-x1), abs(y2-y1))

    if tool == TOOL_RECT:
        pygame.draw.rect(surface, color, rect, size)

    elif tool == TOOL_CIRCLE:
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        rx = abs(x2 - x1) // 2
        ry = abs(y2 - y1) // 2
        r  = max(rx, ry)
        pygame.draw.circle(surface, color, (cx, cy), r, size)

    elif tool == TOOL_SQUARE:
        side = max(abs(x2-x1), abs(y2-y1))
        sq   = pygame.Rect(x1, y1, side, side)
        pygame.draw.rect(surface, color, sq, size)

    elif tool == TOOL_RTRI:
        pts = [(x1, y2), (x2, y2), (x1, y1)]
        pygame.draw.polygon(surface, color, pts, size)

    elif tool == TOOL_ETRI:
        import math
        base = abs(x2 - x1)
        h    = int(base * math.sqrt(3) / 2)
        pts  = [(x1, y1 + h), (x2, y1 + h), ((x1+x2)//2, y1)]
        pygame.draw.polygon(surface, color, pts, size)

    elif tool == TOOL_RHOMBUS:
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        pts = [(cx, y1), (x2, cy), (cx, y2), (x1, cy)]
        pygame.draw.polygon(surface, color, pts, size)

def draw_toolbar(screen, font, active_tool, active_color, brush_size):
    pygame.draw.rect(screen, GRAY, (0, 0, WIN_W, TOOLBAR_H))

    swatch = 22
    gap    = 3
    px     = 5
    for i, col in enumerate(PALETTE):
        r = pygame.Rect(px + i*(swatch+gap), 5, swatch, swatch)
        pygame.draw.rect(screen, col, r)
        if col == active_color:
            pygame.draw.rect(screen, BLACK, r, 2)

    preview_r = pygame.Rect(px + len(PALETTE)*(swatch+gap) + 6, 5, 30, 30)
    pygame.draw.rect(screen, active_color, preview_r)
    pygame.draw.rect(screen, BLACK, preview_r, 2)

    bx = WIN_W - 200
    for key, sz in BRUSH_SIZES.items():
        br = pygame.Rect(bx, 8, 36, 22)
        col = DARK if sz == brush_size else GRAY
        txt_col = WHITE if sz == brush_size else BLACK
        pygame.draw.rect(screen, col, br)
        pygame.draw.rect(screen, BLACK, br, 1)
        label = font.render(f"{key}:{sz}px", True, txt_col)
        screen.blit(label, (bx + 2, 12))
        bx += 42

    tx   = 5
    ty   = 35
    tbw  = 62
    tbh  = 20
    for tool in ALL_TOOLS:
        tr = pygame.Rect(tx, ty, tbw, tbh)
        col = DARK if tool == active_tool else GRAY
        tc  = WHITE if tool == active_tool else BLACK
        pygame.draw.rect(screen, col, tr)
        pygame.draw.rect(screen, BLACK, tr, 1)
        lbl = font.render(TOOL_LABELS[tool], True, tc)
        screen.blit(lbl, (tx + 2, ty + 3))
        tx += tbw + 2
        if tx + tbw > WIN_W:
            tx = 5; ty += tbh + 2

def toolbar_click(pos, font, active_tool, active_color, brush_size):
    
    x, y = pos

    swatch = 22; gap = 3; px = 5
    for i, col in enumerate(PALETTE):
        r = pygame.Rect(px + i*(swatch+gap), 5, swatch, swatch)
        if r.collidepoint(x, y):
            return active_tool, col, brush_size

    bx = WIN_W - 200
    for key, sz in BRUSH_SIZES.items():
        br = pygame.Rect(bx, 8, 36, 22)
        if br.collidepoint(x, y):
            return active_tool, active_color, sz
        bx += 42

    tx = 5; ty = 35; tbw = 62; tbh = 20
    for tool in ALL_TOOLS:
        tr = pygame.Rect(tx, ty, tbw, tbh)
        if tr.collidepoint(x, y):
            return tool, active_color, brush_size
        tx += tbw + 2
        if tx + tbw > WIN_W:
            tx = 5; ty += tbh + 2

    return active_tool, active_color, brush_size

def save_canvas(canvas: pygame.Surface):
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"canvas_{ts}.png"
    pygame.image.save(canvas, filename)
    print(f"[TSIS2] Canvas saved → {filename}")
    return filename

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("TSIS 2 – Paint Extended")
    clock  = pygame.font.SysFont("consolas", 11)
    font   = pygame.font.SysFont("consolas", 11)

    canvas = pygame.Surface((WIN_W, WIN_H - CANVAS_TOP))
    canvas.fill(WHITE)

    active_tool  = TOOL_PENCIL
    active_color = BLACK
    brush_size   = BRUSH_SIZES[1]

    pencil = PencilTool()
    liner  = LineTool()
    texter = TextTool()

    shape_drawing = False
    shape_start   = (0, 0)
    canvas_snap   = None

    notif_text = ""
    notif_timer = 0

    running = True
    while running:
        mouse_pos     = pygame.mouse.get_pos()
        canvas_mouse  = (mouse_pos[0], mouse_pos[1] - CANVAS_TOP)
        on_canvas     = CANVAS_RECT.collidepoint(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if texter.active:
                    result = texter.on_key(event)
                    if result == "commit":
                        texter.commit(canvas, active_color)
                else:
                    if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        fname = save_canvas(canvas)
                        notif_text  = f"Saved: {fname}"
                        notif_timer = 180

                    elif event.key == pygame.K_1:
                        brush_size = BRUSH_SIZES[1]
                    elif event.key == pygame.K_2:
                        brush_size = BRUSH_SIZES[2]
                    elif event.key == pygame.K_3:
                        brush_size = BRUSH_SIZES[3]

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not on_canvas:
                    active_tool, active_color, brush_size = toolbar_click(
                        mouse_pos, font, active_tool, active_color, brush_size
                    )
                else:
                    if active_tool == TOOL_PENCIL:
                        pencil.on_mouse_down(canvas_mouse)

                    elif active_tool == TOOL_LINE:
                        liner.on_mouse_down(canvas_mouse)
                        canvas_snap = canvas.copy()

                    elif active_tool == TOOL_FILL:
                        flood_fill(canvas, canvas_mouse, active_color)

                    elif active_tool == TOOL_TEXT:
                        texter.on_click(canvas_mouse)

                    elif active_tool == TOOL_ERASER:
                        pygame.draw.circle(canvas, WHITE, canvas_mouse, brush_size * 3)

                    elif active_tool in (TOOL_RECT, TOOL_CIRCLE, TOOL_SQUARE,
                                         TOOL_RTRI, TOOL_ETRI, TOOL_RHOMBUS):
                        shape_drawing = True
                        shape_start   = canvas_mouse
                        canvas_snap   = canvas.copy()

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if on_canvas or active_tool in (TOOL_LINE,
                                                TOOL_RECT, TOOL_CIRCLE,
                                                TOOL_SQUARE, TOOL_RTRI,
                                                TOOL_ETRI, TOOL_RHOMBUS):
                    if active_tool == TOOL_PENCIL:
                        pencil.on_mouse_up()

                    elif active_tool == TOOL_LINE:
                        liner.on_mouse_up(canvas, canvas_mouse, active_color, brush_size)
                        canvas_snap = None

                    elif shape_drawing:
                        draw_shape(canvas, active_tool,
                                   shape_start, canvas_mouse,
                                   active_color, brush_size)
                        shape_drawing = False
                        canvas_snap   = None

        if pygame.mouse.get_pressed()[0] and on_canvas:
            if active_tool == TOOL_PENCIL:
                pencil.on_mouse_move(canvas, canvas_mouse, active_color, brush_size)
            elif active_tool == TOOL_ERASER:
                pygame.draw.circle(canvas, WHITE, canvas_mouse, brush_size * 3)

        screen.fill(GRAY)

        if (active_tool == TOOL_LINE and liner.active and canvas_snap):
            screen.blit(canvas_snap, CANVAS_RECT.topleft)
            liner.draw_preview(screen, canvas_snap, canvas_mouse,
                               active_color, brush_size, CANVAS_RECT)
        elif (shape_drawing and canvas_snap):
            screen.blit(canvas_snap, CANVAS_RECT.topleft)
            snap_copy = canvas_snap.copy()
            draw_shape(snap_copy, active_tool,
                       shape_start, canvas_mouse,
                       active_color, brush_size)
            screen.blit(snap_copy, CANVAS_RECT.topleft)
        else:
            screen.blit(canvas, CANVAS_RECT.topleft)

        if texter.active:
            tx_screen = (texter.pos[0], texter.pos[1] + CANVAS_TOP)
            orig_pos  = texter.pos
            texter.pos = tx_screen
            texter.draw_preview(screen, active_color)
            texter.pos = orig_pos

        draw_toolbar(screen, font, active_tool, active_color, brush_size)

        if notif_timer > 0:
            notif_timer -= 1
            nf = font.render(notif_text, True, BLACK)
            screen.blit(nf, (WIN_W//2 - nf.get_width()//2, TOOLBAR_H + 8))

        pygame.display.flip()
        pygame.time.Clock().tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
