import pygame

class SpriteSheet:
    """
    Utility class for loading and parsing complex spritesheets.
    """
    def __init__(self, filename):
        try:
            # We use convert_alpha() for transparency
            self.sheet = pygame.image.load(filename).convert_alpha() 
        except pygame.error as e:
            print(f"Unable to load spritesheet image: {filename}")
            raise SystemExit(e)

    def get_image(self, x, y, width, height, scale_width, scale_height):
        """Get a single image frame from the spritesheet."""
        # Create a new blank surface with transparency
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        # Copy the sprite from the sheet onto the new surface
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        
        # Scale the image to fit our game's horse size
        image = pygame.transform.scale(image, (scale_width, scale_height))
        return image

    def get_animation_column(self, frame_width, frame_height, column_index, start_row_index, num_frames, scale_width, scale_height):
        """
        Cuts a vertical column of frames from the spritesheet.
        """
        frames = []
        # X coordinate is constant for a column
        x = column_index * frame_width 
        
        for i in range(num_frames):
            # Y coordinate changes for each frame
            y = (start_row_index + i) * frame_height
            frames.append(self.get_image(x, y, frame_width, frame_height, scale_width, scale_height))
        return frames