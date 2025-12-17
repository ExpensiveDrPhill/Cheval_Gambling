import pygame
import random
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from anims.SpriteSheet import SpriteSheet 

# Horse class - handles individual horse data and animations
class Horse:
    def __init__(self, name, y_pos, idle_strip_path, run_strip_path, color_fallback, 
                 start_line_x, horse_sprite_width, horse_sprite_height, animation_speed_ms,
                 weather_preference="Sunny"):
        
        self.name = name
        self.rect = pygame.Rect(start_line_x, y_pos, horse_sprite_width, horse_sprite_height)
        self.color_fallback = color_fallback
        self.start_line_x = start_line_x
        # using float for smooth movement because rect only takes int
        self.exact_x = float(start_line_x)
        self.animation_speed_ms = animation_speed_ms
        self.weather_preference = weather_preference
        
        # Hitbox for accurate collision detection (tighter than sprite rect)
        # Positioned at bottom-center of sprite where the horse body is
        hitbox_width = 50
        hitbox_height = 40
        hitbox_x_offset = (horse_sprite_width - hitbox_width) // 2
        hitbox_y_offset = horse_sprite_height - hitbox_height - 5
        self.hitbox = pygame.Rect(
            start_line_x + hitbox_x_offset,
            y_pos + hitbox_y_offset,
            hitbox_width,
            hitbox_height
        )
        
        self.stats = {}
        self.winrate_percent = 0
        self.multiplier = 0
        self.generate_stats_and_odds()

        # --- ANIMATION LOGIC ---
        self.running_frames = []
        self.idle_frames = []
        self.current_animation_frames = [] 
        self.animation_state = "IDLE" # Start in IDLE state

        try:
            # Load IDLE animation strip (3 frames, horizontal)
            idle_sheet = SpriteSheet(idle_strip_path)
            self.idle_frames = idle_sheet.get_animation_row(
                frame_width=256,
                frame_height=192,
                num_frames=3,
                scale_width=horse_sprite_width,
                scale_height=horse_sprite_height,
                row_index=0
            )
            
            # Load RUN animation strip (5 frames, horizontal)
            run_sheet = SpriteSheet(run_strip_path)
            self.running_frames = run_sheet.get_animation_row(
                frame_width=256,
                frame_height=192,
                num_frames=5,
                scale_width=horse_sprite_width,
                scale_height=horse_sprite_height,
                row_index=0
            )
            
            # Set the starting animation to IDLE
            self.current_animation_frames = self.idle_frames
            self.current_frame_index = 0
            self.image = self.current_animation_frames[self.current_frame_index]
            self.last_update_time = pygame.time.get_ticks()

        except Exception as e:
            print(f"Error loading animations: {e}. Using color fallback.")
            self.idle_frames = []
            self.running_frames = []
            self.image = pygame.Surface((horse_sprite_width, horse_sprite_height))
            self.image.fill(self.color_fallback)
            self.idle_frames = [self.image]
            self.current_animation_frames = self.idle_frames
            self.current_frame_index = 0
            self.last_update_time = pygame.time.get_ticks() 

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
        # Apply weather modifier and "slow" horse movement
        movement = (speed_roll + stamina_roll) * weather_modifier * 0.15
        self.exact_x += movement
        old_x = self.rect.x
        self.rect.x = int(self.exact_x)
        # Update hitbox to follow sprite position
        self.hitbox.x += (self.rect.x - old_x)
        
    def reset(self):
        old_x = self.rect.x
        self.rect.x = self.start_line_x
        self.exact_x = float(self.start_line_x)
        # Reset hitbox position
        self.hitbox.x += (self.rect.x - old_x)
        self.generate_stats_and_odds()
        # Reset animation to IDLE
        self.set_animation_state("IDLE")

    # Switch between idle and running animations
    def set_animation_state(self, state):
        if state == "RUNNING" and self.animation_state != "RUNNING":
            self.animation_state = "RUNNING"
            self.current_animation_frames = self.running_frames
            self.current_frame_index = 0 
        elif state == "IDLE" and self.animation_state != "IDLE":
            self.animation_state = "IDLE"
            self.current_animation_frames = self.idle_frames
            self.current_frame_index = 0
            
    # Cycle through animation frames
    def update_animation(self):
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
        if self.idle_frames:
            return self.idle_frames[0]
        elif self.current_animation_frames:
            return self.current_animation_frames[0]
        else:
            return self.image