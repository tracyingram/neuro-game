import csv
import os
import random
import sys

import pygame
pygame.init()

from neuro_collector.client import NeuroClient
from neuro_collector.clients.symptoms.wrap import render_wrap


TIME_SYMPTOM_ON_SCREEN = 3000
TIME_SYMPTOM_OFF_SCREEN = 1000


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
symptom_on_screen = False

font = pygame.font.SysFont('Arial', 48)

explanation_font = pygame.font.SysFont('Arial', 30)
explanation = explanation_font.render('Do you experience...', True, (0, 0, 0))


pygame.time.set_timer(pygame.USEREVENT, TIME_SYMPTOM_OFF_SCREEN)

while not halt:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or not have_more_symptoms():
            halt = True
            break
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            halt = True
            break
        elif event.type == pygame.USEREVENT:
            if symptom_on_screen:
                symptom_on_screen = False
                pygame.time.set_timer(pygame.USEREVENT, TIME_SYMPTOM_OFF_SCREEN)
                client.record_sensors({'symptom': '', 'group': ''})
            else:
                symptom_on_screen = True
                group, symptom = get_next_symptom()
                client.record_sensors({'symptom': symptom, 'group': group})

                pygame.time.set_timer(pygame.USEREVENT, TIME_SYMPTOM_ON_SCREEN)
                text = render_wrap(symptom, font, 620)

    screen.fill((255, 255, 255))
    screen.blit(explanation, (320 - explanation.get_width() // 2, 0))

    if symptom_on_screen:
        screen.blit(text, (320 - text.get_width() // 2,
                           240 - text.get_height() // 2))

    pygame.display.flip()
    clock.tick(60)
else:
    sys.exit(0)
