# -*- coding: utf-8 -*-
#/usr/bin/python



from chat import ChatClientProtocol
import pygame
from pygame.locals import *

def main():
        
    #Initialize
    pygame.init()
    
    font = pygame.font.SysFont("arial", 16);
    font_height = font.get_linesize()
    


    #Display
    SCREEN_SIZE = (800, 600)
    screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32)
    pygame.display.set_caption("Simple Galaktia Client")

    #Entities
    #set up variables
    
    event_text = [""]

    #ACTION

        #Assign 
    clock = pygame.time.Clock()
    keepGoing = True
    string = ""

        #Loop
    while keepGoing:

        #Time
        clock.tick(30)

        #Events
        for event in pygame.event.get():
            if event.type == QUIT:
                keepGoing = False
            elif event.type == KEYDOWN:
                if event.key == K_RETURN:
                    
                    event_text.append(string)
                    event_text[-1] = ""
                    event_text = event_text[-SCREEN_SIZE[1]/font_height:]
                    string = ""
                else:
                    string += pygame.key.name(event.key)
                    event_text[-1] = string

        #Refresh screen
        screen.fill((255, 255, 255))
        pygame.draw.line(screen, (0, 0, 0),(0,SCREEN_SIZE[1]-font_height-1), (SCREEN_SIZE[0],SCREEN_SIZE[1]-font_height-1), 1)
        y = SCREEN_SIZE[1]-font_height
        for text in reversed(event_text):
            screen.blit( font.render(text, True, (0, 0, 0)), (0, y) )
            y-=font_height
        
        pygame.display.flip()
        
    return

if __name__ == "__main__":
    main()