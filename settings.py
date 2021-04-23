import pygame as pg
from random import choice

vec = pg.math.Vector2

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
CAR_ROT_SPEED = 200
CAR_IMG = 'car.png'
CAR_HIT_RECT = pg.Rect(0, 0, 35, 35)
BARREL_OFFSET = vec(30, 10)

# Gun settings
BULLET_IMG = 'bullet.png'
BULLET_SPEED = 500
BULLET_LIFETIME = 1000
BULLET_RATE = 150
KICKBACK = 200
GUN_SPREAD = 5
BULLET_DAMAGE = 10

# Mob settings
MOB_IMG = 'zombie.png'
MOB_SPEEDS = 100
MOB_HIT_RECT = pg.Rect(0, 0, 30, 30)
MOB_HEALTH = 100
MOB_DAMAGE = 10
MOB_KNOCKBACK = 20
AVOID_RADIUS = 50

#Item list
ITEM_IMAGES = {'destination': 'destinationpoint.png', 'pass1': 'kenny.png', 'pass2': 'kenny.png', 'pass3': 'kenny.png', 'pass4' : "kenny.png"}
BOB_RANGE = 15
BOB_SPEED = 0.4

#Night Mode
NIGHT_COLOR = (20,20,20)
LIGHT_RADIUS = (500,500)
LIGHT_MASK = 'light.png'

