import random
import pygame
pygame.init()

from neuro_collector.client import NeuroClient


TIME_BLINK_ON_SCREEN = 500
MIN_TIME_BETWEEN_BLINKS = 1000
MAX_TIME_BETWEEN_BLINKS = 5000


client = NeuroClient('blink')

screen = pygame.display.set_mode((640, 480), pygame.FULLSCREEN)
clock = pygame.time.Clock()

halt = False
blink_on_screen = False

font = pygame.font.SysFont('Arial', 72)
text = font.render('BLINK', True, (0, 0, 0))


def get_random_ms(min_ms=MIN_TIME_BETWEEN_BLINKS,
                  max_ms=MAX_TIME_BETWEEN_BLINKS):
    return random.randint(min_ms, max_ms)


pygame.time.set_timer(pygame.USEREVENT, get_random_ms())


while not halt:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            halt = True
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            halt = True
        elif event.type == pygame.USEREVENT:
            if blink_on_screen:
                blink_on_screen = False
                pygame.time.set_timer(pygame.USEREVENT, get_random_ms())
                client.record_sensors({'blink_on_screen': 0})
            else:
                blink_on_screen = True
                pygame.time.set_timer(pygame.USEREVENT, TIME_BLINK_ON_SCREEN)
                client.record_sensors({'blink_on_screen': 1})

    screen.fill((255, 255, 255))

    if blink_on_screen:
        screen.blit(text, (320 - text.get_width() // 2,
                           240 - text.get_height() // 2))

    pygame.display.flip()
    clock.tick(60)
