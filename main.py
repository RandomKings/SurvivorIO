from typing import Any
import pygame
from pygame.locals import *
import button
import slash_handler
import random
from astar import Node, heuristic, get_neighbors, astar
from world import World
import math

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1000
screen_height = 1000

tile_size = 50
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption('Survivor.IO')

#states
menu_state = "main"

#load images
player_sprites = pygame.image.load('algopro/final exam project/sprites/player/TEST.png').convert_alpha()
start_img = pygame.image.load('algopro/final exam project/screens/start_btn.png').convert_alpha()
exit_img = pygame.image.load('algopro/final exam project/screens/exit_btn.png').convert_alpha()


# load sound
slash_sound = pygame.mixer.Sound('algopro/final exam project/sounds/slash_sound.wav')
damage_taken = pygame.mixer.Sound('algopro/final exam project/sounds/damage_taken.wav')
coin_pick = pygame.mixer.Sound('algopro/final exam project/sounds/coin_pick.wav')
monster_hit = pygame.mixer.Sound('algopro/final exam project/sounds/monster_hit.wav')

#define color
black = (0,0,0)
items_group = pygame.sprite.Group()

def get_img(sheet,frame, width, height,colour):
    image = pygame.Surface((width,height)).convert_alpha()
    image.blit(sheet,(0, 0),(0, (frame*height), width, height))
    image = pygame.transform.scale(image,(50,50))
    image.set_colorkey(colour)

    return image

#load player images
down_1 = get_img(player_sprites,0,16,21,black)
down_2 = get_img(player_sprites,1,16,21,black)
right_1 = get_img(player_sprites,2,16,21,black)
right_2 = get_img(player_sprites,3,16,21,black)
up_1 = get_img(player_sprites,4,16,21,black)
up_2 = get_img(player_sprites,5,16,21,black)
left_1 = get_img(player_sprites,6,16,21,black)
left_2 = get_img(player_sprites,7,16,21,black)

MAX_PLAYER_HEALTH = 3
HEALTH_BAR_WIDTH = 50
HEALTH_BAR_HEIGHT = 10





class Player(pygame.sprite.Sprite):
    def __init__(self,x,y):
        self.image_right = [right_1, right_2]
        self.image_left = [left_1, left_2]
        self.image_up = [up_1, up_2]
        self.image_down = [down_1, down_2]
        self.index = 0
        self.image = self.image_down[self.index]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = x/2
        self.rect.y = y/2
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = 1
        self.direction = 0
        self.slash_duration = 0
        self.slash_timer = 0
        self.keep_attacking = True
        self.last_slash_time = pygame.time.get_ticks()
        self.slash_delay = 500
        self.newRect = None
        self.items_picked_up = 0
        self.health = MAX_PLAYER_HEALTH
        super().__init__()
        self.slash_group = pygame.sprite.Group()
        self.counter = 0
    
    def slash(self):

        current_time = pygame.time.get_ticks()
        if current_time - self.last_slash_time > self.slash_delay and len(self.slash_group) < 2:
            slash = slash_handler.Slash(self.rect, self.direction)
            slash_sound.play()
            self.slash_group.add(slash)
            self.last_slash_time = current_time
        # check collision with tree
        
    
    def collision_detection(self):
        prev_x, prev_y = self.rect.x, self.rect.y
        collisions = pygame.sprite.spritecollide(self, world.collidable_sprites, False, pygame.sprite.collide_mask)
        for collision in collisions:
            if self.direction == 1:
                self.rect.top = collision.rect.bottom
            elif self.direction == 2:
                self.rect.bottom = collision.rect.top
            elif self.direction == 3:
                self.rect.left = collision.rect.right
            elif self.direction == 4:
                self.rect.right = collision.rect.left


    def reduce_health(self):
        self.health -= 1
        if self.health <= 0:
            print("Player is defeated!")
            self.items_picked_up = 0
            self.health = 3
            global menu_state
            menu_state = "main"
            monsters.clear()
            
            
    def draw_health_bar(self):
        pygame.draw.rect(
            screen,
            (255, 0, 0),
            (self.rect.x, self.rect.y - 10, 16*self.health, HEALTH_BAR_HEIGHT),
        )

    def takeDamage(self):
        for monster in monsters:
            if self.rect.colliderect(monster.rect):
                monsters.remove(monster)
                self.reduce_health()
                damage_taken.play()
                new_monster = Monster(find_random_grass_position_x(world),find_random_grass_position_y(world))
                monsters.append(new_monster)
                


    def collect_items(self, items_group):
        collisions = pygame.sprite.spritecollide(self, items_group, True)
        for item in collisions:
            # Handle the collected item (e.g., increase player's score)
            coin_pick.play()
            print("Item collected!")   
            self.items_picked_up += 1
                    

    def Update(self):
        dx = 0
        dy = 0
        walk_cooldown = 20

        # get key press
        key_pressed = pygame.key.get_pressed()

        if key_pressed[pygame.K_w]:
            dy = -5
            self.direction = 1
        elif key_pressed[pygame.K_s]:
            dy = 5
            self.direction = 2
        elif key_pressed[pygame.K_a]:
            dx = -5
            self.direction = 3
        elif key_pressed[pygame.K_d]:
            dx = 5
            self.direction = 4
        if key_pressed[pygame.K_SPACE]:
            player.slash()

        # Calculate the new position
        new_x = self.rect.x + dx
        new_y = self.rect.y + dy
        # Create a temporary rect for collision detection
        temp_rect = self.rect.copy()
        temp_rect.x = new_x
        temp_rect.y = new_y

        # Check collision with the temporary rect
        collisions = [sprite for sprite in world.collidable_sprites if sprite.rect.colliderect(temp_rect)]


        # Update position only if there is no collision
        if not collisions:
            self.rect.x = new_x
            self.rect.y = new_y

        # Check collision again after updating the position
        self.collision_detection()

        # handle animation
        self.counter += 1   
        if self.counter > walk_cooldown:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.image_down):
                self.index = 0
            if self.direction == 1:
                self.image = self.image_up[self.index]
            if self.direction == 2:
                self.image = self.image_down[self.index]
            if self.direction == 3:
                self.image = self.image_left[self.index]
            if self.direction == 4:
                self.image = self.image_right[self.index]

        # Draw the player
        screen.blit(self.image, self.rect)

        # Update and draw slash rectangles if they exist
        player.slash_group.update()
        player.slash_group.draw(screen)

        # Draw slash rectangles if they exist
        if player.slash_group:
            for slash in player.slash_group:
                for monster in monsters:
                    if slash.getNewRect().colliderect(monster.rect):
                        # Monster killed
                        monster_hit.play()
                        item = monster.drop_item()
                        items_group.add(item)
                        monsters.remove(monster)
                        print("killed")
                        # Spawn a new monster
                        new_monster = Monster(find_random_grass_position_x(world), find_random_grass_position_y(world))
                        monsters.append(new_monster)
                        # Remove the slash
                        slash.kill()
                pygame.draw.rect(screen, (255, 255, 255), slash.getNewRect(), 2)
                for tile in world.tile_list:
                    if tile[2] == 1:
                        if slash.getNewRect().colliderect(tile[1]):
                            print("collided")
                            slash.kill()

        # Draw health bar, collect items, etc.
        self.draw_health_bar()
        self.takeDamage()
        player.collect_items(items_group)

        # Update items
        items_group.update()
        items_group.draw(screen)

        # Draw the score
        font = pygame.font.Font(None, 36)
        text = font.render(f'Items: {self.items_picked_up}', True, (255, 255, 255))
        screen.blit(text, (screen_width - 150, 50))

        pygame.display.update()


class Item(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30))  # Adjust the size and appearance
        self.image.fill((255, 255, 0))  # Yellow color as an example
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Monster(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_cooldown = 10  # Adjust value to control the movement cooldown
        self.last_move_time = pygame.time.get_ticks()
        self.path = []
        self.speed =  2 # Adjust value to control the monster's speed

    def move_towards_player(self, player_rect):
        # Get the current time in milliseconds
        current_time = pygame.time.get_ticks()

        # Check if enough time has passed since the last move
        if current_time - self.last_move_time > self.move_cooldown:
            # Convert the monster's current position to grid coordinates (nodes)
            start_node = Node(self.rect.x // tile_size, self.rect.y // tile_size)

            # Calculate the center of the player's rectangle in grid coordinates
            player_center = (
                (player_rect.x + player_rect.width // 2) // tile_size,
                (player_rect.y + player_rect.height // 2) // tile_size
            )

            # Create a goal node based on the player's center
            goal_node = Node(*player_center)

            # Find a path using A* algorithm from the monster to the player
            self.path = astar(world_data, start_node, goal_node)

            # Check if a valid path is found and it has more than one node
            if self.path and len(self.path) > 1:
                # Get the next node in the path
                next_node = self.path[1]
                next_x, next_y = next_node

                # Calculate the direction vector from the monster to the next node
                dx = next_x * tile_size - self.rect.x
                dy = next_y * tile_size - self.rect.y

                # Calculate the distance between the monster and the next node
                distance = math.sqrt(dx ** 2 + dy ** 2)

                # Normalize the direction vector to get a unit vector
                if distance != 0:
                    dx /= distance
                    dy /= distance

                # Move the monster towards the next node smoothly based on its speed
                self.rect.x += dx * self.speed
                self.rect.y += dy * self.speed

            # Update the last move time to the current time
            self.last_move_time = current_time

    def draw_path(self, path):
        for node in path:
            pygame.draw.rect(screen, (0, 0, 255), (node[0] * tile_size, node[1] * tile_size, tile_size, tile_size), 2)

    def drop_item(self):
        item = Item(self.rect.x, self.rect.y)
        return item

    def update(self, player_rect):
        self.move_towards_player(player_rect)
        self.draw_path(self.path)
        screen.blit(self.image, self.rect)


world_data = [
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1], 
[1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1], 
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

world = World(world_data,tile_size)


def find_random_grass_position_x(world):
    grass_tiles = [tile for tile in world.tile_list if tile[2] == 0]
    if grass_tiles:
        random_grass_tile = random.choice(grass_tiles)
        x = random_grass_tile[1].x
        return x
    else:
        return None

def find_random_grass_position_y(world):
    grass_tiles = [tile for tile in world.tile_list if tile[2] == 0]
    if grass_tiles:
        random_grass_tile = random.choice(grass_tiles)
        y = random_grass_tile[1].y
        return y
    else:
        return None

player = Player(screen_width/2, screen_height/2)

start_button = button.Button(150,screen_height/2,start_img, 0.8)
exit_button = button.Button(650,screen_height/2,exit_img,0.8)
monsters = [Monster(find_random_grass_position_x(world),find_random_grass_position_y(world))]
monster_clock = pygame.time.Clock()





spawn_monster_timer = pygame.time.get_ticks()
spawn_monster_interval = 10000  
high_score = 0
run = True

while run:
    clock.tick(fps)
    if menu_state == "main":
        screen.fill((88, 103, 56))
        font = pygame.font.Font(None, 36)
        high_score_text = font.render(f'High Score: {high_score}', True, (255, 255, 255))
        screen.blit(high_score_text, (screen_width - 200, 50))

        if start_button.draw(screen):
            menu_state = "in-game"
        if exit_button.draw(screen):
            run = False

    if menu_state == "in-game":
        world.draw(screen)
        for monster in monsters:
            monster.update(player.rect)
        player.Update()

        # Handle item collection
        player.collect_items(items_group)
        if player.items_picked_up > high_score:
            high_score = player.items_picked_up
    
        current_time = pygame.time.get_ticks()
        if current_time - spawn_monster_timer > spawn_monster_interval:
            # Spawn a new monster
            new_monster = Monster(find_random_grass_position_x(world), find_random_grass_position_y(world))
            monsters.append(new_monster)
            # Reset the timer
            spawn_monster_timer = current_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()


pygame.quit()