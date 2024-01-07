
import pygame

class World():
    def __init__(self, data,tile_size):
        self.tile_list = []
        self.collidable_sprites = pygame.sprite.Group()

        # Load images
        grass_img = pygame.image.load('algopro/final exam project/sprites/floor/Grass1.png')
        tree_img = pygame.image.load('algopro/final exam project/sprites/floor/Tree.png')
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 0:
                    img = pygame.transform.scale(grass_img, (50, 50))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    collidable = 0
                    tile = (img, img_rect, collidable)
                    self.tile_list.append(tile)
                if tile == 1:
                    img = pygame.transform.scale(tree_img, (50, 50))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    collidable = 1
                    tile = (img, img_rect, collidable)
                    self.tile_list.append(tile)
                col_count += 1
            row_count += 1
        for tile in self.tile_list:
            if tile[2] == 1:
                collidable_sprite = pygame.sprite.Sprite()
                collidable_sprite.image = tile[0]
                collidable_sprite.rect = tile[1]
                self.collidable_sprites.add(collidable_sprite)

    def draw(self,screen):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            # pygame.draw.rect(screen,(255,255,255),tile[1], 2)
