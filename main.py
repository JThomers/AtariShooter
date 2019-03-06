# TODO
#  Add screen to choose difficulty (number of zombies, speed, etc.
#  Score system?
#  Limit ammo? Add ammo pickup?
#  Different weapon types? Shotgun, grenade, etc?

import platform
import pygame
import random
import sys
from pygame.locals import *

# ====================
# INIT
# ====================

# Constants
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Screen size
hSize = 1280
vSize = 800

# Difficulty variables
numZombies = 8

# Setup window
windowSurface = pygame.display.set_mode((hSize, vSize), 0, 32)

# Startup Pygame
pygame.init()

# Create basic font
basicFont = pygame.font.SysFont(None, 48)

# Name window
pygame.display.set_caption('Teh Zombeez')

# Sprites
survivorIMG = pygame.image.load('images/survivor.png').convert_alpha()
zombieIMG = pygame.image.load('images/zombie.png').convert_alpha()
bulletIMG = pygame.image.load('images/projectile.png').convert_alpha()

# Create sprite groups
allSpritesGroup = pygame.sprite.Group()
zombiesGroup = pygame.sprite.Group()
bulletsGroup = pygame.sprite.Group()

# Flags to determine win/loss
loseFlag = False
winFlag = False

# ====================
# CLASS DEFINITIONS
# ====================
# Player
class Survivor(pygame.sprite.Sprite):
    def __init__(self, imgFile=survivorIMG, xStart=0, yStart=0, speed=0):
        super().__init__()
        self.image = pygame.transform.scale(imgFile, (32, 32))
        self.rect = self.image.get_rect(center=(xStart, yStart))  # Get rect for image
        self.xStart, self.yStart, self.speed = xStart, yStart, speed

    def moveKeyboardUDLR(self, pressedKey):
        if pressedKey[pygame.K_UP] or pressedKey[pygame.K_w]:
            self.rect.y -= self.speed
        if pressedKey[pygame.K_DOWN] or pressedKey[pygame.K_s]:
            self.rect.y += self.speed
        if pressedKey[pygame.K_LEFT] or pressedKey[pygame.K_a]:
            self.rect.x -= self.speed
        if pressedKey[pygame.K_RIGHT] or pressedKey[pygame.K_d]:
            self.rect.x += self.speed
        self.rect = fixOutOfBounds(self.rect)

    def shoot(self):
        bulletX = self.rect.x
        bulletY = self.rect.y
        newBullet = Bullet(bulletX, bulletY)
        allSpritesGroup.add(newBullet)
        bulletsGroup.add(newBullet)


# Enemy
class Zombie(pygame.sprite.Sprite):
    def __init__(self, xStart=hSize/2, yStart=vSize/2, xSpeed=0, ySpeed=0, imgFile=zombieIMG):
        super().__init__()
        self.image = pygame.transform.scale(imgFile, (32, 32))
        self.rect = self.image.get_rect(center=(xStart, yStart))  # Get rect for image
        self.xStart, self.yStart, self.xSpeed, self.ySpeed = xStart, yStart, xSpeed, ySpeed

    # Pick what direction it moves
    def move(self):
        self.rect.x += self.xSpeed
        self.rect.y += self.ySpeed
        if self.rect.left < 0 or self.rect.right > hSize:
            self.xSpeed *= -1
        if self.rect.top < 0 or self.rect.bottom > vSize:
            self.ySpeed *= -1
        self.rect = fixOutOfBounds(self.rect)

    # Bounce off enemies
    def collide(self, enemySprite2):
        if self.rect.colliderect(enemySprite2.rect):
            self.xSpeed *= -1
            self.ySpeed *= -1

    # If shot, destroy
    def destroy(self):
        self.kill()


# Bullet
class Bullet(pygame.sprite.Sprite):
    def __init__(self, xStart, yStart, xSpeed=20, imgFile=bulletIMG):
        super().__init__()
        self.image = pygame.transform.scale(imgFile, (8, 8))
        self.rect = self.image.get_rect(center=(xStart, yStart))
        self.xStart, self.yStart, self.xSpeed = xStart, yStart, xSpeed

    def move(self):
        self.rect.x += self.xSpeed
        # Check if bullet is off the screen; if so, destroy it.
        if self.rect.x > hSize:
            self.kill()

    # Check if bullet collides with another defined sprite
    def isCollidedWith(self, sprite):
        return self.rect.colliderect(sprite.rect)


# ==================================
# Secondary Function Definitions
# ==================================
# Stop rect from going off the screen
def fixOutOfBounds(rect):
    if rect.left < 0:
        rect.left = 0
    elif rect.right > hSize:
        rect.right = hSize
    if rect.top < 0:
        rect.top = 0
    elif rect.bottom > vSize:
        rect.bottom = vSize
    return rect


# ==================================
# Main Function
# ==================================
def main():
    global winFlag
    global loseFlag
    gunLimitFrames = 0
    score = 0

    # Create survivor
    survivor = Survivor(survivorIMG, 32, 32, 5)
    allSpritesGroup.add(survivor)

    # Create zombies
    for i in range(numZombies):
        xPos = random.randint(32, hSize - 32)
        yPos = random.randint(32, vSize - 32)
        xSpeed = random.randint(-5, 5)
        ySpeed = random.randint(-5, 5)
        newZombie = Zombie(xPos, yPos, xSpeed, ySpeed)
        zombiesGroup.add(newZombie)
        allSpritesGroup.add(newZombie)

    # Setup clock for game loop speed
    clock = pygame.time.Clock()

    # Check OS to set key repeat values
    if platform.system() == "Darwin":  # Darwin = macOS
        print("Using macOS config.")
        pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # Runs REALLY slow unless in full-screen mode on Mac
        pygame.key.set_repeat(5, 10)  # This works on Mac, but is likely too fast for PC.
    elif platform.system() == "Windows":
        print("Using Windows config.")
        pygame.key.set_repeat(50, 100)  # These work well on my Windows VM, but I couldn't test on a real machine
    else:
        print("Using catchall config.")
        pygame.key.set_repeat(50, 100)  # Catchall. Better than an error...

    # =====================
    # Main Game Loop
    # =====================
    while True:
        clock.tick(30)

        # Limit the fire rate of the gun to every 10 frames
        if 0 < gunLimitFrames < 11: # Don't start the timer until the user shoots
            gunLimitFrames += 1
        elif gunLimitFrames >= 11:
            gunLimitFrames = 0

        for event in pygame.event.get():
            # Get the list of all keys that are pressed
            pressed = pygame.key.get_pressed()

            # if the event is quit, then exit the game
            if event.type == QUIT or pressed[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit()

            # Shoot the gun and start the gunLimitFrames timer
            if pressed[pygame.K_SPACE] and gunLimitFrames == 0:
                survivor.shoot()
                gunLimitFrames += 1

            # Keep processing events if not lost or won
            if not loseFlag or winFlag:
                survivor.moveKeyboardUDLR(pressed)

        # Move zombies and bullets
        for z in zombiesGroup:
            z.move()
        for bullet in bulletsGroup:
            bullet.move()

        # Set Win Condition
        if len(zombiesGroup) == 0:
            winFlag = True
            text = basicFont.render("You Win!", True, WHITE)

        # Set Lose Condition
        for z in zombiesGroup:
            if survivor.rect.colliderect(z):
                loseFlag = True
                text = basicFont.render("You lose", True, WHITE)

        # For each zombie, see if it intersects with another zombie. If so reverse direction
        for z in zombiesGroup:
            for z2 in zombiesGroup:
                if z != z2:
                    z.collide(z2)

        # For each zombie, see if it intersects with a bullet. If so, destroy the zombie
        for z in zombiesGroup:
            for b in bulletsGroup:
                if b.isCollidedWith(z):
                    z.destroy()

        # Draw win or lose screen
        if winFlag or loseFlag:
            text_rect = text.get_rect()
            text_x = windowSurface.get_width() / 2 - text_rect.width / 2
            text_y = windowSurface.get_height() / 2 - text_rect.height / 2
            windowSurface.blit(text, [text_x, text_y])
            pygame.display.update()
        else:
            # Draw the game
            windowSurface.fill(BLACK)
            allSpritesGroup.draw(windowSurface)
            pygame.display.update()


main()
