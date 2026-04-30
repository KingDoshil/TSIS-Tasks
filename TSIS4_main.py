import pygame
import sys
import json
import os

from game import GameWorld, WIN_W, WIN_H, UP, DOWN, LEFT, RIGHT
from db   import init_db, save_result, get_top10, get_personal_best

SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "snake_color": [50, 200, 80],
    "grid":        False,
    "sound":       True,
}

def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, encoding="utf-8") as f:
                data = json.load(f)
            for k, v in DEFAULT_SETTINGS.items():
                data.setdefault(k, v)
            return data
        except Exception:
            pass
    return dict(DEFAULT_SETTINGS)

def save_settings(s: dict):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(s, f, indent=2)

BLACK  = (  0,   0,   0)
WHITE  = (255, 255, 255)
DARK   = ( 20,  20,  20)
DKGRAY = ( 50,  50,  50)
GRAY   = (130, 130, 130)
GREEN  = ( 50, 200,  80)
RED    = (220,  50,  50)
CYAN   = (  0, 210, 220)
YELLOW = (240, 200,   0)
ORANGE = (255, 140,   0)
PURPLE = (160,  50, 220)

COLOR_OPTIONS = [
    ("Green",  ( 50, 200,  80)),
    ("Blue",   ( 50, 120, 220)),
    ("Yellow", (240, 200,   0)),
    ("White",  (230, 230, 230)),
    ("Orange", (255, 140,   0)),
    ("Purple", (160,  50, 220)),
]

def _btn(surface, font, text, rect, hover=False,
         bg=DKGRAY, fg=WHITE, border=CYAN):
    pygame.draw.rect(surface, border if hover else bg,
                     rect, border_radius=8)
    pygame.draw.rect(surface, border, rect, 2, border_radius=8)
    lbl = font.render(text, True, fg)
    surface.blit(lbl, (rect.centerx - lbl.get_width()//2,
                        rect.centery - lbl.get_height()//2))

def _title(surface, font, text, y, color=CYAN):
    lbl = font.render(text, True, color)
    surface.blit(lbl, (WIN_W//2 - lbl.get_width()//2, y))

def screen_username(surface, clock) -> str:
    font_big = pygame.font.SysFont("consolas", 30, bold=True)
    font_med = pygame.font.SysFont("consolas", 20)
    font_sm  = pygame.font.SysFont("consolas", 14)
    name = ""

    while True:
        surface.fill(DARK)
        _title(surface, font_big, "ENTER USERNAME", WIN_H//2 - 70)

        box = pygame.Rect(WIN_W//2 - 120, WIN_H//2 - 18, 240, 40)
        pygame.draw.rect(surface, DKGRAY, box, border_radius=6)
        pygame.draw.rect(surface, CYAN, box, 2, border_radius=6)
        lbl = font_med.render(name + "|", True, WHITE)
        surface.blit(lbl, (box.x+8, box.centery - lbl.get_height()//2))

        hint = font_sm.render("Press Enter to continue", True, GRAY)
        surface.blit(hint, (WIN_W//2 - hint.get_width()//2, WIN_H//2 + 36))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 16 and event.unicode.isprintable():
                    name += event.unicode

def screen_main_menu(surface, clock, username: str) -> str:
    font_big = pygame.font.SysFont("consolas", 36, bold=True)
    font_med = pygame.font.SysFont("consolas", 20)
    font_sm  = pygame.font.SysFont("consolas", 14)

    buttons = [
        ("Play",        "play"),
        ("Leaderboard", "leaderboard"),
        ("Settings",    "settings"),
        ("Quit",        "quit"),
    ]
    bw, bh  = 220, 46
    start_y = WIN_H//2 - 70

    while True:
        surface.fill(DARK)
        _title(surface, font_big, "SNAKE", 60, GREEN)

        user_lbl = font_sm.render(f"Player: {username}", True, GRAY)
        surface.blit(user_lbl, (WIN_W//2 - user_lbl.get_width()//2, 106))

        mx, my = pygame.mouse.get_pos()
        rects  = []
        for i, (label, _) in enumerate(buttons):
            r = pygame.Rect(WIN_W//2 - bw//2,
                            start_y + i*(bh+12), bw, bh)
            rects.append(r)
            _btn(surface, font_med, label, r,
                 hover=r.collidepoint(mx, my))

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

def screen_game_over(surface, clock,
                     score: int, level: int, personal_best: int) -> str:
    font_big = pygame.font.SysFont("consolas", 32, bold=True)
    font_med = pygame.font.SysFont("consolas", 20)

    bw, bh  = 180, 44
    retry_r = pygame.Rect(WIN_W//2 - bw - 8, WIN_H//2 + 70, bw, bh)
    menu_r  = pygame.Rect(WIN_W//2 + 8,       WIN_H//2 + 70, bw, bh)

    while True:
        surface.fill(DARK)
        _title(surface, font_big, "GAME OVER", WIN_H//2 - 110, RED)

        stats = [
            f"Score:         {score}",
            f"Level reached: {level}",
            f"Personal best: {personal_best}",
        ]
        for i, s in enumerate(stats):
            col = YELLOW if "best" in s else WHITE
            lbl = font_med.render(s, True, col)
            surface.blit(lbl, (WIN_W//2 - lbl.get_width()//2,
                                WIN_H//2 - 40 + i*30))

        mx, my = pygame.mouse.get_pos()
        _btn(surface, font_med, "Retry",
             retry_r, hover=retry_r.collidepoint(mx, my), border=GREEN)
        _btn(surface, font_med, "Main Menu",
             menu_r,  hover=menu_r.collidepoint(mx, my),  border=CYAN)

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "menu"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if retry_r.collidepoint(event.pos): return "retry"
                if menu_r.collidepoint(event.pos):  return "menu"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:      return "retry"
                if event.key == pygame.K_ESCAPE: return "menu"

def screen_leaderboard(surface, clock):
    font_big = pygame.font.SysFont("consolas", 26, bold=True)
    font_med = pygame.font.SysFont("consolas", 17)
    font_sm  = pygame.font.SysFont("consolas", 13)

    back_r = pygame.Rect(WIN_W//2-70, WIN_H - 64, 140, 40)

    try:
        board = get_top10()
    except Exception:
        board = []

    while True:
        surface.fill(DARK)
        _title(surface, font_big, "LEADERBOARD", 20)

        header = font_sm.render(
            f"{'#':<3} {'Username':<14} {'Score':>6} {'Lvl':>4} {'Date':<12}",
            True, CYAN)
        surface.blit(header, (14, 58))
        pygame.draw.line(surface, CYAN, (14, 76), (WIN_W-14, 76), 1)

        for i, e in enumerate(board[:10]):
            rank  = e.get("rank", i+1)
            name  = str(e.get("username", "?"))[:13]
            sc    = e.get("score", 0)
            lv    = e.get("level_reached", 0)
            dt    = str(e.get("played_at", ""))[:10]
            col   = YELLOW if rank == 1 else (GRAY if rank > 3 else WHITE)
            row   = font_med.render(
                f"{rank:<3} {name:<14} {sc:>6} {lv:>4} {dt}", True, col)
            surface.blit(row, (14, 84 + i*32))

        if not board:
            empty = font_med.render("No scores yet.", True, GRAY)
            surface.blit(empty, (WIN_W//2 - empty.get_width()//2, 160))

        mx, my = pygame.mouse.get_pos()
        _btn(surface, font_med, "Back", back_r,
             hover=back_r.collidepoint(mx, my))

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

def screen_settings(surface, clock, settings: dict) -> dict:
    font_big = pygame.font.SysFont("consolas", 26, bold=True)
    font_med = pygame.font.SysFont("consolas", 18)
    font_sm  = pygame.font.SysFont("consolas", 13)

    s = dict(settings)

    while True:
        surface.fill(DARK)
        _title(surface, font_big, "SETTINGS", 24)

        mx, my   = pygame.mouse.get_pos()
        clickable = []

        y = 80
        lbl = font_med.render("Snake color:", True, WHITE)
        surface.blit(lbl, (20, y))
        for i, (cname, cval) in enumerate(COLOR_OPTIONS):
            cr = pygame.Rect(20 + i*74, y+30, 66, 28)
            active = (tuple(s["snake_color"]) == tuple(cval))
            pygame.draw.rect(surface, cval, cr, border_radius=5)
            if active:
                pygame.draw.rect(surface, WHITE, cr, 3, border_radius=5)
            cl = font_sm.render(cname[:5], True, BLACK)
            surface.blit(cl, (cr.x+3, cr.y+6))
            clickable.append(("color_" + cname, cr))

        y = 170
        lbl = font_med.render("Grid overlay:", True, WHITE)
        surface.blit(lbl, (20, y))
        gr = pygame.Rect(200, y, 100, 34)
        on = s["grid"]
        _btn(surface, font_med, "ON" if on else "OFF", gr,
             bg=GREEN if on else DKGRAY)
        clickable.append(("grid", gr))

        y = 224
        lbl = font_med.render("Sound:", True, WHITE)
        surface.blit(lbl, (20, y))
        sr = pygame.Rect(200, y, 100, 34)
        on2 = s["sound"]
        _btn(surface, font_med, "ON" if on2 else "OFF", sr,
             bg=GREEN if on2 else DKGRAY)
        clickable.append(("sound", sr))

        back_r = pygame.Rect(WIN_W//2-90, WIN_H-80, 180, 44)
        _btn(surface, font_med, "Save & Back", back_r,
             hover=back_r.collidepoint(mx, my))
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
                        if tag.startswith("color_"):
                            cname = tag[6:]
                            for cn, cv in COLOR_OPTIONS:
                                if cn == cname:
                                    s["snake_color"] = list(cv)
                        elif tag == "grid":
                            s["grid"] = not s["grid"]
                        elif tag == "sound":
                            s["sound"] = not s["sound"]
                        elif tag == "back":
                            save_settings(s)
                            return s

def run_game(screen, clock, username: str, settings: dict) -> tuple:
    
    pb    = 0
    try:
        pb = get_personal_best(username)
    except Exception:
        pass

    world = GameWorld(settings, personal_best=pb)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if   event.key == pygame.K_UP    or event.key == pygame.K_w:
                    world.snake.change_dir(UP)
                elif event.key == pygame.K_DOWN  or event.key == pygame.K_s:
                    world.snake.change_dir(DOWN)
                elif event.key == pygame.K_LEFT  or event.key == pygame.K_a:
                    world.snake.change_dir(LEFT)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    world.snake.change_dir(RIGHT)
                elif event.key == pygame.K_ESCAPE:
                    return world.score, world.level

        result = world.update()
        world.draw(screen)
        pygame.display.flip()
        clock.tick(120)

        if result == "dead":
            return world.score, world.level

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("TSIS 4 – Snake")
    clock    = pygame.time.Clock()
    settings = load_settings()

    try:
        init_db()
    except Exception as e:
        print(f"[DB] Could not connect: {e}")

    username = screen_username(screen, clock)

    while True:
        action = screen_main_menu(screen, clock, username)

        if action == "quit":
            pygame.quit(); sys.exit()

        elif action == "leaderboard":
            screen_leaderboard(screen, clock)

        elif action == "settings":
            settings = screen_settings(screen, clock, settings)

        elif action == "play":
            score, level = run_game(screen, clock, username, settings)

            try:
                save_result(username, score, level)
                pb = get_personal_best(username)
            except Exception as e:
                print(f"[DB] Save failed: {e}")
                pb = score

            result = screen_game_over(screen, clock, score, level, pb)
            if result == "retry":
                score, level = run_game(screen, clock, username, settings)
                try:
                    save_result(username, score, level)
                except Exception:
                    pass

if __name__ == "__main__":
    main()
