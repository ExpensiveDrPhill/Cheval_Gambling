"""
Renderer.py - Handles all Pygame rendering and drawing
Separates display logic from game logic
"""
import pygame
import math

class Renderer:
    """Manages all drawing operations for the game."""
    
    def __init__(self, screen, screen_width, race_height, ui_height):
        self.screen = screen
        self.screen_width = screen_width
        self.race_height = race_height
        self.ui_height = ui_height
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GREEN_TRACK = (34, 139, 34)
        self.RED = (213, 50, 80)
        self.BLUE = (50, 80, 213)
        self.FINISH_LINE_COLOR = (255, 215, 0)
        self.UI_BG = (40, 40, 40)
        self.UI_DIVIDER = (100, 100, 100)
        self.GOLD = (255, 215, 0)
        self.GOLD_DARK = (180, 150, 0)
        self.STAT_BAR_BG = (80, 0, 0)
        self.STAT_BAR_FG = (200, 0, 0)
        self.BRIGHT_GREEN = (50, 255, 50)
        
        # Load fonts
        try:
            self.large_font = pygame.font.SysFont('Arial', 50)
            self.medium_font = pygame.font.SysFont('Arial', 24)
            self.small_font = pygame.font.SysFont('Arial', 18)
            self.micro_font = pygame.font.SysFont('Arial', 14)
        except pygame.error:
            self.large_font = pygame.font.Font(None, 64)
            self.medium_font = pygame.font.Font(None, 32)
            self.small_font = pygame.font.Font(None, 24)
            self.micro_font = pygame.font.Font(None, 18)
        
        # UI Element Rects
        self.play_button_rect = pygame.Rect(400, 480, 160, 80)
        self.bet_25_rect = pygame.Rect(30, 530, 35, 35)
        self.bet_50_rect = pygame.Rect(75, 530, 35, 35)
        self.bet_100_rect = pygame.Rect(120, 530, 35, 35)
        self.horse_img_rect = pygame.Rect(30, 425, 120, 90)
    
    def draw_text(self, text, font, color, x, y, align="topleft"):
        """Draw text on screen with specified alignment."""
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect()
        if align == "topleft":
            text_rect.topleft = (x, y)
        elif align == "center":
            text_rect.center = (x, y)
        elif align == "midright":
            text_rect.midright = (x, y)
        self.screen.blit(text_obj, text_rect)
    
    def draw_stat_bar(self, y, label, value):
        """Draw a stat bar with label and filled percentage."""
        self.draw_text(label, self.small_font, self.WHITE, 170, y)
        bar_bg_rect = pygame.Rect(260, y + 5, 120, 15)
        bar_fg_width = int((value / 100) * 120)
        bar_fg_rect = pygame.Rect(260, y + 5, bar_fg_width, 15)
        pygame.draw.rect(self.screen, self.STAT_BAR_BG, bar_bg_rect)
        pygame.draw.rect(self.screen, self.STAT_BAR_FG, bar_fg_rect)
    
    def draw_popup(self, text):
        """Draw a centered popup with semi-transparent background."""
        text_surface = self.large_font.render(text, True, self.WHITE)
        text_rect = text_surface.get_rect(center=(self.screen_width / 2, self.race_height / 2))
        s = pygame.Surface((text_rect.width + 40, text_rect.height + 40))
        s.set_alpha(200)
        s.fill(self.BLACK)
        self.screen.blit(s, (text_rect.x - 20, text_rect.y - 20))
        self.screen.blit(text_surface, text_rect)
    
    def draw_game_state(self, game_manager):
        """Main drawing method - renders entire game state."""
        # Draw background
        if game_manager.background:
            self.screen.blit(game_manager.background, (0, 0))
        else:
            self.screen.fill(self.GREEN_TRACK)
        
        # Draw track lines
        pygame.draw.line(self.screen, self.FINISH_LINE_COLOR, 
                        (game_manager.finish_line_x, game_manager.track_top), 
                        (game_manager.finish_line_x, game_manager.track_bottom), 5)
        pygame.draw.line(self.screen, self.WHITE, 
                        (game_manager.start_line_x, game_manager.track_top), 
                        (game_manager.start_line_x, game_manager.track_bottom), 2)
        
        # Draw horses
        for horse in game_manager.horses:
            horse.draw(self.screen)
        
        # Draw selection rectangle
        if game_manager.game_state == "BETTING" and game_manager.selected_horse:
            pygame.draw.rect(self.screen, self.WHITE, game_manager.selected_horse.rect, 3)
        
        # Draw UI panel
        pygame.draw.rect(self.screen, self.UI_BG, (0, self.race_height, self.screen_width, self.ui_height))
        pygame.draw.line(self.screen, self.UI_DIVIDER, (0, self.race_height), (self.screen_width, self.race_height), 3)
        
        # Preview image
        preview_image = game_manager.selected_horse.get_preview_image()
        scaled_preview = pygame.transform.scale(preview_image, self.horse_img_rect.size)
        self.screen.blit(scaled_preview, self.horse_img_rect.topleft)
        
        self.draw_text(game_manager.selected_horse.name, self.small_font, self.WHITE, 
                      self.horse_img_rect.centerx, 418, align="center")
        self.draw_text(f"MULTIPLIER: {game_manager.selected_horse.multiplier:.2f}X", 
                      self.micro_font, self.WHITE, self.horse_img_rect.centerx, 518, align="center")
        
        # Bet buttons
        self._draw_bet_buttons(game_manager.selected_bet_pct)
        
        # Stats
        self.draw_stat_bar(430, "SPEED", game_manager.selected_horse.stats["SPEED"])
        self.draw_stat_bar(455, "STAMINA", game_manager.selected_horse.stats["STAMINA"])
        self.draw_stat_bar(480, "WIT", game_manager.selected_horse.stats["WIT"])
        
        # Top UI
        self.draw_text("OBJECTIVE: Finish your debt", self.micro_font, self.WHITE, 
                      self.screen_width // 2, 10, align="center")
        self.draw_text(f"DEBT: {game_manager.wallet.debt:,.0f}", self.small_font, self.RED, 
                      self.screen_width // 2, 30, align="center")
        self.draw_text(f"DAY: {game_manager.day} / {game_manager.day_limit}", self.small_font, self.WHITE, 
                      self.screen_width - 10, 10, align="midright")
        
        # Horse info
        self.draw_text(f"CHANCES: {game_manager.selected_horse.winrate_percent:.0f}%", 
                      self.small_font, self.WHITE, 590, 430)
        self.draw_text(f"WEATHER: {game_manager.weather.current_weather}", 
                      self.small_font, self.WHITE, 590, 455)
        self.draw_text(f"PREFERS: {game_manager.selected_horse.weather_preference}", 
                      self.micro_font, self.WHITE, 590, 480)
        
        # Cash display
        self.draw_text(f"CASH: {game_manager.wallet.cash:,.0f}", self.medium_font, self.WHITE, 
                      770, 530, align="midright")
        
        if game_manager.wallet.bet_amount > 0:
            self.draw_text(f"BET: {game_manager.wallet.bet_amount:,.0f}", self.small_font, self.GOLD, 
                          770, 555, align="midright")
            if game_manager.game_state == "BETTING":
                potential_win = math.floor(game_manager.wallet.bet_amount * game_manager.selected_horse.multiplier)
                self.draw_text(f"POTENTIAL: +{potential_win:,.0f}", self.small_font, self.BRIGHT_GREEN, 
                              770, 580, align="midright")
        
        # Play button
        self._draw_play_button(game_manager.game_state)
        
        # Popups
        if game_manager.game_state == "POST_RACE" and game_manager.winner:
            self.draw_popup(f"{game_manager.winner.name} Wins!")
        elif game_manager.game_state == "GAME_OVER":
            self.draw_popup(game_manager.game_over_message)
    
    def _draw_bet_buttons(self, selected_bet_pct):
        """Draw the betting percentage buttons."""
        pygame.draw.rect(self.screen, self.GOLD_DARK if selected_bet_pct == 25 else self.GOLD, self.bet_25_rect)
        self.draw_text("25%", self.small_font, self.BLACK, 
                      self.bet_25_rect.centerx, self.bet_25_rect.centery, align="center")
        
        pygame.draw.rect(self.screen, self.GOLD_DARK if selected_bet_pct == 50 else self.GOLD, self.bet_50_rect)
        self.draw_text("50%", self.small_font, self.BLACK, 
                      self.bet_50_rect.centerx, self.bet_50_rect.centery, align="center")
        
        pygame.draw.rect(self.screen, self.GOLD_DARK if selected_bet_pct == 100 else self.GOLD, self.bet_100_rect)
        self.draw_text("100%", self.small_font, self.BLACK, 
                      self.bet_100_rect.centerx, self.bet_100_rect.centery, align="center")
    
    def _draw_play_button(self, game_state):
        """Draw the play/action button with appropriate text."""
        pygame.draw.rect(self.screen, self.RED, self.play_button_rect)
        
        button_text = "PLAY"
        if game_state == "RACING":
            button_text = "RACING..."
        elif game_state == "POST_RACE":
            button_text = "NEXT DAY"
        elif game_state == "GAME_OVER":
            button_text = "PLAY AGAIN"
        
        self.draw_text(button_text, self.medium_font, self.WHITE, 
                      self.play_button_rect.centerx, self.play_button_rect.centery, align="center")
    
    def get_ui_rects(self):
        """Return dictionary of UI rectangles for click detection."""
        return {
            'play_button': self.play_button_rect,
            'bet_25': self.bet_25_rect,
            'bet_50': self.bet_50_rect,
            'bet_100': self.bet_100_rect
        }
