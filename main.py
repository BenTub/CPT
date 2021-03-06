import pygame as pg
import sys
from os import path
from random import uniform
import pytmx
# vectors and arrays are used to make the mobs move on their own
vec = pg.math.Vector2
# used for the bobbing of the items
import pytweening as tween

#########################################################

# settings (images and variables)


# define some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BROWN = (106, 55, 5)
CYAN = (0, 255, 255)

# game settings
WIDTH = 1024  # 16 * 64 or 32 * 32 or 64 * 16
HEIGHT = 768  # 16 * 48 or 32 * 24 or 64 * 12
FPS = 60
TITLE = "Tilemap Demo"
BGCOLOR = BROWN

TILESIZE = 64
GRIDWIDTH = WIDTH / TILESIZE
RIDHEIGHT = HEIGHT / TILESIZE

# Wall settings
WALL_IMG = 'tileGreen_39.png'

# Car settings
CAR_HEALTH = 100
CAR_SPEED = 280
CAR_SPEED2 = 330
CAR_SPEED3 = 380
CAR_ROT_SPEED = 200
CAR_IMG = 'car.png'
CAR_HIT_RECT = pg.Rect(0, 0, 35, 35)
BARREL_OFFSET = vec(30, 10)

# Gun settings
BULLET_IMG = 'bullet.png'
BULLET_SPEED = 500
BULLET_LIFETIME = 1000
BULLET_RATE = 120
KICKBACK = 200
GUN_SPREAD = 5
BULLET_DAMAGE1 = 10
BULLET_DAMAGE2 = 20

# Minimap settings
MINIMAP_IMG = 'Level1Minimap.png'
MINIMAP_IMG2 = 'Level2Minimap.png'
MINIMAP_IMG3 = 'Level3Minimap.png'

# Mob settings
MOB_IMG = 'zombie.png'
MOB_SPEEDS = 100
MOB_SPEEDS2 = 125
MOB_SPEEDS3 = 150
MOB_HIT_RECT = pg.Rect(0, 0, 30, 30)
MOB_HEALTH1 = 100
MOB_HEALTH2 = 110
MOB_HEALTH3 = 150
MOB_DAMAGE = 5
MOB_KNOCKBACK = 20
AVOID_RADIUS = 50

# Item list
ITEM_IMAGES = {'destination': 'destinationpoint.png', 'pass1': 'kenny.png', 'pass2': 'kenny.png', 'pass3': 'kenny.png', 'pass4' : "kenny.png", 'pass5' : "kenny.png", 'pass6' : "kenny.png"}
BOB_RANGE = 15
BOB_SPEED = 0.4

# Night Mode
NIGHT_COLOR = (20, 20, 20)
LIGHT_RADIUS = (500, 500)
LIGHT_MASK = 'light.png'

############################################################################
# Sprite settings (mobs, obstacles, car, passengers)


def draw_car_health(surf, x, y, pct):
    if pct < 0:
        pct = 0
    bar_length = 100
    bar_height = 20
    fill = pct * bar_length
    outline_rect = pg.Rect(x, y, bar_length, bar_height)
    fill_rect = pg.Rect(x, y, fill, bar_height)
    # changes the color of the health bar in top right depending on the players health
    if pct > 0.6:
        col = GREEN
    elif pct > 0.3:
        col = YELLOW
    else:
        col = RED
    # draws a rectangle and fills it with the correct color
    pg.draw.rect(surf, col, fill_rect)
    pg.draw.rect(surf, WHITE, outline_rect, 2)


def collide_with_walls(sprite, group, dir):
    # using coordinates at the center of each sprite rectangle to detects if they collide or overlap
    # checks the x coordinate
    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    # checks the y coordinate
    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y


class Car(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        # adds the sprite to the all sprites group
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # calls the car image
        self.image = game.car_img
        # creates rectangle variable that is placed over the player
        # used to determine if it collides with anything
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        # from settings it gets the dimensions for the rectangle to be drawn
        self.hit_rect = CAR_HIT_RECT
        self.hit_rect.center = self.rect.center
        # imported vectors to make the player movement and position easier tocalculatee and work with
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        # rotation of the player when using the side keys
        self.rot = 0
        self.last_shot = 0
        # car health
        self.health = CAR_HEALTH

    def get_keys(self):
        self.rot_speed = 0
        self.vel = vec(0, 0)
        global level
        keys = pg.key.get_pressed()
        # establishing the key press and assigning it to a rotation of the player
        # (ex. if left arrow key is pushed rotate the player left)
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.rot_speed = CAR_ROT_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.rot_speed = -CAR_ROT_SPEED
        if keys[pg.K_UP] or keys[pg.K_w]:
            # checks which level the game is using global variable then adjusts the speed to make the car move faster
            if level == 1:
                self.vel = vec(CAR_SPEED, 0).rotate(-self.rot)
            elif level == 2:
                self.vel = vec(CAR_SPEED2, 0).rotate(-self.rot)
            elif level == 3:
                self.vel = vec(CAR_SPEED3, 0).rotate(-self.rot)
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            if level == 1:
                # if the car is moving backwards it divides the speed by half so the car goes slower
                self.vel = vec(-CAR_SPEED / 2, 0).rotate(-self.rot)
            elif level == 2:
                self.vel = vec(-CAR_SPEED2 / 2, 0).rotate(-self.rot)
            elif level == 3:
                self.vel = vec(-CAR_SPEED3 / 2, 0).rotate(-self.rot)
        if keys[pg.K_SPACE]:
            # assigning variable "now" to make sure bullets don't keep going endlessly
            now = pg.time.get_ticks()
            if now - self.last_shot > BULLET_RATE:
                self.last_shot = now
                # using the bullet settings the bullet shoots and gives the player and mob kickback
                dir = vec(1, 0).rotate(-self.rot)
                pos = self.pos + BARREL_OFFSET.rotate(-self.rot)
                Bullet(self.game, pos, dir)
                self.vel = vec(-KICKBACK, 0).rotate(-self.rot)
                
    def update(self):
        # update the player information and variables set in "__init__'
        self.get_keys()
        # rotation speed
        self.rot = (self.rot + self.rot_speed * self.game.dt) % 360
        # calls the image and rotates it as the player moves
        self.image = pg.transform.rotate(self.game.car_img, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        # calls the collide with walls function to make sure the player doesn't go through the walls
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center


class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        # assigning the mob sprite to the all sprites group
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # setting the mob image from "load data"
        self.image = game.mob_img
        # establishing the rectangle variables
        self.rect = self.image.get_rect()
        # setting the mobs rectangle dimensions
        self.hit_rect = MOB_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        # using vectors to set the position speed and acceleration of the mob
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.rot = 0
        # calling the global variable level to adjust the mobs health and speed as the levels progress
        global level
        if level == 1:
            self.health = MOB_HEALTH1
            self.speed = MOB_SPEEDS
        elif level == 2:
            self.health = MOB_HEALTH2
            self.speed = MOB_SPEEDS2
        elif level == 3:
            self.health = MOB_HEALTH3
            self.speed = MOB_SPEEDS3

    def avoid_mobs(self):
        # using a tutorial we inserted this code to make sure the mobs don't all overlap each other
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < AVOID_RADIUS:
                    self.acc += dist.normalize()

    def update(self):
        # assigning information to the variables initialized in "__init__"
        self.rot = (self.game.car.pos - self.pos).angle_to(vec(1, 0))
        self.image = pg.transform.rotate(self.game.mob_img, self.rot)
        self.rect.center = self.pos
        self.acc = vec(1, 0).rotate(-self.rot)
        self.avoid_mobs()
        # mob movement using vectors to make it move freely on its own
        self.acc.scale_to_length(self.speed)
        self.acc += self.vel * -1
        self.vel += self.acc * self.game.dt
        self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
        self.hit_rect.centerx = self.pos.x
        # checks so the mobs don't run through the walls and stay on the roads
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center
        # updates when the mobs health equals 0 then it disappears using the kill variable
        if self.health <= 0:
            self.kill()

    def draw_health(self):
        # settings the colours, size and position of the health bar above the mob"
        # series of if statements that make the colour of the health bar change as the mob looses health
        global level
        if self.health > 60:
            col = GREEN
        elif self.health > 30:
            col = YELLOW
        else:
            col = RED
        # if statement that checks if it is level three than if so it adds more health to the bar
        if level == 1:
            width = int(self.rect.width * self.health / MOB_HEALTH1)
            self.health_bar = pg.Rect(0, 0, width, 7)
            if self.health < MOB_HEALTH1:
                pg.draw.rect(self.image, col, self.health_bar)

        elif level == 2:
            width = int(self.rect.width * self.health / MOB_HEALTH2)
            self.health_bar = pg.Rect(0, 0, width, 7)
            if self.health < MOB_HEALTH2:
                pg.draw.rect(self.image, col, self.health_bar)

        elif level == 3:
            width = int(self.rect.width * self.health / MOB_HEALTH3)
            self.health_bar = pg.Rect(0, 0, width, 7)
            if self.health < MOB_HEALTH3:
                pg.draw.rect(self.image, col, self.health_bar)


class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, dir):
        # adding bullets to the all sprites group
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # initializing the bullet image
        self.image = game.bullet_img
        # setting up the rectangle around the bullet
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        # using vectors to set the position
        self.pos = vec(pos)
        self.rect.center = pos
        # setting the speed of the bullets and using the uniform function to make them vary in bullet trajectory
        spread = uniform(-GUN_SPREAD, GUN_SPREAD)
        self.vel = dir.rotate(spread) * BULLET_SPEED
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        # if the bullet collides with a wall it should disappear
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()
        # after a certain distance the bullets should disappear so they don't go on forever
        if pg.time.get_ticks() - self.spawn_time > BULLET_LIFETIME:
            self.kill()


class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        # setting up initial variables for the wall
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # calling wall image and setting rectangles around it
        self.image = game.wall_img
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE


class Obstacle(pg.sprite.Sprite):
    # updating these variables to make them Obstacles that cannot be passed through by any of the sprites
    def __init__(self, game, x, y, w, h):
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # using a rectangle to make a barrier that is placed around the walls
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y


# the item class consists of the passengers and the destination point complied in a list
# the code of the destination and passenger works the same just with different images
class Item(pg.sprite.Sprite):
    def __init__(self, game, pos, type):
        # adding the item to the all sprites class
        self.groups = game.all_sprites, game.items
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # assigning the image variable with the list set in settings
        self.image = game.item_images[type]
        # initializing the rectangle allowing it to be picked up when collided with
        self.rect = self.image.get_rect()
        # identifying the type of item in the list
        self.type = type
        self.pos = pos
        self.rect.center = pos
        # tween is a module which allows a sprite to smoothly bob up and down
        self.tween = tween.easeInOutSine
        self.step = 0
        self.dir = 1

    def update(self):
        # bobbing motion using pytweening
        offset = BOB_RANGE * (self.tween(self.step / BOB_RANGE) - 0.5)
        self.rect.centery = self.pos.y + offset * self.dir
        self.step += BOB_SPEED
        if self.step > BOB_RANGE:
            self.step = 0
            self.dir *= -1


##############################################################################

# "tiled" map settings

def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)


class Map:
    def __init__(self, filename):
        self.data = []
        with open(filename, 'rt') as f:
            for line in f:
                self.data.append(line.strip())
        # assigning dimensions to the map
        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)
        self.width = self.tilewidth * TILESIZE
        self.height = self.tileheight * TILESIZE


class TiledMap:
    # initializing the Tiled map and assigning dimensions to it
    def __init__(self, filename):
        # tmx is the package used to read the Tiled map files
        tm = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm

    def render(self, surface):
        # bliting the Tiled map to the screen
        ti = self.tmxdata.get_tile_image_by_gid\
        # making sure everything is layered properly
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                # making sure it's loaded in at the proper dimensions
                for x, y, gid, in layer:
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile, (x * self.tmxdata.tilewidth,
                                            y * self.tmxdata.tileheight))

    def make_map(self):
        # makes the map
        temp_surface = pg.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface


class Camera:
    # initializing the camera variables
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height
    # using entity function to make it top down and follow the player around the map

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        # the x and y coordinates of the player
        x = -target.rect.centerx + int(WIDTH / 2)
        y = -target.rect.centery + int(HEIGHT / 2)

        # limit scrolling to map size
        x = min(0, x)  # left
        y = min(0, y)  # top
        x = max(-(self.width - WIDTH), x)  # right
        y = max(-(self.height - HEIGHT), y)  # bottom
        self.camera = pg.Rect(x, y, self.width, self.height)


#########################################################################################
# global variables
level = 1
attempts = 0
# game loop


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.load_data()
    # imported this series of if statements that we can use to place text on certain portion of the screen
    # for example 'nw' = north west or 'e' = east

    def draw_text(self, text, font_name, size, color, x, y, align="nw"):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "nw":
            text_rect.topleft = (x, y)
        if align == "ne":
            text_rect.topright = (x, y)
        if align == "sw":
            text_rect.bottomleft = (x, y)
        if align == "se":
            text_rect.bottomright = (x, y)
        if align == "n":
            text_rect.midtop = (x, y)
        if align == "s":
            text_rect.midbottom = (x, y)
        if align == "e":
            text_rect.midright = (x, y)
        if align == "w":
            text_rect.midleft = (x, y)
        if align == "center":
            text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def load_data(self):
        # importing the data from the CPT folder on the desktop
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'img')
        self.map_folder = path.join(game_folder, 'maps')
        self.title_font = path.join(img_folder, 'JosefinSans-Bold.TTF')
        self.title_font2 = path.join(img_folder, 'COMICATE.TTF')
        self.map = TiledMap(path.join(self.map_folder, 'level1.tmx'))
        self.map2 = TiledMap(path.join(self.map_folder, 'level2.tmx'))
        self.map3 = TiledMap(path.join(self.map_folder, 'level3.tmx'))
        self.hud_font = path.join(img_folder, 'JosefinSans-Bold.TTF')
        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 180))
        self.car_img = pg.image.load(path.join(img_folder, CAR_IMG)).convert_alpha()
        self.minimap_img = pg.image.load(path.join(img_folder, MINIMAP_IMG)).convert_alpha()
        self.minimap_img2 = pg.image.load(path.join(img_folder, MINIMAP_IMG2)).convert_alpha()
        self.minimap_img3 = pg.image.load(path.join(img_folder, MINIMAP_IMG3)).convert_alpha()
        self.mob_img = pg.image.load(path.join(img_folder, MOB_IMG)).convert_alpha()
        self.wall_img = pg.image.load(path.join(img_folder, WALL_IMG)).convert_alpha()
        self.bullet_img = pg.image.load(path.join(img_folder, BULLET_IMG)).convert_alpha()
        self.item_images = {}
        # list
        for item in ITEM_IMAGES:
            self.item_images[item] = pg.image.load(path.join(img_folder, ITEM_IMAGES[item])).convert_alpha()
        # lighting effect
        self.fog = pg.Surface((WIDTH, HEIGHT))
        # fills the screen with a transparent gray colour
        self.fog.fill(NIGHT_COLOR)
        # imports and places a light mask over the player
        self.light_mask = pg.image.load(path.join(img_folder, LIGHT_MASK)).convert_alpha()
        self.light_mask = pg.transform.scale(self.light_mask, LIGHT_RADIUS)
        self.light_rect = self.light_mask.get_rect()

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()
        global level
        # import the levels from application 'Tiled'
        # using the global level variable to determine what map to load in
        if level == 1:
            self.map_img = self.map.make_map()
            self.map.rect = self.map_img.get_rect()
            for tile_object in self.map.tmxdata.objects:
                obj_center = vec(tile_object.x + tile_object.width / 2, tile_object.y + tile_object.height / 2)
                # series of if statements that reads the Tiled map and places the Car, Mobs, Items or walls
                # object in the map with the name "player" it calls the car function to be assigned to that object
                if tile_object.name == 'player':
                    self.car = Car(self, obj_center.x, obj_center.y)
                # if the object name is wall it makes it an obstacle using the obstacle function
                if tile_object.name == 'wall':
                    Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
                if tile_object.name in ['destination', 'pass1', 'pass2']:
                    Item(self, obj_center, tile_object.name)
                if tile_object.name == 'mob':
                    Mob(self, obj_center.x, obj_center.y)
            self.camera = Camera(self.map.width, self.map.height)
        elif level == 2:
            self.map2_img = self.map2.make_map()
            self.map2.rect = self.map2_img.get_rect()
            for tile_object in self.map2.tmxdata.objects:
                obj_center = vec(tile_object.x + tile_object.width / 2, tile_object.y + tile_object.height / 2)
                if tile_object.name == 'player':
                    self.car = Car(self, obj_center.x, obj_center.y)
                if tile_object.name == 'wall':
                    Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
                if tile_object.name in ['destination', 'pass1', 'pass2', 'pass3', 'pass4']:
                    Item(self, obj_center, tile_object.name)
                if tile_object.name == 'mob':
                    Mob(self, obj_center.x, obj_center.y)
            self.camera = Camera(self.map2.width, self.map2.height)
        elif level == 3:
            self.map3_img = self.map3.make_map()
            self.map3.rect = self.map3_img.get_rect()
            for tile_object in self.map3.tmxdata.objects:
                obj_center = vec(tile_object.x + tile_object.width / 2, tile_object.y + tile_object.height / 2)
                if tile_object.name == 'player':
                    self.car = Car(self, obj_center.x, obj_center.y)
                if tile_object.name == 'wall':
                    Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
                if tile_object.name in ['destination', 'pass1', 'pass2', 'pass3', 'pass4', 'pass5', 'pass6']:
                    Item(self, obj_center, tile_object.name)
                if tile_object.name == 'mob':
                    Mob(self, obj_center.x, obj_center.y)
            self.camera = Camera(self.map3.width, self.map3.height)
        # setting variables as False to be triggered to True when a certain button is pressed
        self.minimap = False
        self.night = False
        self.pickup = False
        self.over = False

    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        while self.playing:
            # FPS rate at which the game is running
            self.dt = self.clock.tick(FPS) / 1000.0
            self.events()
            if not self.minimap:
                self.update()
            self.draw()

    def quit(self):
        # when player quits game the game loop exits
        pg.quit()
        sys.exit()

    def update(self):
        # update portion of the game loop
        # import all the sprites from the sprites folder
        self.all_sprites.update()
        self.camera.update(self.car)
        global level
        # game over when the length of passengers equals zero including the destination
        if len(self.items) == 0:
            self.playing = False
        # mob hits player
        hits = pg.sprite.spritecollide(self.car, self.mobs, False, collide_hit_rect)
        for hit in hits:
            # subtracts the mob damage from the player health
            self.car.health -= MOB_DAMAGE
            hit.vel = vec(0, 0)
            # when the player health equals zero the game loop ends and ddisplaysthe game over screen
            if self.car.health <= 0:
                self.playing = False
                self.over = True
                self.attempts = True
        if hits:
            # adds a certain knockback speed when mob hits player
            self.car.pos += vec(MOB_KNOCKBACK, 0).rotate(-hits[0].rot)
        # bullets hit mobs
        hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for hit in hits:
            # subtracts the bullet damage from the zombies depending on the level
            if level == 3:
                hit.health -= BULLET_DAMAGE2
            else:
                hit.health -= BULLET_DAMAGE1
            hit.vel = vec(0, 0)

            pg.display.flip()
        # player hits items
        hits = pg.sprite.spritecollide(self.car, self.items, False)
        # if m key is pushed down
        if self.pickup:
            for hit in hits:
                # the item disappears
                hit.kill()
            self.pickup = False

    def draw_grid(self):
        # draws the game grid used to develop the map
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def render_fog(self):
        # draw the light mask (gradient) onto fog image so when you press 'n' it turns into night mode
        self.fog.fill(NIGHT_COLOR)
        self.light_rect.center = self.camera.apply(self.car).center
        self.fog.blit(self.light_mask, self.light_rect)
        self.screen.blit(self.fog, (0, 0), special_flags=pg.BLEND_MULT)

    def draw(self):
        # sets the game caption to 'Tuber'
        pg.display.set_caption("Tuber")
        # using level function to blit it level maps to the screen
        global level
        if level == 1:
            self.screen.blit(self.map_img, self.camera.apply(self.map))
        elif level == 2:
            self.screen.blit(self.map2_img, self.camera.apply(self.map2))
        elif level == 3:
            self.screen.blit(self.map3_img, self.camera.apply(self.map3))
        # self.draw_grid()
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob):
                # draws zombie health to screen above mobs
                sprite.draw_health()
            self.screen.blit(sprite.image, self.camera.apply(sprite))

        # draws player health to top left of screen
        draw_car_health(self.screen, 10, 10, self.car.health / CAR_HEALTH)
        # if statement to engage the night time mode
        if self.night:
            self.render_fog()
        # draws the passengers left text to the top right of the screen and the level in the center
        self.draw_text('Passengers left: {}'.format(len(self.items) - 1), self.hud_font, 30, WHITE, WIDTH - 10, 10, align='ne')
        self.draw_text('Level {}'.format(level), self.hud_font, 50, WHITE, WIDTH / 2, HEIGHT * 1/14, align='center')

        if self.minimap:
            # if the player presses the m key the minimap pops ip
            self.screen.blit(self.dim_screen, (0, 0))
            # draws level number minimap to the top of the screen
            self.draw_text("Level {} Minimap".format(level), self.title_font, 75, WHITE, WIDTH / 2, HEIGHT * 1/8, align='center')
            # blits the minimap image depending on the level
            if level == 1:
                self.screen.blit(self.minimap_img, (0, 140))
            elif level == 2:
                self.screen.blit(self.minimap_img2, (7, 140))
            elif level == 3:
                self.screen.blit(self.minimap_img3, (0, 140))
        pg.display.flip()

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_m:
                    # when m is pressed it triggered the minimap function
                    self.minimap = not self.minimap
                if event.key == pg.K_b:
                    # when b is pressed the pickup function is triggered
                    self.pickup = True
                if event.key == pg.K_n:
                    # when n is pressed the night function is triggered
                    self.night = not self.night

    def show_start_screen(self):
        self.screen.fill(LIGHTGREY)
        pg.display.set_caption("Tuber")
        # draws welcome text to the center of the screen
        self.draw_text('WELCOME TO TUBER', self.title_font, 90, YELLOW, WIDTH / 2, HEIGHT * 1/3, align='center')
        # draws 'press a key to start level' to the center of the screen just below the welcome" (* 3/4)
        self.draw_text('Press a key to start level 1', self.title_font, 50, WHITE, WIDTH / 2, HEIGHT / 2, align='center')
        # draws the controls to the bottom of the splash screen
        self.draw_text('Controls:', self.title_font, 50, YELLOW, WIDTH / 2, HEIGHT * 4 / 5, align='center')
        self.draw_text('Arrow Keys=Move  Space Bar=Shoot', self.title_font, 30, YELLOW, WIDTH / 2, HEIGHT * 3.5 / 4, align='center')
        self.draw_text(' B=Pickup/Drop-off   M=Minimap   N=Night mode', self.title_font, 30, YELLOW, WIDTH / 2, HEIGHT * 3.8 / 4, align='center')
        pg.display.flip()
        'call wait for key function'
        self.wait_for_key()

    def show_go_screen(self):
        global level
        global attempts
        if not self.over:
            if level == 3:
                # if the player completes level three
                self.screen.fill(LIGHTGREY)
                # draws 'GAME COMPLETE!' text to the center of the screen
                self.draw_text('GAME COMPLETE!', self.title_font, 100, YELLOW, WIDTH / 2, HEIGHT / 2, align='center')
                # draws a congratulations and gives the player the number of deaths they had using the attempts variable
                self.draw_text('Congratulations you completed Tuber'.format(attempts), self.title_font, 40, WHITE, WIDTH / 2, HEIGHT * 3 / 4, align='center')
                self.draw_text('Number of attempts/deaths: {}'.format(attempts), self.title_font, 40, WHITE, WIDTH / 2, HEIGHT * 3.5 / 4, align='center')
                pg.display.flip()
                'call wait for key function'
                self.wait_for_key()
            else:
                self.screen.fill(BLACK)
                # draws 'level complete' text to the center of the screen
                self.draw_text('LEVEL COMPLETE!', self.title_font, 100, CYAN, WIDTH / 2, HEIGHT * 1 / 4, align='center')
                # draws 'press a key to start level #' to the center of the screen just below the 'Level over" (* 3/4)
                self.draw_text('Press a key to start level {}'.format(level + 1), self.title_font, 55, WHITE, WIDTH / 2, HEIGHT * 1.5 / 4, align ='center')
                # draws the additions in the next level to the bottom of the screen
                if level == 1:
                    self.draw_text('LEVEL 2:', self.title_font, 60, WHITE, WIDTH / 40, HEIGHT * 3.2 / 4, align='w')
                    self.draw_text('++5 Zombies  ++Zombie Health  ++Zombie Speed', self.title_font, 40, RED, WIDTH / 2, HEIGHT * 3.5 / 4, align='center')
                    self.draw_text('++2 Passengers ++Car speed', self.title_font, 40, GREEN, WIDTH / 2, HEIGHT * 3.8 / 4, align='center')
                elif level == 2:
                    self.draw_text('LEVEL 3:', self.title_font, 60, WHITE, WIDTH / 40, HEIGHT * 3.2 / 4, align='w')
                    self.draw_text('++5 Zombies  ++Zombie Health  ++Zombie Speed', self.title_font, 40, RED, WIDTH / 2, HEIGHT * 3.5 / 4, align='center')
                    self.draw_text('++2 Passengers ++Car speed ++Bullet Damage', self.title_font, 40, GREEN, WIDTH / 2, HEIGHT * 3.8 / 4, align='center')
                pg.display.flip()
                'call wait for key function'
                # calls wait for key 2
                self.wait_for_key2()
        else:
            # game over or level over screen
            self.screen.fill(BLACK)
            # draws 'level over' text to the center of the screen
            self.draw_text('LEVEL OVER', self.title_font2, 150, RED, WIDTH / 2, HEIGHT / 2, align='center')
            # draws 'press a key to start next level' to the center of the screen just below the 'Level over" (* 3/4)
            self.draw_text('Press a key to restart level', self.title_font, 50, WHITE, WIDTH / 2, HEIGHT * 3 / 4,
                           align='center')
            # adds one to attempts
            attempts += 1
            pg.display.flip()
            'call wait for key function'
            self.wait_for_key()

    def wait_for_key(self):
        # wait function so the next level doesnt start automatically
        pg.event.wait()
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                # if the player quits after the level
                if event.type == pg.QUIT:
                    waiting = False
                # uses key up instead of key down to give the player time to press down the key to start the next level
                elif event.type == pg.KEYUP:
                    waiting = False

    def wait_for_key2(self):
        # same as wait for key it just adds one to level.
        # wait function so the next level doesnt start automatically
        pg.event.wait()
        waiting = True
        global level
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                # if the player quits after the level
                if event.type == pg.QUIT:
                    waiting = False
                # uses key up to give the player time to press down the key to start the next level
                if event.type == pg.KEYUP:
                    waiting = False
                    # difference between wait_for_key1 and 2 is wait_for_key2 adds plus one to level when called
                    # wait_for_key2 is called for the level complete screen
                    level += 1

# calls the game loop
g = Game()
g.show_start_screen()
while True:
    g.new()
    g.run()
    g.show_go_screen()
