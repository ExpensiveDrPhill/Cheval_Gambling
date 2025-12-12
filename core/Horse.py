import pygame
import random
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from anims.SpriteSheet import SpriteSheet 

class Horse:
    """
    Stores all data for a single horse, including multiple animation states.
    """
    def __init__(self, name, y_pos, spritesheet_filename, color_fallback, 
                 start_line_x, horse_sprite_width, horse_sprite_height, animation_speed_ms,
                 weather_preference="Sunny"):
        
        self.name = name
        self.rect = pygame.Rect(start_line_x, y_pos, horse_sprite_width, horse_sprite_height)
        self.color_fallback = color_fallback
        self.start_line_x = start_line_x
        self.animation_speed_ms = animation_speed_ms
        self.weather_preference = weather_preference
        
        self.stats = {}
        self.winrate_percent = 0
        self.multiplier = 0
        self.generate_stats_and_odds()

        # --- ANIMATION LOGIC ---
        self.running_frames = []
        self.idle_frame = None
        self.current_animation_frames = [] 
        self.animation_state = "IDLE" # Start in IDLE state

        try:
            self.spritesheet = SpriteSheet(spritesheet_filename)
            
            # 1. Load the RUNNING animation (Column 3/Index 2, Row 5/Index 4, 6 frames)
            self.running_frames = self.spritesheet.get_animation_column(
                frame_width=64,      # Your sprite's native width
                frame_height=48,     # Your sprite's native height
                column_index=2,      # 3rd column
                start_row_index=4,   # 5th row
                num_frames=6,        # 6 frames of running
                scale_width=horse_sprite_width,
                scale_height=horse_sprite_height
            )
            
            # 2. Load the single IDLE frame (Column 3/Index 2, Row 1/Index 0)
            self.idle_frame = self.spritesheet.get_image(
                x=128,               # 64px * column_index 2
                y=0,                 # 48px * row_index 0
                width=64,
                height=48,
                scale_width=horse_sprite_width,
                scale_height=horse_sprite_height
            )
            
            # 3. Set the starting animation to IDLE
            self.current_animation_frames = [self.idle_frame] 
            self.current_frame_index = 0
            self.image = self.current_animation_frames[self.current_frame_index]
            self.last_update_time = pygame.time.get_ticks()

        except Exception as e:
            print(f"Error loading animations for {spritesheet_filename}: {e}. Using color fallback.")
            self.animation_frames = [] 
            self.image = pygame.Surface((horse_sprite_width, horse_sprite_height))
            self.image.fill(self.color_fallback)
            if self.idle_frame is None:
                self.idle_frame = self.image 

    def generate_stats_and_odds(self):
        self.stats = {
            "SPEED": random.randint(30, 100),
            "STAMINA": random.randint(30, 100),
            "WIT": random.randint(30, 100),
        }
        total_stats = sum(self.stats.values())
        normalized_winrate = (total_stats / 300) ** 1.5 
        self.winrate_percent = max(10, min(90, normalized_winrate * 100))
        multiplier_range = 2.0 - 1.1
        self.multiplier = 1.1 + ((1.0 - normalized_winrate) * multiplier_range)
        self.multiplier = round(max(1.1, min(2.0, self.multiplier)), 2)

    def move(self, weather_modifier=1.0):
        speed_roll = random.randint(1, 3) + int(self.stats["SPEED"] / 20)
        stamina_roll = random.randint(0, int(self.stats["STAMINA"] / 33))
        # Apply weather modifier to movement
        movement = (speed_roll + stamina_roll) * weather_modifier
        self.rect.x += int(movement)
        
    def reset(self):
        self.rect.x = self.start_line_x 
        self.generate_stats_and_odds()
        # Reset animation to IDLE
        self.set_animation_state("IDLE")

    def set_animation_state(self, state):
        """Switches the horse's animation between 'IDLE' and 'RUNNING'."""
        if state == "RUNNING" and self.animation_state != "RUNNING":
            self.animation_state = "RUNNING"
            self.current_animation_frames = self.running_frames
            self.current_frame_index = 0 
        elif state == "IDLE" and self.animation_state != "IDLE":
            self.animation_state = "IDLE"
            self.current_animation_frames = [self.idle_frame]
            self.current_frame_index = 0
            
    def update_animation(self):
        """Cycles through the current animation frames."""
        if not self.current_animation_frames: 
            return 
            
        now = pygame.time.get_ticks()
        if now - self.last_update_time > self.animation_speed_ms: 
            self.last_update_time = now
            self.current_frame_index = (self.current_frame_index + 1) % len(self.current_animation_frames)
            self.image = self.current_animation_frames[self.current_frame_index]

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        
    def get_preview_image(self):
        if self.idle_frame:
            return self.idle_frame
        elif self.current_animation_frames:
            return self.current_animation_frames[0]
        else:
            return self.image