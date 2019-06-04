import numpy as np
from math import *

import pygame

WHITE =     (255, 255, 255)
BLUE =      (  0,   0, 255)
GREEN =     (  0, 255,   0)
RED =       (255,   0,   0)
TEXTCOLOR = (  0,   0,  0)
(width, height) = (200, 300)

running = True

def main():
    global running, screen

    pointFilename = "paths/path-new.csv"
    SCREEN_SIZE = 1000
    with open(pointFilename, "r") as pointFile:
        pointLines = pointFile.readlines()
    
    points = np.array([line.split(",")[:2] for line in pointLines], dtype=float)
    origin = points[0]
    screentransfer = np.array([SCREEN_SIZE/1.3, SCREEN_SIZE/2])

    circle_radius = 3
    conversion_ratio = 100
    points = ((points-origin) * conversion_ratio)+screentransfer

    mapImg = pygame.image.load('maps/kelley.png')
    mapImg = pygame.transform.flip(mapImg, 1, 1)
    mapImg = pygame.transform.scale(mapImg, (conversion_ratio,conversion_ratio))
    print(points[:10])

    dragging = False
    selectedPointIndex = None
    offset_x = 0
    offset_y = 0
    mouse_x = 0
    mouse_y = 0
    FPS = 30

    screen = pygame.init()
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
    # - mainloop -

    clock = pygame.time.Clock()

    running = True

    while running:

        # - events -

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:            
                    for cdx in range(len(points)):
                            if np.linalg.norm(np.asarray(event.pos)-points[cdx]) <= circle_radius:
                                selectedPointIndex = cdx

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:            
                    selectedPointIndex = None

            elif event.type == pygame.MOUSEMOTION:
                if selectedPointIndex != None:
                    mouse_x, mouse_y = event.pos
                    points[selectedPointIndex][0] = mouse_x + offset_x
                    points[selectedPointIndex][1] = mouse_y + offset_y

            screen.fill(WHITE)
            screen.blit(mapImg, (0, 0))

            for p in points:
                pygame.draw.circle(screen, RED, (int(p[0]),int(p[1])), int(circle_radius))

            pygame.display.flip()

            clock.tick(FPS)

    with open(pointFilename.split(".")[0]+".csv", "w+") as newPointFile:
        outpoints = ((points-screentransfer) / conversion_ratio) + origin
        for pdx in range(len(outpoints)):
            newPointFile.write("{},{},0.0,0.0\n".format(str(outpoints[pdx][0]),str(outpoints[pdx][1])))
        print("WROTE THE FILE")

if __name__ == "__main__":
    main()