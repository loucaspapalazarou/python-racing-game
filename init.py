import pygame


# The car is modeled as an object since it is
# always drawn in a different place with different parameters
class Car:
    def __init__(self, max_vel, rotation_vel, x, y):
        self.img = CAR
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.pos_X = x
        self.pos_Y = y

    # draw the car according to rotation
    def draw(self, win, angle):
        blit_rotate_center(win, self.img, (self.pos_X, self.pos_Y), angle)


# Function to make images larger or smaller
def scale_image(img, factor):
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size)


# Helping function to rotate images around their center
# Normal center of rotation is top left
def blit_rotate_center(win, image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=top_left).center)
    win.blit(rotated_image, new_rect.topleft)


# Game initialization
pygame.init()
SIZE = WIDTH, HEIGHT = 700, 700
DEFAULT_IMAGE_SIZE = SIZE
WIN = pygame.display.set_mode(SIZE)
clock = pygame.time.Clock()
DEFAULT_IMAGE_POSITION = (0, 0)
pygame.display.set_caption("Loukas Papalazarou Racing Game!")
FPS = 60
last_angle = 0

# Import images
GRASS = pygame.image.load("assets/grass.jpg")
TRACK = pygame.image.load("assets/track.png")
TRACK_BORDER = pygame.image.load("assets/track-border.png")
CAR = pygame.image.load("assets/car.png")
FINISH = pygame.image.load("assets/finish.png")
MEDALS = pygame.image.load("assets/medals.png")

# Scale images and declare static images
TRACK = scale_image(TRACK, 0.65)
TRACK_BORDER = scale_image(TRACK_BORDER, 0.65)
FINISH = scale_image(FINISH, 0.6)
GRASS = scale_image(GRASS, 2)
CAR = scale_image(CAR, 0.55)
MEDALS = scale_image(MEDALS, 0.3)
images = [(GRASS, (0, 0)),
          (TRACK, (55, 100)),
          (MEDALS, (0, 5)),
          ]
FINISH_POS = (70, 210)

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 128)
BLACK = (0, 0, 0)
color = (255, 255, 255)
color_light = (170, 170, 170)
color_dark = (100, 100, 100)

# Textbox assets
font = pygame.font.Font('freesansbold.ttf', 50)
med_font = pygame.font.Font('freesansbold.ttf', 26)
small_font = pygame.font.Font('freesansbold.ttf', 20)
intro_text = font.render('What is your name?', True, WHITE)
outro_text = font.render('Thanks for playing!', True, WHITE)
space_to_play = font.render('Press Space to begin!', True, WHITE)
