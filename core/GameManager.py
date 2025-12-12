import pygame
import random
import sys
import os
import math

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.Horse import Horse

# --- Initialization ---
pygame.init()
pygame.font.init()

# --- Screen Settings ---
SCREEN_WIDTH = 800
RACE_HEIGHT = 400
UI_HEIGHT = 200
SCREEN_HEIGHT = RACE_HEIGHT + UI_HEIGHT
TRACK_TOP_MARGIN = 100      
TRACK_BOTTOM_MARGIN = 400

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN_TRACK = (34, 139, 34)
RED = (213, 50, 80)
BLUE = (50, 80, 213)
FINISH_LINE_COLOR = (255, 215, 0)
UI_BG = (40, 40, 40)
UI_DIVIDER = (100, 100, 100)
GOLD = (255, 215, 0)
GOLD_DARK = (180, 150, 0)
STAT_BAR_BG = (80, 0, 0)
STAT_BAR_FG = (200, 0, 0)
BRIGHT_GREEN = (50, 255, 50)

# --- Game Constants ---
START_LINE_X = 40
FINISH_LINE_X = SCREEN_WIDTH - 80
HORSE_SPRITE_WIDTH = 64 
HORSE_SPRITE_HEIGHT = 48
STARTING_CASH = 5000
DEBT_TO_PAY = 10000
DAY_LIMIT = 30
WIN_TARGET_CASH = 20000 
ANIMATION_SPEED_MS = 100

# --- Track Line Positioning ---
TRACK_TOP_MARGIN = 85     # Y coordinate where lines START (top)
TRACK_BOTTOM_MARGIN = 250  # Y coordinate where lines END (bottom)

#Weather Types 
WEATHER_TYPES = ["Sunny", "Rainy", "Cloudy", "Windy", "Foggy"]

# Horse Names 
HORSE_NAMES = [
    "Frankfurt","Mejiro","Seabiscuit", "Black Death", "Senomy", "Nearly There",
    "Thunderbolt", "Shadowfax", "Windrunner", "Stormchaser"
] 

# --- Fonts ---
try:
    large_font = pygame.font.SysFont('Arial', 50)
    medium_font = pygame.font.SysFont('Arial', 24)
    small_font = pygame.font.SysFont('Arial', 18)
    micro_font = pygame.font.SysFont('Arial', 14)
except pygame.error:
    large_font = pygame.font.Font(None, 64)
    medium_font = pygame.font.Font(None, 32)
    small_font = pygame.font.Font(None, 24)
    micro_font = pygame.font.Font(None, 18)

# --- UI Element Rects ---
play_button_rect = pygame.Rect(400, 480, 160, 80)
bet_25_rect = pygame.Rect(30, 530, 35, 35)
bet_50_rect = pygame.Rect(75, 530, 35, 35)
bet_100_rect = pygame.Rect(120, 530, 35, 35)
horse_img_rect = pygame.Rect(30, 425, 120, 90)

# --- Helper Functions ---
def draw_text(text, font, color, surface, x, y, align="topleft"):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    if align == "topleft":
        text_rect.topleft = (x, y)
    elif align == "center":
        text_rect.center = (x, y)
    elif align == "midright":
        text_rect.midright = (x, y)
    surface.blit(text_obj, text_rect)

def draw_stat_bar(surface, y, label, value):
    draw_text(label, small_font, WHITE, surface, 170, y)
    bar_bg_rect = pygame.Rect(260, y + 5, 120, 15)
    bar_fg_width = int((value / 100) * 120)
    bar_fg_rect = pygame.Rect(260, y + 5, bar_fg_width, 15)
    pygame.draw.rect(surface, STAT_BAR_BG, bar_bg_rect)
    pygame.draw.rect(surface, STAT_BAR_FG, bar_fg_rect)

# --- WEATHER CLASS ---

class Weather:
    """Manages weather conditions and their effects on horses."""
    def __init__(self):
        self.current_weather = random.choice(WEATHER_TYPES)
    
    def change_weather(self):
        """Randomly change the weather for a new race."""
        self.current_weather = random.choice(WEATHER_TYPES)
    
    def get_performance_modifier(self, horse_weather_preference):
        """Returns a speed modifier based on weather match."""
        if self.current_weather == horse_weather_preference:
            return 1.3  # 30% boost in preferred weather
        elif self.current_weather in ["Rainy", "Foggy"] and horse_weather_preference in ["Sunny", "Windy"]:
            return 0.8  # 20% penalty in opposite conditions
        elif self.current_weather in ["Sunny", "Windy"] and horse_weather_preference in ["Rainy", "Foggy"]:
            return 0.8  # 20% penalty in opposite conditions
        else:
            return 1.0  # Neutral

# --- GAMEMANAGER CLASS ---

class GameManager:
    """Manages the overall game state, loop, and data."""
    def __init__(self):
        self.cash = STARTING_CASH
        self.original_debt = DEBT_TO_PAY
        self.debt = DEBT_TO_PAY
        self.day = 1
        self.day_limit = DAY_LIMIT
        self.win_target = WIN_TARGET_CASH
        self.game_state = "BETTING" 
        
        # Build path to assets
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Load background image
        try:
            bg_path = os.path.join(project_root, "Assets", "horse race arena.png")
            self.background = pygame.image.load(bg_path).convert()
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, RACE_HEIGHT))
        except:
            self.background = None
        
        # Weather system
        self.weather = Weather()
        
        # Available horse sprites
        self.available_sprites = [
            os.path.join(project_root, "Assets", "Horses", "3.png"),
            os.path.join(project_root, "Assets", "Horses", "4.png"),
            os.path.join(project_root, "Assets", "Horses", "5.png"),
            os.path.join(project_root, "Assets", "Horses", "6.png"),
            os.path.join(project_root, "Assets", "Horses", "7.png"),
            os.path.join(project_root, "Assets", "Horses", "8.png"),
        ]
        
        self.horses = self._create_horses()
        
        self.selected_horse = self.horses[0]
        self.bet_amount = 0
        self.selected_bet_pct = 0
        self.winner = None
        self.game_over_message = ""
    
    def _create_horses(self):
        """Create unique horses with different sprites and weather preferences."""
        horses = []
        y_positions = [90, 110, 130, 155, 180]
        
        # Randomly choose 3-5 horses for this race
        num_horses = random.randint(3, 5)
        used_sprites = random.sample(self.available_sprites, min(num_horses, len(self.available_sprites)))
        used_y_positions = y_positions[:num_horses]
        # Pick unique random names for this race
        used_names = random.sample(HORSE_NAMES, num_horses)
        
        for i, (sprite_path, y_pos, name) in enumerate(zip(used_sprites, used_y_positions, used_names)):
            weather_pref = random.choice(WEATHER_TYPES)
            horse = Horse(
                name=name,
                y_pos=y_pos,
                spritesheet_filename=sprite_path,
                color_fallback=(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)),
                start_line_x=START_LINE_X,
                horse_sprite_width=HORSE_SPRITE_WIDTH,
                horse_sprite_height=HORSE_SPRITE_HEIGHT,
                animation_speed_ms=ANIMATION_SPEED_MS,
                weather_preference=weather_pref
            )
            horses.append(horse)
        
        return horses

    def select_horse(self, mouse_pos):
        if self.game_state != "BETTING":
            return
        for horse in self.horses:
            if horse.rect.collidepoint(mouse_pos):
                self.selected_horse = horse
                self.bet_amount = 0
                self.selected_bet_pct = 0
                break

    def set_bet(self, percent):
        if self.game_state != "BETTING":
            return
        self.selected_bet_pct = percent
        self.bet_amount = math.floor(self.cash * (percent / 100))
        if self.bet_amount <= 0 and self.cash > 0:
            self.bet_amount = 1
        if self.bet_amount > self.cash:
            self.bet_amount = self.cash

    def start_race(self):
        if self.game_state == "BETTING" and self.bet_amount > 0 and self.selected_horse:
            self.cash -= self.bet_amount
            self.game_state = "RACING"
            self.winner = None
            
            # Switch all horses to RUNNING animation
            for horse in self.horses:
                horse.set_animation_state("RUNNING")

    def update_race(self):
        if self.game_state != "RACING":
            return

        for horse in self.horses:
            # Get weather modifier for this horse
            weather_mod = self.weather.get_performance_modifier(horse.weather_preference)
            horse.move(weather_mod)
            horse.update_animation() # Update animation while racing
            if horse.rect.right >= FINISH_LINE_X and not self.winner:
                self.winner = horse
                self.game_state = "POST_RACE"
                self.process_winnings()
                self.next_day()
                break
                
    def process_winnings(self):
        if self.winner == self.selected_horse:
            winnings = math.floor(self.bet_amount * self.selected_horse.multiplier)
            self.cash += winnings + self.bet_amount
        self.update_debt()
    
    def update_debt(self):
        """Calculate debt dynamically based on cash progress."""
        cash_gained = self.cash - STARTING_CASH
        self.debt = self.original_debt - cash_gained
        # Clamp debt between 0 and original debt
        self.debt = max(0, min(self.original_debt, self.debt))

    def next_day(self):
        self.day += 1
        if self.cash <= 0 and self.day <= self.day_limit:
            self.game_state = "GAME_OVER"
            self.game_over_message = "You're Bankrupt!"
        elif self.day > self.day_limit:
            if self.cash >= self.win_target:
                self.game_state = "GAME_OVER"
                self.game_over_message = "You Paid Your Debt and Won!"
            else:
                self.game_state = "GAME_OVER"
                self.game_over_message = "You Failed to Pay the Debt!"
                
    def reset_for_next_race(self):
        if self.game_state == "POST_RACE":
            self.game_state = "BETTING"
            self.bet_amount = 0
            self.selected_bet_pct = 0
            # Change weather and regenerate horses for variety
            self.weather.change_weather()
            self.horses = self._create_horses()
            self.selected_horse = self.horses[0]

    def full_game_reset(self):
        self.__init__()

    def handle_click(self, pos):
        if pos[1] < RACE_HEIGHT:
            self.select_horse(pos)
            return
        if self.game_state == "BETTING":
            if play_button_rect.collidepoint(pos):
                self.start_race()
            elif bet_25_rect.collidepoint(pos):
                self.set_bet(25)
            elif bet_50_rect.collidepoint(pos):
                self.set_bet(50)
            elif bet_100_rect.collidepoint(pos):
                self.set_bet(100)
        elif self.game_state == "POST_RACE":
            if play_button_rect.collidepoint(pos):
                self.reset_for_next_race()
        elif self.game_state == "GAME_OVER":
            if play_button_rect.collidepoint(pos):
                self.full_game_reset()

    def draw(self, surface):
        # Draw background or green fill
        if self.background:
            surface.blit(self.background, (0, 0))
        else:
            surface.fill(GREEN_TRACK)
        
        # Draw finish line (vertical yellow line on the right)
        pygame.draw.line(surface, FINISH_LINE_COLOR, (FINISH_LINE_X, TRACK_TOP_MARGIN), (FINISH_LINE_X, TRACK_BOTTOM_MARGIN), 5)
        # Draw start line (vertical white line on the left)
        pygame.draw.line(surface, WHITE, (START_LINE_X, TRACK_TOP_MARGIN), (START_LINE_X, TRACK_BOTTOM_MARGIN), 2)
        
        for horse in self.horses:
            horse.draw(surface)
            
        if self.game_state == "BETTING" and self.selected_horse:
            pygame.draw.rect(surface, WHITE, self.selected_horse.rect, 3) 

        # UI Panel
        pygame.draw.rect(surface, UI_BG, (0, RACE_HEIGHT, SCREEN_WIDTH, UI_HEIGHT))
        pygame.draw.line(surface, UI_DIVIDER, (0, RACE_HEIGHT), (SCREEN_WIDTH, RACE_HEIGHT), 3)

        # Preview Image
        preview_image = self.selected_horse.get_preview_image()
        scaled_preview = pygame.transform.scale(preview_image, horse_img_rect.size)
        surface.blit(scaled_preview, horse_img_rect.topleft)
        
        draw_text(self.selected_horse.name, small_font, WHITE, surface, horse_img_rect.centerx, 418, align="center")
        draw_text(f"MULTIPLIER: {self.selected_horse.multiplier:.2f}X", micro_font, WHITE, surface, horse_img_rect.centerx, 518, align="center")
        
        # Bet Buttons
        pygame.draw.rect(surface, GOLD_DARK if self.selected_bet_pct == 25 else GOLD, bet_25_rect)
        draw_text("25%", small_font, BLACK, surface, bet_25_rect.centerx, bet_25_rect.centery, align="center")
        pygame.draw.rect(surface, GOLD_DARK if self.selected_bet_pct == 50 else GOLD, bet_50_rect)
        draw_text("50%", small_font, BLACK, surface, bet_50_rect.centerx, bet_50_rect.centery, align="center")
        pygame.draw.rect(surface, GOLD_DARK if self.selected_bet_pct == 100 else GOLD, bet_100_rect)
        draw_text("100%", small_font, BLACK, surface, bet_100_rect.centerx, bet_100_rect.centery, align="center")

        # Stats
        draw_stat_bar(surface, 430, "SPEED", self.selected_horse.stats["SPEED"])
        draw_stat_bar(surface, 455, "STAMINA", self.selected_horse.stats["STAMINA"])
        draw_stat_bar(surface, 480, "WIT", self.selected_horse.stats["WIT"])
        
        # Top UI - Objective and Debt (center-top)
        draw_text("OBJECTIVE: Finish your debt", micro_font, WHITE, surface, SCREEN_WIDTH // 2, 10, align="center")
        draw_text(f"DEBT: {self.debt:,.0f}", small_font, RED, surface, SCREEN_WIDTH // 2, 30, align="center")
        
        # Top-right - Day counter
        draw_text(f"DAY: {self.day} / {self.day_limit}", small_font, WHITE, surface, SCREEN_WIDTH - 10, 10, align="midright")
        
        # Info
        draw_text(f"CHANCES: {self.selected_horse.winrate_percent:.0f}%", small_font, WHITE, surface, 590, 430)
        draw_text(f"WEATHER: {self.weather.current_weather}", small_font, WHITE, surface, 590, 455)
        draw_text(f"PREFERS: {self.selected_horse.weather_preference}", micro_font, WHITE, surface, 590, 480)
        
        # Cash display
        draw_text(f"CASH: {self.cash:,.0f}", medium_font, WHITE, surface, 770, 530, align="midright")
        if self.bet_amount > 0:
            draw_text(f"BET: {self.bet_amount:,.0f}", small_font, GOLD, surface, 770, 555, align="midright")
            # Show potential earnings only during betting phase
            if self.game_state == "BETTING":
                potential_win = math.floor(self.bet_amount * self.selected_horse.multiplier)
                draw_text(f"POTENTIAL: +{potential_win:,.0f}", small_font, BRIGHT_GREEN, surface, 770, 580, align="midright")

        # Play Button
        pygame.draw.rect(surface, RED, play_button_rect)
        button_text = "PLAY"
        if self.game_state == "BETTING": button_text = "PLAY"
        elif self.game_state == "RACING": button_text = "RACING..."
        elif self.game_state == "POST_RACE": button_text = "NEXT DAY"
        elif self.game_state == "GAME_OVER": button_text = "PLAY AGAIN"
        draw_text(button_text, medium_font, WHITE, surface, play_button_rect.centerx, play_button_rect.centery, align="center")

        # Winner/Game Over Text
        if self.game_state == "POST_RACE" and self.winner:
            self.draw_popup(f"{self.winner.name} Wins!", surface)
        elif self.game_state == "GAME_OVER":
            self.draw_popup(self.game_over_message, surface)
            
    def draw_popup(self, text, surface):
        text_surface = large_font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH / 2, RACE_HEIGHT / 2))
        s = pygame.Surface((text_rect.width + 40, text_rect.height + 40))
        s.set_alpha(200); s.fill(BLACK)
        surface.blit(s, (text_rect.x - 20, text_rect.y - 20))
        surface.blit(text_surface, text_rect)

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Horse Race Betting Tycoon")
    
    game_manager = GameManager()
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                game_manager.handle_click(event.pos)

        # Logic Update
        if game_manager.game_state == "RACING":
            game_manager.update_race()
        elif game_manager.game_state == "BETTING":
             # Continually update animation so idle frames cycle (if you ever add more idle frames)
             for horse in game_manager.horses:
                horse.update_animation()

        game_manager.draw(screen) 
        pygame.display.flip()
        clock.tick(60)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()