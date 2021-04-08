import pygame
import os
from random import randint, randrange
# ! Animations and Health countdowns.
pygame.mixer.init()
pygame.font.init()

WIDTH, HEIGHT = 1280, 720
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space War")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BORDER = pygame.Rect(WIDTH / 2 - 5, 0, 10, HEIGHT)

# Loading images
HEALTH_ICON = pygame.transform.scale(pygame.image.load(
    "c:/Users/Emirhan Ese/VSC Projects/Python Projects/Multiplayer Space War/Assets/health_icon.png"), (48, 48))

RED_SHIP = pygame.transform.rotate(
    pygame.transform.scale(pygame.image.load("c:/Users/Emirhan Ese/VSC Projects/Python Projects/Multiplayer Space War/Assets/spaceship_red.png"), (80, 80)), 90)
YELLOW_SHIP = pygame.transform.rotate(
    pygame.transform.scale(pygame.image.load("c:/Users/Emirhan Ese/VSC Projects/Python Projects/Multiplayer Space War/Assets/spaceship_yellow.png"), (80, 80)), 270)
RED_SHIP_LASER = pygame.transform.scale(pygame.image.load(
    "c:/Users/Emirhan Ese/VSC Projects/Python Projects/Multiplayer Space War/Assets/red_laser.png"),
    (60, 40))
POWERED_RED_SHIP_LASER = pygame.transform.scale(pygame.image.load(
    "c:/Users/Emirhan Ese/VSC Projects/Python Projects/Multiplayer Space War/Assets/powered_red_laser.png"),
    (70, 40))
YELLOW_SHIP_LASER = pygame.transform.rotate(
    pygame.transform.scale(pygame.image.load("c:/Users/Emirhan Ese/VSC Projects/Python Projects/Multiplayer Space War/Assets/blue_laser.png"), (60, 40)), 180)

POWERED_YELLOW_SHIP_LASER = pygame.transform.rotate(
    pygame.transform.scale(pygame.image.load("c:/Users/Emirhan Ese/VSC Projects/Python Projects/Multiplayer Space War/Assets/powered_blue_laser.png"), (70, 40)), 180)

METEOR = pygame.image.load(
    "c:/Users/Emirhan Ese/VSC Projects/Python Projects/Multiplayer Space War/Assets/meteor.png")

# Loading sound effects
GRENADE_SOUND = pygame.mixer.Sound(
    "c:/Users/Emirhan Ese/VSC Projects/Python Projects/Multiplayer Space War/Assets/grenade.mp3")
GRENADE_SOUND.set_volume(0.2)
GUN_SOUND = pygame.mixer.Sound(
    "c:/Users/Emirhan Ese/VSC Projects/Python Projects/Multiplayer Space War/Assets/gun.mp3")
GUN_SOUND.set_volume(0.1)

# Background image
BG = pygame.image.load(
    "c:/Users/Emirhan Ese/VSC Projects/Python Projects/Multiplayer Space War/Assets/space.png")
ICON = pygame.image.load(
    "c:/Users/Emirhan Ese/VSC Projects/Python Projects/Multiplayer Space War/Assets/icon.png")
pygame.display.set_icon(ICON)


class Health:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.img = HEALTH_ICON
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))


class Meteor:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.img = METEOR
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        for meteor in meteors:
            meteor.y += vel

            if meteor.y >= HEIGHT:
                meteors.remove(meteor)


class Laser:
    def __init__(self, x, y, laser_img):
        self.x = x
        self.y = y
        self.laser_img = laser_img
        self.mask = pygame.mask.from_surface(laser_img)

    def move(self, bullet_velocity):
        self.x += bullet_velocity

    def draw(self, window):
        window.blit(self.laser_img, (self.x, self.y))

    def off_screen(self):
        return not (self.x >= 0 and self.x <= WIDTH)

    def collision(self, obj):
        return collide(obj, self)


class Player:
    COLOR_MAP = {
        "red": (RED_SHIP, RED_SHIP_LASER),
        "yellow": (YELLOW_SHIP, YELLOW_SHIP_LASER)
    }

    def __init__(self, x, y, color, health=100):
        self.x = x
        self.y = y
        self.color = color
        self.health = health
        self.ship_img, self.ship_laser = self.COLOR_MAP[color]
        self.bullets = []
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.cool_down_counter = 0
        self.lost_count = 0
        self.lost = False
        self.shoot_number = 0
        self.powered_shot = False
        self.ctr = 3
        self.iced = False
        self.burn_animation = []
        for i in range(120):
            burn_img = pygame.transform.scale(pygame.image.load(f"c:/Users/Emirhan Ese/VSC Projects/Python Projects/Multiplayer Space War/Assets/burn/1_{i}.png"),
                                              (self.ship_img.get_width(), self.ship_img.get_height())).convert_alpha()
            self.burn_animation.append(burn_img)

    def burn_ship(self):
        current_img = 0
        WIN.blit(self.burn_animation[int(current_img)], (self.x, self.y))
        pygame.display.update()
        current_img += 0.2

    def special_shot(self):
        if self.shoot_number == 5:
            return True

    def powered_shot_bar(self, window):
        pygame.draw.rect(window, (255, 255, 255), (self.x, self.y + self.ship_img.get_height() + 21,
                                                   self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (255, 255, 0), (self.x, self.y + self.ship_img.get_height() + 21,
                                                 self.ship_img.get_width() * (self.shoot_number / 5), 10))

    def health_bar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10,
                                               self.ship_img.get_width(), 10))
        if self.health >= 0:
            pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10,
                                                   self.ship_img.get_width() * (self.health / 100), 10))

    def move(self):
        keys = pygame.key.get_pressed()
        if self.color == "red":
            if not self.iced:
                if keys[pygame.K_w]:
                    if self.y != 0:
                        self.y -= 5
                if keys[pygame.K_s]:
                    if self.y + self.ship_img.get_height() + 35 <= HEIGHT:
                        self.y += 5
                if keys[pygame.K_d]:
                    if self.x <= WIDTH / 2 - 15 - self.ship_img.get_width():
                        self.x += 5
                if keys[pygame.K_a]:
                    if self.x != 0:
                        self.x -= 5

        if self.color == "yellow":
            if keys[pygame.K_UP]:
                if self.y != 0:
                    self.y -= 5
            if keys[pygame.K_DOWN]:
                if self.y + self.ship_img.get_height() + 35 <= HEIGHT:
                    self.y += 5
            if keys[pygame.K_RIGHT]:
                if self.x <= WIDTH - self.ship_img.get_width() - 5:
                    self.x += 5
            if keys[pygame.K_LEFT]:
                if self.x >= WIDTH / 2 + 15:
                    self.x -= 5

    # Important
    def cool_down(self):
        if self.cool_down_counter >= COOLDOWN:
            self.cool_down_counter = 0

        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def move_bullets(self, bullet_velocity, obj):
        self.cool_down()
        for bullet in self.bullets:
            bullet.move(bullet_velocity)
            if bullet.off_screen():
                self.bullets.remove(bullet)
            else:
                if self.color == "red":
                    if bullet.collision(obj):
                        if bullet.laser_img == POWERED_RED_SHIP_LASER:
                            GRENADE_SOUND.play()
                            self.powered_shot = True
                            obj.health -= 20
                            self.bullets.remove(bullet)

                        else:
                            GRENADE_SOUND.play()
                            obj.health -= 10
                            self.bullets.remove(bullet)

                elif self.color == "yellow":
                    if bullet.collision(obj):
                        if bullet.laser_img == POWERED_YELLOW_SHIP_LASER:
                            GRENADE_SOUND.play()
                            self.powered_shot = True
                            obj.health -= 20
                            self.bullets.remove(bullet)

                        else:
                            GRENADE_SOUND.play()
                            obj.health -= 10
                            self.bullets.remove(bullet)

    # Shooting --
    def shoot(self):
        if self.cool_down_counter == 0:
            if self.color == "red":
                if self.shoot_number == 5:
                    bullet = Laser(self.x + self.ship_img.get_width() -
                                   3, self.y + 19, POWERED_RED_SHIP_LASER)
                    self.bullets.append(bullet)

                else:
                    bullet = Laser(
                        self.x + self.ship_img.get_width() - 3, self.y + 19, self.ship_laser)
                    self.bullets.append(bullet)

            if self.color == "yellow":
                if self.shoot_number == 5:
                    bullet2 = Laser(self.x - self.ship_img.get_width() +
                                    18, self.y + 21, POWERED_YELLOW_SHIP_LASER)
                    self.bullets.append(bullet2)

                else:
                    bullet2 = Laser(
                        self.x - self.ship_img.get_width() + 18, self.y + 21, self.ship_laser)
                    self.bullets.append(bullet2)
            GUN_SOUND.play()

            self.cool_down_counter = 1
            if self.shoot_number < 5:
                self.shoot_number += 1
            else:
                self.shoot_number = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for bullet in self.bullets:
            bullet.draw(WIN)


# Important, wichtig
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (int(offset_x), int(offset_y))) != None


FPS = 60
COOLDOWN = 25
clock = pygame.time.Clock()

player1 = Player(100, HEIGHT / 2 - 40, "red")

red_bullet_velocity = 12
player2 = Player(1150, HEIGHT / 2 - 40, "yellow")
yellow_bullet_velocity = -12
pygame.time.set_timer(pygame.USEREVENT, 1000)

lost_count = 0
text = pygame.font.SysFont("comicsans", 60)
title_font = pygame.font.SysFont("comicsans", 50)
title_label = title_font.render("Press 'f' to start the game.", True, WHITE)
meteors = []
health_icons = []

already = False
already2 = False



def red_special_shot():
    for event in pygame.event.get():
        if event.type == pygame.USEREVENT:
            if player1.ctr > 0:
                player2.health -= 6
                player1.ctr -= 1
                player2.burn_ship()
            else:
                player1.powered_shot = False
                player1.ctr = 3


def yellow_special_shot():
    for event in pygame.event.get():
        if event.type == pygame.USEREVENT:
            if player2.ctr > 1:
                player2.ctr -= 1
            else:
                player2.powered_shot = False
                player1.iced = False
                player2.ctr = 3


def winner_text(winner):
    win_text = text.render(f"{winner} has won the game!", True, (255, 0, 0))
    WIN.blit(win_text, (375, HEIGHT / 2 - win_text.get_height() / 2))


def main():
    run = True

    def draw_window():
        WIN.blit(BG, (0, 0))
        pygame.draw.rect(WIN, BLACK, BORDER)

        if len(health_icons) != 0:
            for health in health_icons:
                health.draw(WIN)

        if len(meteors) != 0:
            for meteor in meteors:
                meteor.draw(WIN)
        health_1 = title_font.render(f"Health: {player1.health}", True, WHITE)
        health_2 = title_font.render(f"Health: {player2.health}", True, WHITE)
        if player1.health >= 0:
            WIN.blit(health_1, (10, 10))
        else:
            health_1 = title_font.render(f"Health: 0", True, WHITE)
            WIN.blit(health_1, (10, 10))

        if player2.health >= 0:
            WIN.blit(health_2, (WIDTH - health_2.get_width() - 10, 10))
        else:
            health_2 = title_font.render(f"Health: 0", True, WHITE)
            WIN.blit(health_2, (WIDTH - health_2.get_width() - 10, 10))
        player1.powered_shot_bar(WIN)
        player2.powered_shot_bar(WIN)
        player1.health_bar(WIN)
        player2.health_bar(WIN)

        if player1.lost:
            winner_text("Player 2")
        elif player2.lost:
            winner_text("Player 1")

        player1.draw(WIN), player2.draw(WIN)

        pygame.display.update()

    while run:
        keys = pygame.key.get_pressed()
        clock.tick(FPS)
        draw_window()

        if player1.health >= 0 and player2.health >= 0:
            if len(meteors) == 0:
                rand_num = randint(1, 100)

                if rand_num == 1:
                    left_x = randrange(0, BORDER.x - METEOR.get_width())
                    left_y = randrange(-100, -25)
                    right_x = randrange(
                        BORDER.x + 10, WIDTH - METEOR.get_width())
                    right_y = randrange(-100, -25)

                    meteor1 = Meteor(left_x, left_y)
                    meteor2 = Meteor(right_x, right_y)

                    meteors.append(meteor1)
                    meteors.append(meteor2)
            if len(health_icons) < 2:
                rand_num2 = randint(1, 500)

                if rand_num2 == 1:
                    rand_choice = randint(1, 2)
                    global already
                    global already2
                    if rand_choice == 1 and not already:
                        already2 = False
                        x = randrange(0, BORDER.x - METEOR.get_width() - 16)
                        y = randrange(0, HEIGHT - HEALTH_ICON.get_height())
                        health = Health(x, y)
                        health_icons.append(health)
                        already = True

                    elif rand_choice == 2 and not already2:
                        already = False
                        x = randrange(BORDER.x + 10, WIDTH -
                                      METEOR.get_width() - 16)
                        y = randrange(0, HEIGHT - HEALTH_ICON.get_height())
                        health = Health(x, y)
                        health_icons.append(health)
                        already2 = True

            for meteor in meteors:
                meteor.move(3)

                if collide(meteor, player1):
                    meteors.remove(meteor)
                    player1.health -= 5

                if collide(meteor, player2):
                    meteors.remove(meteor)
                    player2.health -= 5

        for health in health_icons:
            if collide(health, player1):
                health_icons.remove(health)
                if player1.health <= 70:
                    player1.health += 30
                elif player1.health > 70 and player1.health < 100:
                    player1.health = 100
                else:
                    player1.shoot_number += 1

            if collide(health, player2):
                health_icons.remove(health)
                if player2.health <= 70:
                    player2.health += 30

                elif player2.health > 70 and player2.health < 100:
                    player2.health = 100
                else:
                    player2.shoot_number += 1

        if player1.health <= 0:
            player1.lost = True
            player1.lost_count += 1
            if player1.lost_count > FPS * 3:
                run = False

            else:
                continue
        elif player2.health <= 0:
            player2.lost = True
            player2.lost_count += 1
            if player2.lost_count > FPS * 3:
                run = False

            else:
                continue

        if keys[pygame.K_SPACE]:
            if not player1.iced:
                player1.shoot()
        if keys[pygame.K_l]:
            player2.shoot()

        player1.move()
        player2.move()
        player1.move_bullets(red_bullet_velocity, player2)
        if player1.powered_shot:
            red_special_shot()
        player2.move_bullets(yellow_bullet_velocity, player1)
        if player2.powered_shot:
            player1.iced = True
            yellow_special_shot()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

    pygame.quit()


def draw_main_menu():
    WIN.blit(title_label, (WIDTH / 2 - 215, HEIGHT /
                           2 - title_label.get_height() / 2))
    pygame.display.update()


def main_menu():
    run = True

    while run:
        draw_main_menu()
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if keys[pygame.K_f]:
                main()
    pygame.quit()


main_menu()
