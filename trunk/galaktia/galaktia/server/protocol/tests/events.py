# -*- coding: utf-8 -*-
import pygame # PROHIBIDO USAR PYGAME!!!
              # SE LE CORTARA LA CABEZA AL QUE IMPORTE ESTA DEPENDENCIA
from pygame.locals import *
from sys import exit
pygame.init()
SCREEN_SIZE = (800, 600)
screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32)
font = pygame.font.SysFont("arial", 16);
font_height = font.get_linesize()
event_text = []
while True:
    event = pygame.event.wait()
    event_text.append(str(event))
    event_text = event_text[-SCREEN_SIZE[1]/font_height:]
    if event.type == QUIT:
        exit()
    screen.fill((255, 255, 255))
    y = SCREEN_SIZE[1]-font_height
    for text in reversed(event_text):
        screen.blit( font.render(text, True, (0, 0, 0)), (0, y) )
        y-=font_height
    pygame.display.update()
