import pygame
import random

WIN_W, WIN_H = 480, 700
ROAD_LEFT    = 80
ROAD_RIGHT   = 400
ROAD_W       = ROAD_RIGHT - ROAD_LEFT
NUM_LANES    = 4
LANE_W       = ROAD_W // NUM_LANES

def lane_cx(lane: int) -> int:
    
    return ROAD_LEFT + lane * LANE_W + LANE_W // 2

PLAYER_W, PLAYER_H = 36, 60
TRAFFIC_W, TRAFFIC_H = 36, 60

BLACK   = (  0,   0,   0)
WHITE   = (255, 255, 255)
GRAY    = (100, 100, 100)
DKGRAY  = ( 40,  40,  40)
ROAD_C  = ( 60,  60,  60)
LINE_C  = (200, 200,   0)
RED     = (220,  50,  50)
GREEN   = ( 50, 200,  80)
BLUE    = ( 50, 120, 220)
YELLOW  = (240, 200,   0)
ORANGE  = (255, 140,   0)
CYAN    = (  0, 210, 220)
PURPLE  = (160,  50, 220)
OIL_C   = ( 30,  30,  80)
NITRO_C = (  0, 240, 200)
BUMP_C  = (180,  80,  20)
BARRIER_C = (220, 60, 60)

DIFFICULTY = {
    "easy":   {"traffic_freq": 140, "obstacle_freq": 200, "base_speed": 4},
    "normal": {"traffic_freq": 100, "obstacle_freq": 150, "base_speed": 5},
    "hard":   {"traffic_freq":  70, "obstacle_freq": 100, "base_speed": 7},
}

PU_NITRO  = "nitro"
PU_SHIELD = "shield"
PU_REPAIR = "repair"
PU_TIMEOUT = 300
NITRO_DURATION = 240

class Player:
    def __init__(self, color=(50, 180, 255)):
        self.lane  = 1
        self.x     = float(lane_cx(self.lane))
        self.y     = WIN_H - 120
        self.color = color
        self.speed = 0
        self.alive = True

        self.active_pu   = None
        self.pu_timer    = 0
        self.nitro_bonus = 0
        self.shielded    = False
        self.crashes     = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x) - PLAYER_W//2,
                           int(self.y) - PLAYER_H//2,
                           PLAYER_W, PLAYER_H)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        target_x = float(lane_cx(self.lane))
        dx = target_x - self.x
        self.x += dx * 0.18

    def move_left(self):
        if self.lane > 0:
            self.lane -= 1

    def move_right(self):
        if self.lane < NUM_LANES - 1:
            self.lane += 1

    def collect_powerup(self, pu_type: str):
        self.active_pu = pu_type
        if pu_type == PU_NITRO:
            self.pu_timer    = NITRO_DURATION
            self.nitro_bonus = 4
        elif pu_type == PU_SHIELD:
            self.pu_timer = 0
            self.shielded = True
        elif pu_type == PU_REPAIR:
            self.crashes  = max(0, self.crashes - 1)
            self.active_pu = None

    def update(self):
        if self.active_pu == PU_NITRO:
            self.pu_timer -= 1
            if self.pu_timer <= 0:
                self.active_pu   = None
                self.nitro_bonus = 0

    def on_hit(self) -> bool:
        
        if self.shielded:
            self.shielded  = False
            self.active_pu = None
            return False
        self.crashes += 1
        return True

    def draw(self, surface):
        r = self.rect
        pygame.draw.rect(surface, self.color, r, border_radius=6)
        wr = pygame.Rect(r.x+4, r.y+6, r.w-8, 14)
        pygame.draw.rect(surface, CYAN, wr, border_radius=3)
        if self.shielded:
            pygame.draw.rect(surface, CYAN,
                             r.inflate(8, 8), 3, border_radius=8)

TRAFFIC_COLORS = [RED, GREEN, ORANGE, PURPLE, (200,200,50)]

class TrafficCar:
    def __init__(self, lane: int, scroll_speed: float):
        self.lane  = lane
        self.x     = float(lane_cx(lane))
        self.y     = float(-TRAFFIC_H)
        self.color = random.choice(TRAFFIC_COLORS)
        self.speed = scroll_speed + random.uniform(0, 2)

    @property
    def rect(self):
        return pygame.Rect(int(self.x) - TRAFFIC_W//2,
                           int(self.y) - TRAFFIC_H//2,
                           TRAFFIC_W, TRAFFIC_H)

    def update(self):
        self.y += self.speed

    def off_screen(self):
        return self.y > WIN_H + TRAFFIC_H

    def draw(self, surface):
        r = self.rect
        pygame.draw.rect(surface, self.color, r, border_radius=5)
        wr = pygame.Rect(r.x+4, r.y+r.h-20, r.w-8, 14)
        pygame.draw.rect(surface, CYAN, wr, border_radius=3)

OBS_TYPES = ["barrier", "oil_spill", "pothole"]

class Obstacle:
    def __init__(self, lane: int, scroll_speed: float):
        self.lane  = lane
        self.x     = float(lane_cx(lane))
        self.y     = float(-40)
        self.type  = random.choice(OBS_TYPES)
        self.speed = scroll_speed
        self.w, self.h = (LANE_W - 6, 18)

    @property
    def rect(self):
        return pygame.Rect(int(self.x) - self.w//2,
                           int(self.y) - self.h//2,
                           self.w, self.h)

    def update(self):
        self.y += self.speed

    def off_screen(self):
        return self.y > WIN_H + 40

    def draw(self, surface):
        r = self.rect
        if self.type == "barrier":
            pygame.draw.rect(surface, BARRIER_C, r, border_radius=4)
            pygame.draw.line(surface, WHITE,
                             (r.x+6, r.centery), (r.right-6, r.centery), 2)
        elif self.type == "oil_spill":
            pygame.draw.ellipse(surface, OIL_C, r)
            pygame.draw.ellipse(surface, PURPLE,
                                r.inflate(-6, -4), 2)
        else:
            pygame.draw.ellipse(surface, DKGRAY, r)
            pygame.draw.ellipse(surface, BLACK,
                                r.inflate(-8, -4))

class LaneHazard:
    
    HEIGHT = 60

    def __init__(self, lane: int, scroll_speed: float):
        self.lane  = lane
        self.x     = ROAD_LEFT + lane * LANE_W
        self.y     = float(-self.HEIGHT)
        self.speed = scroll_speed

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y),
                           LANE_W, self.HEIGHT)

    def update(self):
        self.y += self.speed

    def off_screen(self):
        return self.y > WIN_H + self.HEIGHT

    def draw(self, surface):
        s = pygame.Surface((LANE_W, self.HEIGHT), pygame.SRCALPHA)
        s.fill((255, 80, 80, 90))
        surface.blit(s, (int(self.x), int(self.y)))
        pygame.draw.rect(surface, RED,
                         pygame.Rect(int(self.x), int(self.y),
                                     LANE_W, self.HEIGHT), 2)

class RoadEvent:
    TYPES = ["nitro_strip", "speed_bump", "moving_barrier"]

    def __init__(self, scroll_speed: float):
        self.type  = random.choice(self.TYPES)
        self.y     = float(-30)
        self.speed = scroll_speed
        self.active = True

        if self.type == "moving_barrier":
            self.x    = float(ROAD_LEFT)
            self.dir  = 1
            self.move_speed = 2.5
            self.w, self.h  = ROAD_W, 18
        else:
            self.x = ROAD_LEFT
            self.w = ROAD_W
            self.h = 20

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self):
        self.y += self.speed
        if self.type == "moving_barrier":
            self.x += self.dir * self.move_speed
            if self.x <= ROAD_LEFT or self.x + self.w >= ROAD_RIGHT:
                self.dir *= -1

    def off_screen(self):
        return self.y > WIN_H + 40

    def draw(self, surface):
        r = self.rect
        if self.type == "nitro_strip":
            pygame.draw.rect(surface, NITRO_C, r, border_radius=4)
            pygame.draw.rect(surface, WHITE, r, 2, border_radius=4)
            font = pygame.font.SysFont("consolas", 12, bold=True)
            lbl  = font.render("NITRO", True, BLACK)
            surface.blit(lbl, (r.centerx - lbl.get_width()//2,
                                r.centery - lbl.get_height()//2))
        elif self.type == "speed_bump":
            pygame.draw.rect(surface, BUMP_C, r, border_radius=3)
            for bx in range(r.x+4, r.right-4, 8):
                pygame.draw.circle(surface, ORANGE, (bx, r.centery), 3)
        else:
            pygame.draw.rect(surface, BARRIER_C, r, border_radius=4)
            pygame.draw.rect(surface, WHITE, r, 2, border_radius=4)

PU_COLORS = {PU_NITRO: NITRO_C, PU_SHIELD: CYAN, PU_REPAIR: GREEN}
PU_LABELS = {PU_NITRO: "N", PU_SHIELD: "S", PU_REPAIR: "R"}

class PowerUpItem:
    SIZE = 28

    def __init__(self, lane: int, pu_type: str, scroll_speed: float):
        self.lane    = lane
        self.x       = float(lane_cx(lane))
        self.y       = float(-self.SIZE)
        self.type    = pu_type
        self.speed   = scroll_speed
        self.timer   = PU_TIMEOUT
        self.font    = None

    @property
    def rect(self):
        s = self.SIZE
        return pygame.Rect(int(self.x)-s//2, int(self.y)-s//2, s, s)

    def update(self):
        self.y     += self.speed
        self.timer -= 1

    def expired(self):
        return self.timer <= 0 or self.y > WIN_H + self.SIZE

    def draw(self, surface):
        if self.font is None:
            self.font = pygame.font.SysFont("consolas", 14, bold=True)
        r   = self.rect
        col = PU_COLORS[self.type]
        pygame.draw.rect(surface, col, r, border_radius=6)
        pygame.draw.rect(surface, WHITE, r, 2, border_radius=6)
        lbl = self.font.render(PU_LABELS[self.type], True, BLACK)
        surface.blit(lbl, (r.centerx - lbl.get_width()//2,
                            r.centery - lbl.get_height()//2))

class GameWorld:
    def __init__(self, player_name: str, settings: dict):
        self.player_name = player_name
        self.settings    = settings

        diff  = settings.get("difficulty", "normal")
        cfg   = DIFFICULTY.get(diff, DIFFICULTY["normal"])

        self.base_speed     = cfg["base_speed"]
        self.scroll_speed   = float(self.base_speed)
        self.traffic_freq   = cfg["traffic_freq"]
        self.obstacle_freq  = cfg["obstacle_freq"]

        color = tuple(settings.get("car_color", [50, 180, 255]))
        self.player   = Player(color=color)

        self.traffic   : list[TrafficCar]  = []
        self.obstacles : list[Obstacle]    = []
        self.hazards   : list[LaneHazard]  = []
        self.events    : list[RoadEvent]   = []
        self.powerups  : list[PowerUpItem] = []

        self.stripe_y  = [WIN_H * i // 6 for i in range(6)]

        self.coins    = 0
        self.distance = 0
        self.frame    = 0

        self.hud_font = pygame.font.SysFont("consolas", 16, bold=True)
        self.sm_font  = pygame.font.SysFont("consolas", 13)

    def _update_speed(self):
        self.scroll_speed = self.base_speed + self.distance / 800

    def _safe_lane(self, exclude=None) -> int:
        lanes = [l for l in range(NUM_LANES) if l != exclude]
        return random.choice(lanes)

    def _spawn_traffic(self):
        lane = self._safe_lane(self.player.lane)
        for t in self.traffic:
            if t.lane == lane and t.y < TRAFFIC_H * 2:
                return
        self.traffic.append(TrafficCar(lane, self.scroll_speed))

    def _spawn_obstacle(self):
        lane = random.randint(0, NUM_LANES-1)
        self.obstacles.append(Obstacle(lane, self.scroll_speed))

    def _spawn_hazard(self):
        lane = random.randint(0, NUM_LANES-1)
        self.hazards.append(LaneHazard(lane, self.scroll_speed))

    def _spawn_event(self):
        self.events.append(RoadEvent(self.scroll_speed))

    def _spawn_powerup(self):
        lane  = random.randint(0, NUM_LANES-1)
        ptype = random.choice([PU_NITRO, PU_SHIELD, PU_REPAIR])
        self.powerups.append(PowerUpItem(lane, ptype, self.scroll_speed))

    def update(self, coins_from_base: int) -> str:
        
        self.frame    += 1
        self.distance += 1
        self.coins    += coins_from_base
        self._update_speed()

        player = self.player
        player.update()
        player.handle_input()

        tf = max(30, self.traffic_freq - self.distance // 200)
        of = max(60, self.obstacle_freq - self.distance // 300)

        if self.frame % tf == 0:
            self._spawn_traffic()
        if self.frame % of == 0:
            self._spawn_obstacle()
        if self.frame % 300 == 0:
            self._spawn_hazard()
        if self.frame % 400 == 0:
            self._spawn_event()
        if self.frame % 350 == 0 and len(self.powerups) == 0:
            self._spawn_powerup()

        for t in self.traffic:   t.update()
        for o in self.obstacles: o.update()
        for h in self.hazards:   h.update()
        for e in self.events:    e.update()
        for p in self.powerups:  p.update()

        self.traffic   = [t for t in self.traffic   if not t.off_screen()]
        self.obstacles = [o for o in self.obstacles if not o.off_screen()]
        self.hazards   = [h for h in self.hazards   if not h.off_screen()]
        self.events    = [e for e in self.events    if not e.off_screen()]
        self.powerups  = [p for p in self.powerups  if not p.expired()]

        for t in self.traffic:
            if player.rect.colliderect(t.rect):
                if player.on_hit():
                    return "dead"
                self.traffic.remove(t)
                break

        for o in self.obstacles:
            if player.rect.colliderect(o.rect):
                if o.type == "oil_spill":
                    self.scroll_speed = max(2, self.scroll_speed - 1.5)
                    self.obstacles.remove(o)
                else:
                    if player.on_hit():
                        return "dead"
                    self.obstacles.remove(o)
                break

        for h in self.hazards:
            if player.rect.colliderect(h.rect):
                self.scroll_speed = max(2, self.scroll_speed - 0.8)

        for e in self.events:
            if player.rect.colliderect(e.rect):
                if e.type == "nitro_strip":
                    player.collect_powerup(PU_NITRO)
                    self.events.remove(e)
                elif e.type == "speed_bump":
                    self.scroll_speed = max(2, self.scroll_speed - 2)
                    self.events.remove(e)
                elif e.type == "moving_barrier":
                    if player.on_hit():
                        return "dead"
                    self.events.remove(e)
                break

        for p in self.powerups:
            if player.rect.colliderect(p.rect):
                player.collect_powerup(p.type)
                self.powerups.remove(p)
                break

        return "alive"

    @property
    def score(self) -> int:
        base    = self.coins * 10
        dist_pts = self.distance // 10
        pu_bonus = 50 if self.player.active_pu else 0
        return base + dist_pts + pu_bonus

    def draw_road(self, surface):
        surface.fill((34, 100, 34))
        pygame.draw.rect(surface, ROAD_C,
                         (ROAD_LEFT, 0, ROAD_W, WIN_H))
        for i in range(1, NUM_LANES):
            lx = ROAD_LEFT + i * LANE_W
            for sy in self.stripe_y:
                pygame.draw.rect(surface, LINE_C,
                                 (lx - 2, sy, 4, 30))
        sp = int(self.scroll_speed) + self.player.nitro_bonus
        self.stripe_y = [(s + sp) % WIN_H for s in self.stripe_y]

    def draw_entities(self, surface):
        for h in self.hazards:   h.draw(surface)
        for e in self.events:    e.draw(surface)
        for o in self.obstacles: o.draw(surface)
        for t in self.traffic:   t.draw(surface)
        for p in self.powerups:  p.draw(surface)
        self.player.draw(surface)

    def draw_hud(self, surface):
        self._hud(surface, f"Coins: {self.coins}", 10, 10)
        self._hud(surface, f"Score: {self.score}", 10, 28)

        self._hud(surface, f"Dist:  {self.distance}m", 10, 46)

        pu = self.player.active_pu
        if pu:
            timer = self.player.pu_timer
            if pu == PU_NITRO:
                msg = f"NITRO {timer//60+1}s"
                col = NITRO_C
            elif pu == PU_SHIELD:
                msg = "SHIELD"
                col = CYAN
            else:
                msg = ""
                col = GREEN
            if msg:
                lbl = self.hud_font.render(msg, True, col)
                surface.blit(lbl, (WIN_W//2 - lbl.get_width()//2, 8))

        sp_lbl = self.sm_font.render(
            f"x{self.scroll_speed:.1f}", True, WHITE)
        surface.blit(sp_lbl, (WIN_W - sp_lbl.get_width() - 8, 10))

    def _hud(self, surface, text, x, y, color=WHITE):
        lbl = self.hud_font.render(text, True, color)
        surface.blit(lbl, (x, y))
