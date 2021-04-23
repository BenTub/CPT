import pygame as pg
from random import uniform, choice, random
from settings import *
from tilemap import collide_hit_rect

vec = pg.math.Vector2
# used for the bobbing of the items
import pytweening as tween

def collide_with_walls(sprite, group, dir):
    #using the x and y cordinates at the center of each sprite the code detects if they collide or overlap
    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
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
        #calls the car image
        self.image = game.car_img
        #creates rectangle variable that is placed over the player
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        #from settings it gets the dimensions for the rectangle to be drawn
        self.hit_rect = CAR_HIT_RECT
        self.hit_rect.center = self.rect.center
        #with help from a tutorial we imported vectors to make the player movment and position easier to calulate and work with
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        #rotation of the player
        self.rot = 0
        self.last_shot = 0
        self.health = CAR_HEALTH

    def get_keys(self):
        self.rot_speed = 0
        self.vel = vec(0, 0)
        keys = pg.key.get_pressed()
        #establishing the key press and assigning it to a rotation of the player (ex. if left arrow key is pushed rotate the player left)
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.rot_speed = CAR_ROT_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.rot_speed = -CAR_ROT_SPEED
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.vel = vec(CAR_SPEED, 0).rotate(-self.rot)
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vel = vec(-CAR_SPEED / 2, 0).rotate(-self.rot)
        if keys[pg.K_SPACE]:
            #assiging variabel now to make sure bullets dont loop endlessly
            now = pg.time.get_ticks()
            if now - self.last_shot > BULLET_RATE:
                self.last_shot = now
                #using the bullet settings preset in settings the bullet shoots and gives the player kickback
                dir = vec(1, 0).rotate(-self.rot)
                pos = self.pos + BARREL_OFFSET.rotate(-self.rot)
                Bullet(self.game, pos, dir)
                self.vel = vec(-KICKBACK, 0).rotate(-self.rot)


    def update(self):
        #update the player information and variables set in "__init__'
        self.get_keys()
        self.rot = (self.rot + self.rot_speed * self.game.dt) % 360
        self.image = pg.transform.rotate(self.game.car_img, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center


class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        #assiging he mob sprite to the all sprites group
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        #settings the mob image
        self.image = game.mob_img
        #establishing the rectange variabes
        self.rect = self.image.get_rect()
        #setting the mobs rectange dimensions
        self.hit_rect = MOB_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        #using vectors to set the position speed and acceleration of the mob
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.rot = 0
        #calling the mobs health and speed varibale set in settings
        self.health = MOB_HEALTH
        self.speed = MOB_SPEEDS

    def avoid_mobs(self):
        #using a tutorial we inserted this code to make sure the mobs dont all overlap each other while chasing the car and make the movemnt more realistic
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < AVOID_RADIUS:
                    self.acc += dist.normalize()

    def update(self):
        #assigning informatin to the varibales initialized in "__init__"
        self.rot = (self.game.car.pos - self.pos).angle_to(vec(1, 0))
        self.image = pg.transform.rotate(self.game.mob_img, self.rot)
        # self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.acc = vec(1, 0).rotate(-self.rot)
        self.avoid_mobs()
        self.acc.scale_to_length(self.speed)
        self.acc += self.vel * -1
        self.vel += self.acc * self.game.dt
        self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center
        if self.health <= 0:
            self.kill()



    def draw_health(self):
        #settings the colours, size and position of the health bar above the mob"
        #series of if statments that make the colour of the health bar change as the mob looses health
        if self.health > 60:
            col = GREEN
        elif self.health > 30:
            col = YELLOW
        else:
            col = RED
        width = int(self.rect.width * self.health / MOB_HEALTH)
        self.health_bar = pg.Rect(0, 0, width, 7)
        if self.health < MOB_HEALTH:
            pg.draw.rect(self.image, col, self.health_bar)

class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, dir):
        #adding bullets to the all sprites group
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        #initializing the bullet image
        self.image = game.bullet_img
        #setting up the rectagle around the bullet
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        #using vectors to set the position
        self.pos = vec(pos)
        self.rect.center = pos
        #setting the spped of the bullets and the using the uniform fuction to make sure they have varity in bullet trajectory
        spread = uniform(-GUN_SPREAD, GUN_SPREAD)
        self.vel = dir.rotate(spread) * BULLET_SPEED
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        #if the bullet collides with a wall it should disappar
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()
        #after a certain distance the bullets should disappear so they don't go on forever
        if pg.time.get_ticks() - self.spawn_time > BULLET_LIFETIME:
            self.kill()

class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        #setting up inital variables for the wall
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.wall_img
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

class Obstacle(pg.sprite.Sprite):
    #updating these variables to make them Obstacles that cannot be passed through
    def __init__(self, game, x, y, w, h):
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y


#the item class consists of the passengers and the destination point complied in a last
#the code between the destination and passenger works the same  just with different images
class Item(pg.sprite.Sprite):
    def __init__(self, game, pos, type):
        #adding the item to the all sprites class
        self.groups = game.all_sprites, game.items
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        #assigning the image variable with the list set in settings
        self.image = game.item_images[type]
        #initalizing the rectangle allowing it to be picked up when collided with
        self.rect = self.image.get_rect()
        #identifying the type of item in the list
        self.type = type
        self.pos = pos
        self.rect.center = pos
        #tween is a module which allows a sprite to smoothly bob up and down
        self.tween = tween.easeInOutSine
        self.step = 0
        self.dir = 1

    def update(self):
        # bobbing motion
        offset = BOB_RANGE * (self.tween(self.step / BOB_RANGE) - 0.5)
        self.rect.centery = self.pos.y + offset * self.dir
        self.step += BOB_SPEED
        if self.step > BOB_RANGE:
            self.step = 0
            self.dir *= -1

