import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
import pygame
pygame.init()
print("Pygame initialized successfully")
screen = pygame.display.set_mode((640, 480))
print("Display set")
pygame.quit()