import pygame
import random
import math
from enum import Enum

# Initialize Pygame and Mixer
pygame.init()
pygame.mixer.init()

# Constants - Upgraded to 1080p!
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60
GRAVITY = 0.6
SCREW_RADIUS = 15 # Scaled up for 1080p
INVENTORY_Y = 950 # Moved down to the bottom of the new screen

class Color(Enum):
    RED = (255, 50, 50)
    BLUE = (50, 50, 255)
    GREEN = (50, 255, 50)
    YELLOW = (255, 255, 50)
    ORANGE = (255, 165, 0)
    PURPLE = (180, 50, 255)
    CYAN = (50, 255, 255)

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    WON = 3
    LOST = 4
    SETTINGS = 5

class Screw:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.color = color
    
    def draw(self, screen):
        pygame.draw.circle(screen, (20, 20, 20), (int(self.x) + 3, int(self.y) + 3), SCREW_RADIUS)
        pygame.draw.circle(screen, self.color.value, (int(self.x), int(self.y)), SCREW_RADIUS)
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x) - 4, int(self.y) - 4), 4)

class Plate:
    def __init__(self, points, color, layer):
        self.points = points
        self.base_color = color
        self.layer = layer
        self.active = True
        self.screws = []
        self.vx, self.vy = 0, 0
        self.angle, self.rot_speed = 0, 0

    def update(self):
        if not self.active:
            self.vy += GRAVITY
            self.points = [(p[0] + self.vx, p[1] + self.vy) for p in self.points]
            self.angle += self.rot_speed

    def draw(self, screen):
        if not self.active and self.points[0][1] > SCREEN_HEIGHT + 200: return
        display_pts = self.points
        if not self.active:
            cx, cy = sum(p[0] for p in self.points)/len(self.points), sum(p[1] for p in self.points)/len(self.points)
            rad = math.radians(self.angle)
            display_pts = [((px-cx)*math.cos(rad)-(py-cy)*math.sin(rad)+cx, (px-cx)*math.sin(rad)+(py-cy)*math.cos(rad)+cy) for px, py in self.points]

        pygame.draw.polygon(screen, self.base_color, display_pts)
        pygame.draw.polygon(screen, (40, 40, 40), display_pts, 4)
        if self.active:
            for s in self.screws: s.draw(screen)

class Game:
    def __init__(self):
        # Set to 1920x1080
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Nofal Match - HD Edition")
        self.clock = pygame.time.Clock()
        
        # Scaled fonts
        self.font_title = pygame.font.SysFont("Verdana", 140, bold=True)
        self.font_lg = pygame.font.SysFont("Verdana", 90, bold=True)
        self.font_md = pygame.font.SysFont("Arial", 40, bold=True)
        
        self.state = GameState.MENU
        self.current_level = 1
        self.menu_timer = 0 
        
        # Volume Settings (0.0, 0.3, 0.6, 1.0)
        self.sfx_vol = 1.0
        self.music_vol = 0.3
        self.load_sounds()

    def load_sounds(self):
        def safe_load(filename):
            try: return pygame.mixer.Sound(filename)
            except: return None
        self.snd_click = safe_load("click.mp3")
        self.snd_match = safe_load("match.mp3")
        self.snd_drop = safe_load("drop.mp3")
        self.snd_win = safe_load("win.mp3")
        self.snd_lose = safe_load("lose.mp3")
        
        try:
            pygame.mixer.music.load("music.mp3")
            self.update_volumes()
            pygame.mixer.music.play(-1)
        except: pass

    def update_volumes(self):
        for snd in [self.snd_click, self.snd_match, self.snd_drop, self.snd_win, self.snd_lose]:
            if snd: snd.set_volume(self.sfx_vol)
        if pygame.mixer.music.get_busy() or True:
            pygame.mixer.music.set_volume(self.music_vol)

    def play_sound(self, sound):
        if sound: sound.play()

    def point_in_poly(self, x, y, poly):
        inside = False
        for i in range(len(poly)):
            p1x, p1y = poly[i]
            p2x, p2y = poly[(i + 1) % len(poly)]
            if min(p1y, p2y) < y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xints:
                            inside = not inside
        return inside

    def load_level(self, level_num):
        self.plates = []
        self.inventory = []
        self.start_ticks = pygame.time.get_ticks()
        
        plate_configs = []
        if level_num == 1:
            # Scaled up level 1 coordinates for 1080p
            p1 = Plate([(700, 400), (1200, 400), (1200, 800), (700, 800)], (180, 180, 180), 0)
            p2 = Plate([(600, 400), (950, 150), (1300, 400)], (150, 50, 50), 1)
            plate_configs = [(p1, 3), (p2, 3)]
        else:
            num_plates = min(3 + level_num, 16) 
            for i in range(num_plates):
                w, h = random.randint(200, 500), random.randint(150, 350)
                x, y = random.randint(200, 1300), random.randint(100, 550)
                p = Plate([(x, y), (x+w, y), (x+w, y+h), (x, y+h)], 
                          (random.randint(50, 210), random.randint(50, 210), random.randint(50, 210)), i)
                plate_configs.append((p, random.randint(2, 5))) 

        total_screws = sum(count for p, count in plate_configs)
        remainder = total_screws % 3
        if remainder != 0:
            needed_screws = 3 - remainder
            plate_configs[0] = (plate_configs[0][0], plate_configs[0][1] + needed_screws)
            total_screws += needed_screws

        self.time_limit = (total_screws * 3) + 10

        all_colors = list(Color)
        num_colors_to_use = min(3 + (level_num // 2), len(all_colors))
        colors_available = all_colors[:num_colors_to_use]

        color_pool = []
        for _ in range(total_screws // 3):
            chosen_color = random.choice(colors_available)
            color_pool.extend([chosen_color, chosen_color, chosen_color])
        random.shuffle(color_pool)

        for plate, count in plate_configs:
            self.plates.append(plate)
            for _ in range(count):
                c = color_pool.pop() 
                mx, Mx = min(p[0] for p in plate.points)+40, max(p[0] for p in plate.points)-40
                my, My = min(p[1] for p in plate.points)+40, max(p[1] for p in plate.points)-40
                plate.screws.append(Screw(random.randint(int(mx), int(Mx)), random.randint(int(my), int(My)), c))

    def handle_click(self, pos):
        if self.state == GameState.MENU:
            if self.btn_start.collidepoint(pos): self.start_new_game()
            elif self.btn_settings.collidepoint(pos): self.state = GameState.SETTINGS
                
        elif self.state == GameState.SETTINGS:
            if self.btn_sfx.collidepoint(pos):
                self.sfx_vol = (self.sfx_vol + 0.3) if self.sfx_vol < 1.0 else 0.0
                self.update_volumes()
                self.play_sound(self.snd_click)
            elif self.btn_music.collidepoint(pos):
                self.music_vol = (self.music_vol + 0.3) if self.music_vol < 1.0 else 0.0
                self.update_volumes()
                self.play_sound(self.snd_click)
            elif self.btn_back.collidepoint(pos):
                self.state = GameState.MENU
                
        elif self.state == GameState.WON:
            if self.btn_next.collidepoint(pos): self.next_level()
            elif self.btn_menu.collidepoint(pos): self.state = GameState.MENU
                
        elif self.state == GameState.LOST:
            if self.btn_retry.collidepoint(pos): self.start_new_game()
            elif self.btn_menu.collidepoint(pos): self.state = GameState.MENU
                
        elif self.state == GameState.PLAYING:
            for p in sorted(self.plates, key=lambda x: x.layer, reverse=True):
                if not p.active: continue
                clicked_screw = None
                for s in p.screws:
                    if math.hypot(s.x - pos[0], s.y - pos[1]) < 35: # Larger hit radius for 1080p
                        clicked_screw = s; break
                if clicked_screw:
                    self.play_sound(self.snd_click)
                    self.inventory.append(clicked_screw.color)
                    p.screws.remove(clicked_screw)
                    if not p.screws: 
                        self.play_sound(self.snd_drop)
                        p.active, p.vx, p.rot_speed = False, random.uniform(-4, 4), random.uniform(-10, 10)
                    self.check_matches()
                    return 
                if self.point_in_poly(pos[0], pos[1], p.points): return 

    def check_matches(self):
        for c in Color:
            if sum(1 for x in self.inventory if x == c) >= 3:
                self.play_sound(self.snd_match)
                ct = 0
                self.inventory = [x for x in self.inventory if not (x == c and (ct := ct + 1) <= 3)]
                self.check_matches()

    def start_new_game(self):
        self.current_level = 1
        self.load_level(self.current_level)
        self.state = GameState.PLAYING

    def next_level(self):
        self.current_level += 1
        self.load_level(self.current_level)
        self.state = GameState.PLAYING

    def update(self):
        if self.state == GameState.PLAYING:
            self.time_left = max(0, self.time_limit - (pygame.time.get_ticks() - self.start_ticks)/1000)
            for p in self.plates: p.update()
            
            if all(not p.active for p in self.plates): 
                self.state = GameState.WON
                self.play_sound(self.snd_win)
                
            elif self.time_left <= 0 or len(self.inventory) > 7: 
                self.state = GameState.LOST
                self.play_sound(self.snd_lose)
                
        elif self.state in [GameState.MENU, GameState.SETTINGS]:
            self.menu_timer += 0.04 

    def draw(self):
        self.screen.fill((135, 206, 235))
        
        if self.state == GameState.MENU:
            pulse = math.sin(self.menu_timer) * 10
            self.draw_text("NOFAL MATCH", 300 + pulse, self.font_title, (255, 255, 255), shadow=True)
            self.btn_start = self.draw_btn("START GAME", SCREEN_WIDTH//2, 600)
            self.btn_settings = self.draw_btn("SETTINGS", SCREEN_WIDTH//2, 700)
            
        elif self.state == GameState.SETTINGS:
            self.draw_text("SETTINGS", 250, self.font_lg, (255, 255, 255), shadow=True)
            self.btn_sfx = self.draw_btn(f"SFX VOL: {int(self.sfx_vol * 100)}%", SCREEN_WIDTH//2, 450)
            self.btn_music = self.draw_btn(f"MUSIC VOL: {int(self.music_vol * 100)}%", SCREEN_WIDTH//2, 550)
            self.btn_back = self.draw_btn("BACK TO MENU", SCREEN_WIDTH//2, 750)
            
        else: # PLAYING, WON, or LOST
            # 1080p Grass Background
            pygame.draw.rect(self.screen, (34, 139, 34), (0, 850, SCREEN_WIDTH, 230))
            
            for p in sorted(self.plates, key=lambda x: x.layer): p.draw(self.screen)
            
            timer_col = (255, 0, 0) if self.time_left < 10 else (255, 255, 255)
            self.draw_text(f"LEVEL {self.current_level} | TIME: {int(self.time_left)}s", 60, self.font_md, timer_col, shadow=True)
            
            # Centered 1080p Inventory Bar
            bar_width = 800
            start_x = (SCREEN_WIDTH - bar_width) // 2
            pygame.draw.rect(self.screen, (40, 40, 40), (start_x, INVENTORY_Y - 30, bar_width, 80), border_radius=15)
            for i, c in enumerate(self.inventory): 
                pygame.draw.circle(self.screen, c.value, (start_x + 60 + i * 95, INVENTORY_Y + 10), SCREW_RADIUS + 5)
            
            # Pop-up Overlays for Win/Lose
            if self.state in [GameState.WON, GameState.LOST]:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 190))
                self.screen.blit(overlay, (0,0))
                
                msg = "LEVEL CLEARED!" if self.state == GameState.WON else "GAME OVER!"
                self.draw_text(msg, 350, self.font_lg, shadow=True)
                
                # Side-by-side buttons
                if self.state == GameState.WON:
                    self.btn_next = self.draw_btn("NEXT LEVEL", SCREEN_WIDTH//2 - 180, 550, width=320)
                    self.btn_menu = self.draw_btn("MAIN MENU", SCREEN_WIDTH//2 + 180, 550, width=320)
                else:
                    self.btn_retry = self.draw_btn("RETRY", SCREEN_WIDTH//2 - 180, 550, width=320)
                    self.btn_menu = self.draw_btn("MAIN MENU", SCREEN_WIDTH//2 + 180, 550, width=320)

        pygame.display.flip()

    def draw_text(self, text, y, font, col=(255, 255, 255), shadow=False):
        if shadow:
            s_img = font.render(text, True, (40, 40, 40))
            self.screen.blit(s_img, s_img.get_rect(center=(SCREEN_WIDTH//2 + 4, y + 4)))
        img = font.render(text, True, col)
        self.screen.blit(img, img.get_rect(center=(SCREEN_WIDTH//2, y)))

    def draw_btn(self, text, center_x, center_y, width=350, height=80):
        r = pygame.Rect(0, 0, width, height)
        r.center = (center_x, center_y)
        color = (100, 100, 100) if r.collidepoint(pygame.mouse.get_pos()) else (70, 70, 70)
        pygame.draw.rect(self.screen, color, r, border_radius=15)
        pygame.draw.rect(self.screen, (255, 255, 255), r, 4, border_radius=15)
        img = self.font_md.render(text, True, (255, 255, 255))
        self.screen.blit(img, img.get_rect(center=r.center))
        return r

    def run(self):
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT: return
                if e.type == pygame.MOUSEBUTTONDOWN: self.handle_click(e.pos)
            self.update(); self.draw(); self.clock.tick(FPS)

if __name__ == "__main__":
    Game().run()