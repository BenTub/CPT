import pygame as pg
import sys
from os import path
from random import choice
from settings import *
from sprites import *
from tilemap import *
import time

def level():
    level == 0

def draw_car_health(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 20
    fill = pct * BAR_LENGTH
    outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
    if pct > 0.6:
        col = GREEN
    elif pct > 0.3:
        col = YELLOW
    else:
        col = RED
    pg.draw.rect(surf, col, fill_rect)
    pg.draw.rect(surf, WHITE, outline_rect, 2)


class Game1:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.load_data()

    #series of if statments that we can use to place text on certain portian of the screen signified by 'nw' = north west or 'e' = east
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
        #importing the data from the CPT folder on the desktop
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'img')
        self.map_folder = path.join(game_folder, 'maps')
        self.title_font = path.join(img_folder, 'JosefinSans-Bold.TTF')
        self.title_font2 = path.join(img_folder, 'COMICATE.TTF')
        self.hud_font = path.join(img_folder,'JosefinSans-Bold.TTF')
        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0,0,0,180))
        self.car_img = pg.image.load(path.join(img_folder, CAR_IMG)).convert_alpha()
        self.mob_img = pg.image.load(path.join(img_folder, MOB_IMG)).convert_alpha()
        self.wall_img = pg.image.load(path.join(img_folder, WALL_IMG)).convert_alpha()
        self.bullet_img = pg.image.load(path.join(img_folder, BULLET_IMG)).convert_alpha()
        self.item_images = {}
        #list
        for item in ITEM_IMAGES:
            self.item_images[item] = pg.image.load(path.join(img_folder, ITEM_IMAGES[item])).convert_alpha()
        #lighting effect
        self.fog = pg.Surface((WIDTH, HEIGHT))
        #fills the screen with a transparent gray colour
        self.fog.fill(NIGHT_COLOR)
        #imports and places a light mask over the player
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
        #import the levels from application 'Tiled'
        self.map = TiledMap (path.join(self.map_folder, 'level2.tmx'))
        self.map_img = self.map.make_map()
        self.map.rect = self.map_img.get_rect()
        # identifys all the objects in the "Tiled' map by name and assigns varibales to them like wall where the player can't pass through
        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width / 2, tile_object.y + tile_object.height / 2)
            if tile_object.name == 'player':
                self.car = Car(self, obj_center.x, obj_center.y)
            if tile_object.name == 'wall':
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            if tile_object.name in ['destination', 'pass1', 'pass2', 'pass3', 'pass4']:
                Item(self, obj_center, tile_object.name)
            if tile_object.name == 'mob':
                Mob(self, obj_center.x, obj_center.y)

        self.camera = Camera(self.map.width, self.map.height)
        # setting variables as False to be triggered to True when a certain button is pressed
        self.paused = False
        self.night = False
        self.pickup = False
        self.over = False



    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        while self.playing:
            #FPS rate at which the game is running
            self.dt = self.clock.tick(FPS) / 1000.0  # fix for Python 2.x
            self.events()
            if not self.paused:
                self.update()
            self.draw()

    def quit(self):
        #when player quits game the game loop exits
        pg.quit()
        sys.exit()

    def update(self):
        # update portion of the game loop
        #import all the sprites from the sprites folder
        self.all_sprites.update()
        self.camera.update(self.car)
        #game over screen when the length of passengers equels zero including the destination
        if len(self.items) == 0:
            self.playing = False
            level +=1
        #mob hits player
        hits = pg.sprite.spritecollide(self.car, self.mobs, False, collide_hit_rect)
        for hit in hits:
            #subtracts the mob damage from the player health
            self.car.health -= MOB_DAMAGE
            hit.vel = vec(0, 0)
            #when the player health equels zero the game looop ends and displayes the game over screen
            if self.car.health <= 0:
                self.playing = False
                self.over = True
                self.attempts = True
        if hits:
            #adds a certain knockback speed when mob hits player
            self.car.pos += vec(MOB_KNOCKBACK, 0).rotate(-hits[0].rot)
        # bullets hit mobs
        hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for hit in hits:
            #subtracts the bullet damage from the zombies
            hit.health -= BULLET_DAMAGE
            hit.vel = vec(0, 0)

            pg.display.flip()
        # player hits items
        hits = pg.sprite.spritecollide(self.car, self.items, False)
        # if m key is pushed down
        if self.pickup:
            for hit in hits:
                #item disappears
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
        #sets the game caption to 'Tuber'
        pg.display.set_caption("Tuber")
        # self.screen.fill(BGCOLOR)
        self.screen.blit(self.map_img, self.camera.apply(self.map))
        # self.draw_grid()
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob):
                #draws zombie health to screen above mobs
                sprite.draw_health()
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        # draws player health to top left of screen
        draw_car_health(self.screen, 10, 10, self.car.health / CAR_HEALTH)
        #if statment to engage the night time mode
        if self.night:
            self.render_fog()
        # draws the passengers left text to the top right of the screen
        self.draw_text('Passengers left: {}'.format(len(self.items) -1 ), self.hud_font, 30, WHITE, WIDTH -10, 10, align='ne')
        if self.paused:
            #is game is pause using "p" key then it dims the background and draws "Paused" to the center of the screen
            self.screen.blit(self.dim_screen, (0, 0))
            self.draw_text("Paused", self.title_font, 105, CYAN, WIDTH / 2, HEIGHT / 2, align='center')
        pg.display.flip()


    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_p:
                    #when p is pressed it triggered the paused function
                    self.paused  = not self.paused
                if event.key == pg.K_m:
                    #when m is pressed the pickup function is triggered
                    self.pickup = True
                if event.key == pg.K_n:
                    #when n is pressed the night function is triggered
                    self.night = not self.night

    def show_start_screen(self):
        self.screen.fill(LIGHTGREY)
        # draws 'level over' text to the center of the screen
        self.draw_text('WELCOME TO TUBER', self.title_font, 90, YELLOW, WIDTH / 2, HEIGHT * 1/3, align='center')
        # draws 'press a key to start next level' to the center of the screen just below the 'Level over" (* 3/4)
        self.draw_text('Press a key to start level 1', self.title_font, 50, WHITE, WIDTH / 2, HEIGHT / 2,
                       align='center')
        self.draw_text('Controls:', self.title_font, 50, YELLOW, WIDTH / 2, HEIGHT * 4 / 5, align='center')
        self.draw_text('Arrow Keys = Move     M = Pickup/Drop-off      P = Pause      N = Night mode', self.title_font, 25, YELLOW, WIDTH / 2, HEIGHT * 3.5 / 4, align='center')
        pg.display.flip()
        'call wait for key function'
        self.wait_for_key()


    def show_go_screen(self):
        if not self.over:
            # game over or level over screen
            self.screen.fill(BLACK)
            # draws 'level over' text to the center of the screen
            self.draw_text('LEVEL COMPLETE!', self.title_font, 100, CYAN, WIDTH / 2, HEIGHT / 2, align='center')
            # draws 'press a key to start next level' to the center of the screen just below the 'Level over" (* 3/4)
            self.draw_text('Press a key to start next level', self.title_font, 50, WHITE, WIDTH / 2, HEIGHT * 3 / 4, align ='center')
            pg.display.flip()
            'call wait for key function'
            self.wait_for_key()
        else:
            # game over or level over screen
            self.screen.fill(BLACK)
            # draws 'level over' text to the center of the screen
            self.draw_text('LEVEL OVER', self.title_font2, 150, RED, WIDTH / 2, HEIGHT / 2, align='center')
            # draws 'press a key to start next level' to the center of the screen just below the 'Level over" (* 3/4)
            self.draw_text('Press a key to restart level', self.title_font, 50, WHITE, WIDTH / 2, HEIGHT * 3 / 4,
                           align='center')
            pg.display.flip()
            'call wait for key function'
            self.wait_for_key()


    def wait_for_key(self):
        #wait function so the next level doesnt start automatically
        pg.event.wait()
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                #if the player quits after the level
                if event.type == pg.QUIT:
                     waiting = False
                     self.quit
                #uses key up instad of key down to give the player time to press down the key to start the next level
                if event.type == pg.KEYUP:
                     waiting = False


class Game2:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.load_data()

    #series of if statments that we can use to place text on certain portian of the screen signified by 'nw' = north west or 'e' = east
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
        #importing the data from the CPT folder on the desktop
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'img')
        self.map_folder = path.join(game_folder, 'maps')
        self.title_font = path.join(img_folder, 'JosefinSans-Bold.TTF')
        self.title_font2 = path.join(img_folder, 'COMICATE.TTF')
        self.hud_font = path.join(img_folder,'JosefinSans-Bold.TTF')
        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0,0,0,180))
        self.car_img = pg.image.load(path.join(img_folder, CAR_IMG)).convert_alpha()
        self.mob_img = pg.image.load(path.join(img_folder, MOB_IMG)).convert_alpha()
        self.wall_img = pg.image.load(path.join(img_folder, WALL_IMG)).convert_alpha()
        self.bullet_img = pg.image.load(path.join(img_folder, BULLET_IMG)).convert_alpha()
        self.item_images = {}
        #list
        for item in ITEM_IMAGES:
            self.item_images[item] = pg.image.load(path.join(img_folder, ITEM_IMAGES[item])).convert_alpha()
        #lighting effect
        self.fog = pg.Surface((WIDTH, HEIGHT))
        #fills the screen with a transparent gray colour
        self.fog.fill(NIGHT_COLOR)
        #imports and places a light mask over the player
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
        #import the levels from application 'Tiled'
        self.map = TiledMap (path.join(self.map_folder, 'level1.tmx'))
        self.map_img = self.map.make_map()
        self.map.rect = self.map_img.get_rect()
        # identifys all the objects in the "Tiled' map by name and assigns varibales to them like wall where the player can't pass through
        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width / 2, tile_object.y + tile_object.height / 2)
            if tile_object.name == 'player':
                self.car = Car(self, obj_center.x, obj_center.y)
            if tile_object.name == 'wall':
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            if tile_object.name in ['destination', 'pass1', 'pass2', 'pass3', 'pass4']:
                Item(self, obj_center, tile_object.name)
            if tile_object.name == 'mob':
                Mob(self, obj_center.x, obj_center.y)

        self.camera = Camera(self.map.width, self.map.height)
        # setting variables as False to be triggered to True when a certain button is pressed
        self.paused = False
        self.night = False
        self.pickup = False
        self.over = False



    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        while self.playing:
            #FPS rate at which the game is running
            self.dt = self.clock.tick(FPS) / 1000.0  # fix for Python 2.x
            self.events()
            if not self.paused:
                self.update()
            self.draw()

    def quit(self):
        #when player quits game the game loop exits
        pg.quit()
        sys.exit()

    def update(self):
        # update portion of the game loop
        #import all the sprites from the sprites folder
        self.all_sprites.update()
        self.camera.update(self.car)
        #game over screen when the length of passengers equels zero including the destination
        if len(self.items) == 0:
            self.playing = False
        #mob hits player
        hits = pg.sprite.spritecollide(self.car, self.mobs, False, collide_hit_rect)
        for hit in hits:
            #subtracts the mob damage from the player health
            self.car.health -= MOB_DAMAGE
            hit.vel = vec(0, 0)
            #when the player health equels zero the game looop ends and displayes the game over screen
            if self.car.health <= 0:
                self.playing = False
                self.over = True
                self.attempts = True
        if hits:
            #adds a certain knockback speed when mob hits player
            self.car.pos += vec(MOB_KNOCKBACK, 0).rotate(-hits[0].rot)
        # bullets hit mobs
        hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for hit in hits:
            #subtracts the bullet damage from the zombies
            hit.health -= BULLET_DAMAGE
            hit.vel = vec(0, 0)

            pg.display.flip()
        # player hits items
        hits = pg.sprite.spritecollide(self.car, self.items, False)
        # if m key is pushed down
        if self.pickup:
            for hit in hits:
                #item disappears
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
        #sets the game caption to 'Tuber'
        pg.display.set_caption("Tuber")
        # self.screen.fill(BGCOLOR)
        self.screen.blit(self.map_img, self.camera.apply(self.map))
        # self.draw_grid()
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob):
                #draws zombie health to screen above mobs
                sprite.draw_health()
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        # draws player health to top left of screen
        draw_car_health(self.screen, 10, 10, self.car.health / CAR_HEALTH)
        #if statment to engage the night time mode
        if self.night:
            self.render_fog()
        # draws the passengers left text to the top right of the screen
        self.draw_text('Passengers left: {}'.format(len(self.items) -1 ), self.hud_font, 30, WHITE, WIDTH -10, 10, align='ne')
        if self.paused:
            #is game is pause using "p" key then it dims the background and draws "Paused" to the center of the screen
            self.screen.blit(self.dim_screen, (0, 0))
            self.draw_text("Paused", self.title_font, 105, CYAN, WIDTH / 2, HEIGHT / 2, align='center')
        pg.display.flip()


    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_p:
                    #when p is pressed it triggered the paused function
                    self.paused  = not self.paused
                if event.key == pg.K_m:
                    #when m is pressed the pickup function is triggered
                    self.pickup = True
                if event.key == pg.K_n:
                    #when n is pressed the night function is triggered
                    self.night = not self.night

    def show_start_screen(self):
        self.screen.fill(LIGHTGREY)
        # draws 'level over' text to the center of the screen
        self.draw_text('WELCOME TO TUBER', self.title_font, 90, YELLOW, WIDTH / 2, HEIGHT * 1/3, align='center')
        # draws 'press a key to start next level' to the center of the screen just below the 'Level over" (* 3/4)
        self.draw_text('Press a key to start level 1', self.title_font, 50, WHITE, WIDTH / 2, HEIGHT / 2,
                       align='center')
        self.draw_text('Controls:', self.title_font, 50, YELLOW, WIDTH / 2, HEIGHT * 4 / 5, align='center')
        self.draw_text('Arrow Keys = Move     M = Pickup/Drop-off      P = Pause      N = Night mode', self.title_font, 25, YELLOW, WIDTH / 2, HEIGHT * 3.5 / 4, align='center')
        pg.display.flip()
        'call wait for key function'
        self.wait_for_key()


    def show_go_screen(self):
        if not self.over:
            # game over or level over screen
            self.screen.fill(BLACK)
            # draws 'level over' text to the center of the screen
            self.draw_text('LEVEL COMPLETE!', self.title_font, 100, CYAN, WIDTH / 2, HEIGHT / 2, align='center')
            # draws 'press a key to start next level' to the center of the screen just below the 'Level over" (* 3/4)
            self.draw_text('Press a key to start next level', self.title_font, 50, WHITE, WIDTH / 2, HEIGHT * 3 / 4, align ='center')
            pg.display.flip()
            'call wait for key function'
            self.wait_for_key()
        else:
            # game over or level over screen
            self.screen.fill(BLACK)
            # draws 'level over' text to the center of the screen
            self.draw_text('LEVEL OVER', self.title_font2, 150, RED, WIDTH / 2, HEIGHT / 2, align='center')
            # draws 'press a key to start next level' to the center of the screen just below the 'Level over" (* 3/4)
            self.draw_text('Press a key to restart level', self.title_font, 50, WHITE, WIDTH / 2, HEIGHT * 3 / 4,
                           align='center')
            pg.display.flip()
            'call wait for key function'
            self.wait_for_key()


    def wait_for_key(self):
        #wait function so the next level doesnt start automatically
        pg.event.wait()
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                #if the player quits after the level
                if event.type == pg.QUIT:
                     waiting = False
                     self.quit
                #uses key up instad of key down to give the player time to press down the key to start the next level
                if event.type == pg.KEYUP:
                     waiting = False


# create the game object
if level == 0:
    g = Game1()
    g.show_start_screen()
elif level == 1:
    g = Game2()
while True:
    g.new()
    g.run()
    g.show_go_screen()
