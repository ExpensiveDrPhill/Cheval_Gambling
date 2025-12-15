import pygame
import random
import sys
import os
import math

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.Horse import Horse
from core.Wallet import Wallet
from core.Renderer import Renderer

#I nitialization
pygame.init()
pygame.font.init()

#  Screen Settings 
SCREEN_WIDTH = 800
RACE_HEIGHT = 400
UI_HEIGHT = 200
SCREEN_HEIGHT = RACE_HEIGHT + UI_HEIGHT
TRACK_TOP_MARGIN = 100      
TRACK_BOTTOM_MARGIN = 400

#  Colors 
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

#  Game Constants 
START_LINE_X = 40
FINISH_LINE_X = SCREEN_WIDTH - 80
HORSE_SPRITE_WIDTH = 64 
HORSE_SPRITE_HEIGHT = 48
STARTING_CASH = 5000
DEBT_TO_PAY = 10000
DAY_LIMIT = 30
WIN_TARGET_CASH = 20000 
ANIMATION_SPEED_MS = 100

#lining
TRACK_TOP_MARGIN = 85     # Y top line awal
TRACK_BOTTOM_MARGIN = 250  # Y bottom line akhir

#Weather Types 
WEATHER_TYPES = ["Sunny", "Rainy"]

# Horse Names 
HORSE_NAMES = [
    "Frankfurt","Mejiro","Seabiscuit", "Black Death", "Senomy", "Nearly There",
    "Thunderbolt", "Shadowfax", "Windrunner", "Stormchaser"
] 

#  WEATHER CLASS 

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
            return 1.1  # 10% boost in preferred weather
        elif self.current_weather in ["Rainy"] and horse_weather_preference in ["Sunny"]:
            return 0.8  # 20% penalty in opposite conditions
        else:
            return 1.0  # Neutral

#  GAMEMANAGER CLASS 

class GameManager:
    """Manages the overall game state, loop, and data."""
    def __init__(self, screen=None):
        # Wallet for financial management
        self.wallet = Wallet(STARTING_CASH, DEBT_TO_PAY)
        
        # Renderer for drawing (will be initialized later if screen provided)
        self.renderer = None
        if screen:
            self.renderer = Renderer(screen, SCREEN_WIDTH, RACE_HEIGHT, UI_HEIGHT)
        
        self.day = 1
        self.day_limit = DAY_LIMIT
        self.win_target = WIN_TARGET_CASH
        self.game_state = "BETTING" 
        
        # Track line positions
        self.start_line_x = START_LINE_X
        self.finish_line_x = FINISH_LINE_X
        self.track_top = TRACK_TOP_MARGIN
        self.track_bottom = TRACK_BOTTOM_MARGIN 
        
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
        
        # Load sound effects
        try:
            pygame.mixer.init()
            sounds_path = os.path.join(project_root, "Sounds")
            self.sound_bet_low = pygame.mixer.Sound(os.path.join(sounds_path, "select_low.wav"))
            self.sound_bet_mid = pygame.mixer.Sound(os.path.join(sounds_path, "select_normal.wav"))
            self.sound_bet_high = pygame.mixer.Sound(os.path.join(sounds_path, "select_high.wav"))
            self.sound_cash_register = pygame.mixer.Sound(os.path.join(sounds_path, "cash_register.mp3"))
            self.sound_horse_gallop = pygame.mixer.Sound(os.path.join(sounds_path, "horse_galloping.mp3"))
            self.sound_losing_bell = pygame.mixer.Sound(os.path.join(sounds_path, "losing_bell.wav"))
        except:
            print("Warning: Could not load sound files. Game will run without audio.")
            self.sound_bet_low = None
            self.sound_bet_mid = None
            self.sound_bet_high = None
            self.sound_cash_register = None
            self.sound_horse_gallop = None
            self.sound_losing_bell = None
        
        # Available horse sprite pairs (idle, run)
        self.available_horse_colors = ["black", "brown", "brown2", "gray", "white", "yellow"]
        self.available_sprites = []
        for color in self.available_horse_colors:
            idle_path = os.path.join(project_root, "Assets", f"horses_idle_right_{color}.png")
            run_path = os.path.join(project_root, "Assets", f"horses_run_right_{color}.png")
            self.available_sprites.append((idle_path, run_path))
        
        self.horses = self._create_horses()
        
        self.selected_horse = self.horses[0]
        self.selected_bet_pct = 0
        self.winner = None
        self.game_over_message = ""
    
    def _create_horses(self):
        """Create unique horses with different sprites and weather preferences."""
        horses = []
        y_positions = [90, 110, 130, 155, 180]
        
        # Randomly choose 3-5 horses for this race
        num_horses = random.randint(3, 5)
        used_sprite_pairs = random.sample(self.available_sprites, min(num_horses, len(self.available_sprites)))
        used_y_positions = y_positions[:num_horses]
        # Pick unique names
        used_names = random.sample(HORSE_NAMES, num_horses)
        
        for i, (sprite_pair, y_pos, name) in enumerate(zip(used_sprite_pairs, used_y_positions, used_names)):
            idle_path, run_path = sprite_pair
            weather_pref = random.choice(WEATHER_TYPES)
            horse = Horse(
                name=name,
                y_pos=y_pos,
                idle_strip_path=idle_path,
                run_strip_path=run_path,
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
                self.wallet.reset_bet()
                self.selected_bet_pct = 0
                break

    def set_bet(self, percent):
        if self.game_state != "BETTING":
            return
        self.selected_bet_pct = percent
        self.wallet.bet_amount = self.wallet.get_bet_percentage_amount(percent)

    def start_race(self):
        if self.game_state == "BETTING" and self.wallet.bet_amount > 0 and self.selected_horse:
            self.wallet.place_bet(self.wallet.bet_amount)
            self.game_state = "RACING"
            self.winner = None
            
            # Play gallop sound on loop (-1 means infinite loop)
            if self.sound_horse_gallop:
                self.sound_horse_gallop.play(loops=-1)
            
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
                # Stop gallop sound when race ends
                if self.sound_horse_gallop:
                    self.sound_horse_gallop.stop()
                self.process_winnings()
                self.next_day()
                break
                
    def process_winnings(self):
        if self.winner == self.selected_horse:
            winnings = math.floor(self.wallet.bet_amount * self.selected_horse.multiplier)
            self.wallet.add_winnings(winnings + self.wallet.bet_amount)
            # Play cash register sound on win
            if self.sound_cash_register:
                self.sound_cash_register.play()
        else:
            # Play losing bell sound when losing the bet
            if self.sound_losing_bell:
                self.sound_losing_bell.play()
        self.wallet.update_debt()
    
    def next_day(self):
        self.day += 1
        if self.wallet.check_bankruptcy() and self.day <= self.day_limit:
            self.game_state = "GAME_OVER"
            self.game_over_message = "You're Bankrupt!"
            if self.sound_losing_bell:
                self.sound_losing_bell.play()
        elif self.day > self.day_limit:
            if self.wallet.has_reached_target():
                self.game_state = "GAME_OVER"
                self.game_over_message = "You Paid Your Debt and Won!"
            else:
                self.game_state = "GAME_OVER"
                self.game_over_message = "You Failed to Pay the Debt!"
                if self.sound_losing_bell:
                    self.sound_losing_bell.play()
                
    def reset_for_next_race(self):
        if self.game_state == "POST_RACE":
            self.game_state = "BETTING"
            self.wallet.reset_bet()
            self.selected_bet_pct = 0
            # Change weather and regenerate horses for variety
            self.weather.change_weather()
            self.horses = self._create_horses()
            self.selected_horse = self.horses[0]

    def full_game_reset(self):
        screen = self.renderer.screen if self.renderer else None
        self.__init__(screen)

    def handle_click(self, pos):
        if pos[1] < RACE_HEIGHT:
            self.select_horse(pos)
            return
        if self.game_state == "BETTING":
            if self.renderer.play_button_rect.collidepoint(pos):
                self.start_race()
            elif self.renderer.bet_25_rect.collidepoint(pos):
                self.set_bet(25)
                if self.sound_bet_low:
                    self.sound_bet_low.play()
            elif self.renderer.bet_50_rect.collidepoint(pos):
                self.set_bet(50)
                if self.sound_bet_mid:
                    self.sound_bet_mid.play()
            elif self.renderer.bet_100_rect.collidepoint(pos):
                self.set_bet(100)
                if self.sound_bet_high:
                    self.sound_bet_high.play()
        elif self.game_state == "POST_RACE":
            if self.renderer.play_button_rect.collidepoint(pos):
                self.reset_for_next_race()
        elif self.game_state == "GAME_OVER":
            if self.renderer.play_button_rect.collidepoint(pos):
                self.full_game_reset()

    def draw(self, surface):
        self.renderer.draw_game_state(self)

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Horse Race Betting Tycoon")
    
    game_manager = GameManager(screen)
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