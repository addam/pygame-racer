import pygame
import time
import math
from utils import scale_image, blit_rotate_center

GRASS = scale_image(pygame.image.load("imgs/grass.jpg"), 2.5)
TRACK = scale_image(pygame.image.load("imgs/track.png"), 0.9)

TRACK_BORDER = scale_image(pygame.image.load("imgs/track-border.png"), 0.9)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

FINISH = pygame.image.load("imgs/finish.png")
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (130, 250)

RED_CAR = scale_image(pygame.image.load("imgs/red-car.png"), 0.55)
GREEN_CAR = scale_image(pygame.image.load("imgs/green-car.png"), 0.55)
PURPLE_CAR = scale_image(pygame.image.load("imgs/purple-car.png"), 0.55)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game")

PATH = [(175, 119), (110, 70), (56, 133), (70, 481), (318, 731), (404, 680), (418, 521), (507, 475), (600, 551), (613, 715), (736, 713),
        (734, 399), (611, 357), (409, 343), (433, 257), (697, 258), (738, 123), (581, 71), (303, 78), (275, 377), (176, 388), (178, 260)]

FPS = 60

def clamp(x, low, high):
    return max(low, min(x, high))


class AbstractCar:
    def __init__(self):
        self.img = self.IMG
        self.max_vel = 20
        self.vel = 0
        self.rotation_vel = 4
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1
        self.last_collision = True

    def __str__(self):
        return type(self).__name__

    def rotate(self, amount):
        self.angle += self.rotation_vel * clamp(amount, -0.5, 0.5)

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self, amount):
        if self.vel > 0 and amount < 0:
            amount = max(amount, -5*self.acceleration)
        else:
            amount = clamp(amount, -0.5*self.acceleration, self.acceleration)
        self.vel = clamp(self.vel + amount, -self.max_vel / 2, self.max_vel)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.y -= vertical
        self.x -= horizontal

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def bounce(self):
        self.vel = -0.5 * self.vel
        self.move()


class PlayerCar(AbstractCar):
    IMG = RED_CAR
    START_POS = (150, 200)

    def decide(self, distances):
        forward = 0
        side = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            side += 1
        if keys[pygame.K_RIGHT]:
            side -= 1
        if keys[pygame.K_UP]:
            forward += 1
        if keys[pygame.K_DOWN]:
            forward -= 1
        return forward, side


class AdamCar(AbstractCar):
    IMG = GREEN_CAR
    START_POS = (180, 200)

    def decide(self, distances):
        speed = -10 if distances[0] < 30 else 1
        side = 10 if distances[3] > distances[33] else -10
        return speed, side


class MichalCar2(AbstractCar):
    IMG = GREEN_CAR
    START_POS = (180, 200)

    def decide(self, distances):
        def dev(x, y):
            try:
                return x/y
            except:
                return 0


        #side
        n = 9
        field = distances[-n:]+distances[:n]
        best_dist = 0
        best_direction = 0

        for i in range(len(field)-5):
            if sum(field[i:i+4]) > best_dist:
                best_dist = sum(field[i:i+5])
                best_direction = i+3

        best_direction -= n
        sensor_idx = best_direction
        best_direction /= -2*n

        if best_direction < 0:
            side = 1
        elif best_direction > 0:
            side = -1
        else:
            side = 0

        #speed
        max_speed = 15

        if dev(self.vel, distances[sensor_idx])>0.1:
            print('brake'+str(self.vel))
            speed = -10
        else:
            set_speed = max_speed - (abs(best_direction))*50

            speed = set_speed-self.vel

        return speed, side


class TomasCar(AbstractCar):
    IMG = RED_CAR
    START_POS = (180, 200)

    def decide(self, distances):
        # proudly zkopirovana logika na zataceni:)
        side = 10 if (distances[3] + distances[4])/2 > (distances[32] + distances[33])/2 else -10
        if self.vel > 7.5:
            speed = -0.2
        elif distances[0] < 20:
            speed = -0.5
        elif distances[0] < 50 and self.vel > 1:
            speed = -0.47
        elif distances[0] < 70 and self.vel > 4:
            speed = -0.28
        else:
            speed = 1
        return speed, side


class StolenTomasCar(AbstractCar):
    IMG = PURPLE_CAR
    START_POS = (180, 200)

    def decide(self, distances):
        n = 9
        field = distances[-n:] + distances[:n]
        best_dist = 0
        best_direction = 0

        for i in range(len(field) - 5):
            if sum(field[i:i + 4]) > best_dist:
                best_dist = sum(field[i:i + 5])
                best_direction = i + 3

        best_direction -= n
        best_direction /= -2 * n

        if best_direction < 0:
            side = 1
        elif best_direction > 0:
            side = -1
        else:
            side = 0

        if self.vel > 7.5:
            speed = -0.2
        elif distances[0] < 20:
            speed = -0.5
        elif distances[0] < 50 and self.vel > 1:
            speed = -0.47
        elif distances[0] < 70 and self.vel > 4:
            speed = -0.28
        else:
            speed = 1
        return speed, side


def draw(win, images, cars):
    for img, pos in images:
        win.blit(img, pos)

    for car in cars:
        car.draw(win)
    pygame.display.update()


def cast_ray(angle, car, mask):
    for i in range(1000):
        rad = math.radians(angle)
        x = i * math.sin(rad)
        y = i * math.cos(rad)
        if car.collide(mask, x, y):
            pygame.draw.line(WIN, (255, 128, 128), (car.x, car.y), (car.x - x, car.y - y))
            return i
    return 1000

def move(car):
    distances = [cast_ray(angle + car.angle, car, TRACK_BORDER_MASK) for angle in range(0, 360, 10)]
    forward, side = car.decide(distances)
    car.rotate(side)
    car.move_forward(forward)


def handle_collision(cars):
    for car in cars:
        if car.collide(TRACK_BORDER_MASK) != None:
            car.bounce()
        is_collision = car.collide(FINISH_MASK, *FINISH_POSITION)
        if is_collision and not car.last_collision:
            print(car, current_time)
        car.last_collision = is_collision

def play():
    global current_time
    clock = pygame.time.Clock()
    images = [(GRASS, (0, 0)), (TRACK, (0, 0)),
              (FINISH, FINISH_POSITION), (TRACK_BORDER, (0, 0))]
    cars = [
        MichalCar2(),
        #AdamCar()
        #MichalCar(),
        #AdamCar(),
        #StolenTomasCar(),
        # PlayerCar(),
    ]

    while True:
        clock.tick(FPS)
        draw(WIN, images, cars)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        for car in cars:
            move(car)
        handle_collision(cars)
        current_time += 1

current_time = 0
play()
pygame.quit()
