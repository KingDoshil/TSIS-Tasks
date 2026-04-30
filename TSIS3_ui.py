import pygame
from persistence import load_leaderboard, save_settings

BLACK  = (  0,   0,   0)
WHITE  = (255, 255, 255)
GRAY   = (160, 160, 160)
DARK   = ( 30,  30,  30)
DKGRAY = ( 60,  60,  60)
CYAN   = (  0, 210, 220)
GREEN  = ( 50, 200,  80)
RED    = (220,  50,  50)
YELLOW = (240, 200,   0)
ORANGE = (255, 140,   0)

WIN_W, WIN_H = 480, 700

CAR_COLOR_OPTIONS = [
    ("Blue",   ( 50, 180, 255)),
    ("Red",    (220,  50,  50)),
    ("Green",  ( 50, 200,  80)),
    ("Yellow", (240, 200,   0)),
    ("White",  (240, 240, 240)),
    ("Purple", (160,  50, 220)),
]

DIFFICULTY_OPTIONS = ["easy", "normal", "hard"]

def _draw_button(surface, font, text, rect, active=False,
                 bg=DKGRAY, fg=WHITE, border=CYAN):
    col = border if active else bg
    pygame.draw.rect(surface, col, rect, border_radius=8)
    pygame.draw.rect(surface, border, rect, 2, border_radius=8)
    lbl = font.render(text, True, fg)
    surface.blit(lbl, (rect.centerx - lbl.get_width()//2,
                        rect.centery - lbl.get_height()//2))

def _title(surface, font, text, y, color=CYAN):
    lbl = font.render(text, True, color)
    surface.blit(lbl, (WIN_W//2 - lbl.get_width()//2, y))

def screen_username(surface, clock) -> str:
    
    font_big = pygame.font.SysFont("consolas", 32, bold=True)
    font_med = pygame.font.SysFont("consolas", 22)
    font_sm  = pygame.font.SysFont("consolas", 16)
    name = ""

    while True:
        surface.fill(DARK)
        _title(surface, font_big, "ENTER YOUR NAME", WIN_H//2 - 80)

        box = pygame.Rect(WIN_W//2 - 140, WIN_H//2 - 20, 280, 44)
        pygame.draw.rect(surface, DKGRAY, box, border_radius=6)
        pygame.draw.rect(surface, CYAN, box, 2, border_radius=6)
        display = name + "|"
        lbl = font_med.render(display, True, WHITE)
        surface.blit(lbl, (box.x + 10, box.centery - lbl.get_height()//2))

        hint = font_sm.render("Press Enter to start", True, GRAY)
        surface.blit(hint, (WIN_W//2 - hint.get_width()//2, WIN_H//2 + 40))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 16 and event.unicode.isprintable():
                    name += event.unicode

def screen_main_menu(surface, clock) -> str:
    
    font_big = pygame.font.SysFont("consolas", 38, bold=True)
    font_med = pygame.font.SysFont("consolas", 22)

    buttons = [
        ("Play",        "play"),
        ("Leaderboard", "leaderboard"),
        ("Settings",    "settings"),
        ("Quit",        "quit"),
    ]
    bw, bh = 240, 50
    start_y = WIN_H//2 - 80

    while True:
        surface.fill(DARK)
        _title(surface, font_big, "RACER", 80, CYAN)
        _title(surface, font_med, "TSIS 3", 128, GRAY)

        mx, my = pygame.mouse.get_pos()
        rects  = []
        for i, (label, _) in enumerate(buttons):
            r = pygame.Rect(WIN_W//2 - bw//2,
                            start_y + i*(bh+14), bw, bh)
            rects.append(r)
            hover = r.collidepoint(mx, my)
            _draw_button(surface, font_med, label, r, active=hover)

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, r in enumerate(rects):
                    if r.collidepoint(event.pos):
                        return buttons[i][1]
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "quit"

def screen_settings(surface, clock, settings: dict) -> dict:
    
    font_big = pygame.font.SysFont("consolas", 28, bold=True)
    font_med = pygame.font.SysFont("consolas", 20)
    font_sm  = pygame.font.SysFont("consolas", 15)

    s = dict(settings)

    while True:
        surface.fill(DARK)
        _title(surface, font_big, "SETTINGS", 30)

        mx, my = pygame.mouse.get_pos()
        clickable = []

        y = 100
        lbl = font_med.render("Sound:", True, WHITE)
        surface.blit(lbl, (60, y))
        sr = pygame.Rect(220, y, 120, 36)
        on = s["sound"]
        _draw_button(surface, font_med,
                     "ON" if on else "OFF", sr,
                     bg=GREEN if on else DKGRAY)
        clickable.append(("sound", sr))

        y = 170
        lbl = font_med.render("Car color:", True, WHITE)
        surface.blit(lbl, (60, y))
        for i, (cname, cval) in enumerate(CAR_COLOR_OPTIONS):
            cr = pygame.Rect(60 + i*60, y+40, 50, 30)
            active = (tuple(s["car_color"]) == tuple(cval))
            pygame.draw.rect(surface, cval, cr, border_radius=5)
            if active:
                pygame.draw.rect(surface, WHITE, cr, 3, border_radius=5)
            lc = font_sm.render(cname[:3], True, WHITE)
            surface.blit(lc, (cr.x+2, cr.y+7))
            clickable.append(("color_" + cname, cr))

        y = 290
        lbl = font_med.render("Difficulty:", True, WHITE)
        surface.blit(lbl, (60, y))
        for i, d in enumerate(DIFFICULTY_OPTIONS):
            dr = pygame.Rect(60 + i*120, y+40, 110, 36)
            active = (s["difficulty"] == d)
            col    = {"easy": GREEN, "normal": YELLOW,
                      "hard": RED}[d]
            _draw_button(surface, font_med, d.capitalize(), dr,
                         bg=col if active else DKGRAY,
                         border=col)
            clickable.append(("diff_" + d, dr))

        back_r = pygame.Rect(WIN_W//2-100, WIN_H-90, 200, 48)
        hover  = back_r.collidepoint(mx, my)
        _draw_button(surface, font_med, "Save & Back", back_r, active=hover)
        clickable.append(("back", back_r))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_settings(s); return s
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                save_settings(s); return s
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for tag, r in clickable:
                    if r.collidepoint(event.pos):
                        if tag == "sound":
                            s["sound"] = not s["sound"]
                        elif tag.startswith("color_"):
                            cname = tag[6:]
                            for cn, cv in CAR_COLOR_OPTIONS:
                                if cn == cname:
                                    s["car_color"] = list(cv)
                        elif tag.startswith("diff_"):
                            s["difficulty"] = tag[5:]
                        elif tag == "back":
                            save_settings(s)
                            return s

def screen_game_over(surface, clock,
                     score: int, distance: int, coins: int) -> str:
    
    font_big = pygame.font.SysFont("consolas", 36, bold=True)
    font_med = pygame.font.SysFont("consolas", 22)

    bw, bh = 200, 48
    retry_r = pygame.Rect(WIN_W//2 - bw - 10, WIN_H//2 + 80, bw, bh)
    menu_r  = pygame.Rect(WIN_W//2 + 10,       WIN_H//2 + 80, bw, bh)

    while True:
        surface.fill(DARK)
        _title(surface, font_big, "GAME OVER", WIN_H//2 - 120, RED)

        stats = [
            f"Score:    {score}",
            f"Distance: {distance}m",
            f"Coins:    {coins}",
        ]
        for i, st in enumerate(stats):
            lbl = font_med.render(st, True, WHITE)
            surface.blit(lbl, (WIN_W//2 - lbl.get_width()//2,
                                WIN_H//2 - 50 + i*32))

        mx, my = pygame.mouse.get_pos()
        _draw_button(surface, font_med, "Retry",
                     retry_r, active=retry_r.collidepoint(mx, my),
                     border=GREEN)
        _draw_button(surface, font_med, "Main Menu",
                     menu_r,  active=menu_r.collidepoint(mx, my),
                     border=CYAN)

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "menu"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if retry_r.collidepoint(event.pos): return "retry"
                if menu_r.collidepoint(event.pos):  return "menu"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: return "retry"
                if event.key == pygame.K_ESCAPE: return "menu"

def screen_leaderboard(surface, clock):
    
    font_big  = pygame.font.SysFont("consolas", 28, bold=True)
    font_med  = pygame.font.SysFont("consolas", 19)
    font_sm   = pygame.font.SysFont("consolas", 15)

    back_r = pygame.Rect(WIN_W//2-80, WIN_H-80, 160, 44)
    board  = load_leaderboard()

    while True:
        surface.fill(DARK)
        _title(surface, font_big, "LEADERBOARD", 28)

        header = font_sm.render(
            f"{'#':<3} {'Name':<14} {'Score':>7} {'Dist':>6} {'Coins':>6}",
            True, CYAN)
        surface.blit(header, (20, 78))
        pygame.draw.line(surface, CYAN, (20, 98), (WIN_W-20, 98), 1)

        for i, entry in enumerate(board[:10]):
            rank  = i + 1
            name  = entry.get("name", "?")[:13]
            score = entry.get("score", 0)
            dist  = entry.get("distance", 0)
            coins = entry.get("coins", 0)
            color = YELLOW if rank == 1 else (GRAY if rank > 3 else WHITE)
            row   = font_med.render(
                f"{rank:<3} {name:<14} {score:>7} {dist:>5}m {coins:>5}",
                True, color)
            surface.blit(row, (20, 106 + i*34))

        if not board:
            empty = font_med.render("No scores yet.", True, GRAY)
            surface.blit(empty, (WIN_W//2 - empty.get_width()//2, 200))

        mx, my = pygame.mouse.get_pos()
        _draw_button(surface, font_med, "Back", back_r,
                     active=back_r.collidepoint(mx, my))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_r.collidepoint(event.pos):
                    return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
