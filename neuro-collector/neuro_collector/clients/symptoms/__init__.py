import csv
import os
import random
import sys

import pygame
pygame.init()

from neuro_collector.client import NeuroClient
from neuro_collector.clients.symptoms.wrap import render_wrap

# CONFIGURE TIME HERE
TIME_SYMPTOM_ON_SCREEN = 3000
TIME_BLINK_ON_SCREEN = 500
TIME_SCREEN_BLANK = 1000
# DON'T CHANGE ANY CODE BELOW


# Enum used to identify unique screens
DISPLAY_BLANK = 0
DISPLAY_SYMPTOM = 1
DISPLAY_BLINK = 2


curdir = os.path.dirname(__file__)
path = os.path.join(curdir, 'symptoms.csv')
with open(path) as fp:
    reader = csv.reader(fp)
    symptoms = [row[:2] for row in reader]


_symptoms_left = list(symptoms)
def get_next_symptom():
    random.shuffle(_symptoms_left)
    group, symptom = _symptoms_left.pop()
    return group, symptom


def have_more_symptoms():
    return bool(_symptoms_left)


client = NeuroClient('symptoms')

screen = pygame.display.set_mode((640, 480), pygame.FULLSCREEN)
clock = pygame.time.Clock()

halt = False
display_cur = DISPLAY_BLANK
display_next = DISPLAY_SYMPTOM

symptom_font = pygame.font.SysFont('Arial', 48)

explanation_font = pygame.font.SysFont('Arial', 30)
explanation = explanation_font.render('Do you experience...', True, (0, 0, 0))

blink_font = pygame.font.SysFont('Arial', 72)
blink_text = blink_font.render('BLINK', True, (0, 0, 0))


pygame.time.set_timer(pygame.USEREVENT, TIME_SCREEN_BLANK)

try:
    while not halt:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or not have_more_symptoms():
                halt = True
                break
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                halt = True
                break
            elif event.type == pygame.USEREVENT:
                if display_cur == DISPLAY_BLANK:
                    display_cur = display_next

                    if display_cur == DISPLAY_SYMPTOM:
                        group, symptom = get_next_symptom()
                        client.record_sensors({'symptom': symptom, 'group': group})
                        symptom_text = render_wrap(symptom, symptom_font, 620)

                        display_next = DISPLAY_BLINK
                        pygame.time.set_timer(pygame.USEREVENT,
                                              TIME_SYMPTOM_ON_SCREEN)
                    else:
                        client.record_sensors({'blink': 'blink'})

                        display_next = DISPLAY_SYMPTOM
                        pygame.time.set_timer(pygame.USEREVENT,
                                              TIME_BLINK_ON_SCREEN)

                else:
                    display_cur = DISPLAY_BLANK
                    pygame.time.set_timer(pygame.USEREVENT, TIME_SCREEN_BLANK)
                    client.record_sensors({'symptom': '', 'group': '', 'blink': ''})

        screen.fill((255, 255, 255))

        if display_cur == DISPLAY_SYMPTOM:
            screen.blit(explanation, (320 - explanation.get_width() // 2, 0))
            screen.blit(symptom_text, (320 - symptom_text.get_width() // 2,
                                       240 - symptom_text.get_height() // 2))
        elif display_cur == DISPLAY_BLINK:
            screen.blit(blink_text, (320 - blink_text.get_width() // 2,
                                     240 - blink_text.get_height() // 2))

        pygame.display.flip()
        clock.tick(60)
    else:
        sys.exit(0)
finally:
    try:
        pygame.display.set_mode((640, 480))
    except Exception:
        pass
