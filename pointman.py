import numpy as np
from math import *
import sys

import pygame

WHITE =     (255, 255, 255)
BLUE =      (  0,   0, 255)
GREEN =     (  0, 255,   0, 128)
RED =       (255,   0,   0)
TEXTCOLOR = (  0,   0,  0)
(width, height) = (200, 300)

running = True

def main():
    global running, screen

    pointFilename = sys.argv[1]
    SCREEN_WIDTH = 1300
    SCREEN_HEIGHT = 1300
    circle_radius = 3
    conversion_ratio = 100
    selectedPointIndex = None
    offset_x = 0
    offset_y = 0
    mouse_x = 0
    mouse_y = 0
    FPS = 60
    sideBufferMeters = 4 #we want a 5% total buffer added
    mapPixeltoMeterRatio = 20 #or 33?

    with open(pointFilename, "r") as pointFile:
        pointLines = pointFile.readlines()
    
    points = np.array([line.split(",")[:2] for line in pointLines], dtype=float)

    #         x      y
    #  max [[maxX, maxY],
    #  min  [minX, minY]]
    sidePoints = np.array([
        [np.max(points[:,0]), np.max(points[:,1])],
        [np.min(points[:,0]), np.min(points[:,1])]
    ])
    
    pathDims = np.array(sidePoints[0,:] - sidePoints[1,:])
    print(sidePoints)
    print(pathDims)

    #screentransfer = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
    conversion_ratio = min((SCREEN_WIDTH/(pathDims[0]+sideBufferMeters)), (SCREEN_HEIGHT/(pathDims[1]+sideBufferMeters)))
    print(conversion_ratio)
    screentransfer = sidePoints[1] - .5 * sideBufferMeters
    points = (points - screentransfer) * conversion_ratio

    mapImg = pygame.image.load('maps/kelley-clean.png')
    mapDims = np.array(mapImg.get_size())
    mapScaling = mapDims * (conversion_ratio/mapPixeltoMeterRatio)
    print(mapDims)
    print(mapScaling)
    mapPosition = [-2950, -350]# -1 * sidePoints[1] * mapPixeltoMeterRatio#- .5 * sideBufferMeters
    mapPosition = (((sidePoints[1])/mapPixeltoMeterRatio) + sideBufferMeters * .5) * conversion_ratio #sidePoints[1] * mapPixeltoMeterRatio
    #mapPosition[0] += pathDims[0] * (conversion_ratio/mapPixeltoMeterRatio)
    mapPosition[1] -= pathDims[1] * (conversion_ratio/mapPixeltoMeterRatio)
    mapPositionAdded = [0, 0]#pixels
    print(mapPosition)
    mapImg = pygame.transform.flip(mapImg, 0, 1)
    mapImg = pygame.transform.scale(mapImg, (int(mapScaling[0]), int(mapScaling[1])))


    screen = pygame.init()
    screen = pygame.display.set_mode((int(SCREEN_WIDTH), int(SCREEN_HEIGHT)))
    # - mainloop -

    clock = pygame.time.Clock()

    running = True

    mode = 1
    reverse = 0
    lastCircle = 0
    move_radius = 30
    min_radius = 10
    move_speed = 1
    usedMultiplier = 1.2
    movementExponent = 1.6
    map_speed = conversion_ratio/mapPixeltoMeterRatio
    normSlope = lambda p1, p2, d : ((p1[0]-p2[0])/d**1.6, (p1[1]-p2[1])/d**1.6)
    circleSurface = pygame.Surface((move_radius, move_radius), pygame.SRCALPHA)
    usedCircles = []
    circleSlopes = []
    while running:

        # - events -
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    mode = not mode
                if event.key == pygame.K_UP:
                    mapPositionAdded[1] -= map_speed
                if event.key == pygame.K_DOWN:
                    mapPositionAdded[1] += map_speed
                if event.key == pygame.K_RIGHT:
                    mapPositionAdded[0] += map_speed
                if event.key == pygame.K_LEFT:
                    mapPositionAdded[0] -= map_speed
                print(mapPosition)

            KEYS = pygame.key.get_pressed()
            if KEYS[pygame.K_LSHIFT]:
                reverse = 1
            else:
                reverse = 0

            if mode == 0:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:            
                        min_dist_circle = 1000000
                        for cdx in range(len(points)):
                                d = np.clip(np.linalg.norm(np.asarray(event.pos)-points[cdx]), min_radius, move_radius)
                                
                                if d < min_dist_circle and d < (2* circle_radius):
                                    min_dist_circle = d
                                    selectedPointIndex = cdx

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:            
                        selectedPointIndex = None

                elif event.type == pygame.MOUSEMOTION:
                    if selectedPointIndex != None:
                        mouse_x, mouse_y = event.pos
                        points[selectedPointIndex][0] = mouse_x + offset_x
                        points[selectedPointIndex][1] = mouse_y + offset_y
            elif mode == 1:
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:            
                        selectedPointIndex = None

                elif event.type == pygame.MOUSEMOTION:
                    mouse_x, mouse_y = event.pos
                    if pygame.mouse.get_pressed()[0]:

                        usedCircles = []
                        circleSlopes = []
                        min_dist_circle = move_radius
                        for cdx in range(len(points)):
                            d = np.linalg.norm(np.asarray(event.pos)-points[cdx])
                            if d < move_radius:
                                usedCircles.append(cdx)
                                circleSlopes.append(normSlope(event.pos, points[cdx], d))
                                
                            #elif cdx in usedCircles and d >= move_radius * usedMultiplier:
                                #usedCircles.remove(cdx)
                        #points[selectedPointIndex][0] = mouse_x + offset_x
                        #points[selectedPointIndex][1] = mouse_y + offset_y
        if pygame.mouse.get_pressed()[0]:
            for idx in range(len(usedCircles)):
                points[usedCircles[idx]][0] += circleSlopes[idx][0] * move_speed * (-1 if reverse else 1)
                points[usedCircles[idx]][1] += circleSlopes[idx][1] * move_speed * (-1 if reverse else 1)

        screen.fill(WHITE)
        mapPositionFrame = mapPosition + mapPositionAdded
        screen.blit(mapImg, (mapPositionFrame[0], mapPositionFrame[1]))

        for p in points:
            pygame.draw.circle(screen, RED, (int(p[0]),int(p[1])), int(circle_radius))

        circleSurface.fill((0, 0, 0, 0))
        screen.blit(circleSurface, (mouse_x, mouse_y))
        pygame.draw.circle(circleSurface, GREEN, (int(move_radius/2), int(move_radius/2)), move_radius)

        pygame.display.flip()

        clock.tick(FPS)

    with open(pointFilename.split(".")[0]+".csv", "w+") as newPointFile:
        outpoints = (points / conversion_ratio) + screentransfer
        for pdx in range(len(outpoints)):
            newPointFile.write("{},{},0.0,0.0\n".format(str(outpoints[pdx][0]),str(outpoints[pdx][1])))
        print("WROTE THE FILE")

if __name__ == "__main__":
    main()