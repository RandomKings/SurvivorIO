import pygame
import pygame.sprite as sprite_module


class Slash(pygame.sprite.Sprite):
    def __init__(self, player_rect, direction):
        super().__init__()

        self.direction = direction
        self.right_slash = pygame.image.load('algopro/final exam project/swordanim/right_slash.png').convert_alpha()
        self.down_slash = pygame.image.load('algopro/final exam project/swordanim/down_slash.png').convert_alpha()

        # Call the method to load the appropriate slash image
        self.image = self.load_slash_image()
        self.image = pygame.transform.scale(self.image,(50,50))

        # Use the rect attribute for positioning (will be updated based on movement)
        self.rect = self.image.get_rect(center=self.calculate_slash_position(player_rect))

        # Set the initial time the slash was created
        self.creation_time = pygame.time.get_ticks()

        self.newRect = None

        

    def load_slash_image(self):
        try:
            if self.direction == 1:
                return pygame.transform.flip(self.down_slash, False, True)
            elif self.direction == 2:
                return self.down_slash
            elif self.direction == 3:
                return pygame.transform.flip(self.right_slash, True, False)
            elif self.direction == 4:
                return self.right_slash
        except Exception as e:
            print(f"Error loading slash image: {e}")
            return None

    def calculate_slash_position(self, player_rect):
        # Calculate the initial position of the slash based on the player's position
        if self.direction == 1:
            return player_rect.centerx, player_rect.y + player_rect.height//2
        elif self.direction == 2:
            return player_rect.centerx, player_rect.y + player_rect.height
        elif self.direction == 3:
            return player_rect.x, player_rect.centery
        elif self.direction == 4:
            return player_rect.x + player_rect.width, player_rect.centery
        
    
    def update(self):
        # Move the slash based on the direction 
        slash_speed = 10
        slashdx = 0
        slashdy = 0
        if self.direction == 1:
            slashdy -= slash_speed
        elif self.direction == 2:
            slashdy += slash_speed
        elif self.direction == 3:
            slashdx -= slash_speed
        elif self.direction == 4:
            slashdx += slash_speed
       

        self.rect.x += slashdx
        self.rect.y += slashdy

        # Update the newRect based on the updated rect
        self.newRect = self.rect.copy()

        # Check if the slash has been on the screen for 500 milliseconds
        if pygame.time.get_ticks() - self.creation_time > 500:
            # Remove the slash from the sprite group
            self.kill()
        

    def getNewRect(self):
        return self.newRect