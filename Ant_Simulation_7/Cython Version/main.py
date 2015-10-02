# -*- coding: utf-8 -*-
'''

[Ant Simulation - a small simulation of an anthill with Pygame]
Copyright (C) [2012]  [Malte Lichtenberg, Lucas Tittmann]

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but 
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
for more details.

You should have received a copy of the GNU General Public License along with this 
program; if not, see <http://www.gnu.org/licenses/>.

'''

import pygame
from pygame.locals import *
import sys
import help_functions
import string

# just for testing and setting a seed
import time
import numpy as np
import os
#import pycallgraph
import lib
#import cPickle as pickle


def main(size = "small", 
         map_name = None, 
         make_stat = False, 
         break_cond = 0, 
         intervall = 50,
         epsilon = 0.01,
         fast_start = True,
         FPS = 60):
    # possible sizes are "small" and "big"
    # map_name for example: "map1.txt"

    #5help_functions.inc_priority()
    my_map = None
    if map_name:
        my_map = string.split(help_functions.load_map(map_name),"\n")
        for line in my_map:
            ind = string.find(line,"board_size")
            if ind != -1:
                # there is a order to change board_size in my_map
                if string.find(line,"small") != -1:
                    size = "small"
                elif string.find(line,"big") != -1:
                    size = "big"
                else:
                    print "Strange board_size in my_map: ", line
                break

    size_in_px = 300
    if size == "big":
        size_in_px = 600
    
    fieldSize       = (size_in_px,size_in_px)
    realfps = 0
    log = []

    pygame.init()

    help_functions.seticon("src/icon.bmp")
    
    # Loading screen and pictures
    if fieldSize[0] == 300:
        # size_in_px of menu picture makes the strange values
        screen_size     = [size_in_px,size_in_px+39]
        screen = pygame.display.set_mode(screen_size)
        logo = pygame . image . load ("src/small/logo_small.png") . convert()
        pos = [0,39]
    elif fieldSize[0] == 600:
        # size_in_px of menu picture makes the strange values
        screen_size     = [size_in_px,size_in_px+79]
        screen = pygame.display.set_mode(screen_size)
        logo = pygame . image . load ("src/big/logo_big.png") . convert()
        pos = [0,79]
    
    screen.blit ( logo , pos)
    pygame.display.set_caption("Ant Simulation")
    pygame.display.flip()

    # calculate field size with menu in front; pos[1] = height of menu
    newfieldSize = (fieldSize[0],fieldSize[1] + pos[1])
    backround = pygame.Surface(newfieldSize)
    backround.fill( (255, 215, 0) )
    
    # Loop until the user clicks the close button.
    not_done = [True]
    stop = False    
    
    print "Constructing board..."
    t = time.clock()            
    myMenu = lib.Menu(screen, size)
    myMenu.draw()
    # ugly hack with not_done to have the possibility to shut the game from within
    # used just in Ants.go_home
#    pickle.dump( lib.Board(fieldSize), open( "board.p", "wb" ) )
#    myBoard = pickle.load( open( "board.p", "rb" ) )

    myBoard = lib.Board(screen, fieldSize, fast_start)
    myBoard.individualize(not_done, backround, my_map)   
    
    myMenu.set_board(myBoard)
    print "Construction completed. It took " + str(round(time.clock() - t, 2))\
        + "s to boot."
    
    
    clock = pygame.time.Clock()
    
    screen.blit( backround, pos )
    pygame.display.flip()
    
    # -------- Main Program Loop -----------
    while not_done[0]:
        for event in pygame.event.get(): # User did something
            if event.type == pygame.QUIT: # If user clicked close
                not_done[0]=False # Flag that we are done so we exit this loop
            elif event.type == pygame.MOUSEBUTTONDOWN:
                coord = (pygame.mouse.get_pos())
                myMenu.mouse_down_action(coord, event.button)
            elif event.type == pygame.MOUSEBUTTONUP:
                pass
				#myMenu.mouse_up_action(pygame.mouse.get_pos())
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    stop = not stop
                    if stop:
                        print "Game is stopped."
                    else:
                        print "Game continues."
                key = pygame.key.get_pressed()
                if key[K_n]:
                    if key[K_LSHIFT]:
                        main(size = "big")
                        sys.exit(1)
                    else:
                        main(size= "small")
                        sys.exit(1)
                if key[K_m]:
                    main(map_name = map_name)
                    sys.exit(1)
    
        pygame.event.pump()
        # update the screen
        realfps -= time.clock()

        if not stop:
                myBoard.update ( )
                myBoard.draw_board( )

        clock.tick(FPS)

        # to measure real_fps
#        realfps += time.clock()
#        if myBoard.round_cnt%500==0:
#            print map_name, " runs at ", realfps/.5, "ms on the Main()."
#            realfps = 0

        # to create a graph:
        if make_stat and myBoard.round_cnt%intervall == 0:
            best_perc = round(myBoard.shortest_way_found_until_now/myBoard.best_solution_length,4)
            log.append(best_perc)
            
            if break_cond != 0:
                if best_perc -1 < epsilon:
                    cnt = myBoard.round_cnt
                    while cnt < break_cond:
                        log.append(1)
                        cnt += intervall
                    return [log,(myBoard.round_cnt, myBoard.way_found_first_time, 1)]
                elif myBoard.round_cnt == break_cond:
                    # if shortest way not found return 0 for shortest way
                    return [log,(0, myBoard.way_found_first_time, best_perc)]
#                    return [log,(myBoard.round_cnt, myBoard.way_found_first_time, best_perc)]
    
    pygame.quit()


def engine(size = "small", 
         map_name = None, 
         make_stat = False, 
         break_cond = 0, 
         intervall = 50,
         epsilon = 0.01,
         fast_start = True,
         FPS = 60):
    # possible sizes are "small" and "big"
    # map_name for example: "map1.txt"

    #5help_functions.inc_priority()
    my_map = None
    if map_name:
        my_map = string.split(help_functions.load_map(map_name),"\n")
        for line in my_map:
            ind = string.find(line,"board_size")
            if ind != -1:
                # there is a order to change board_size in my_map
                if string.find(line,"small") != -1:
                    size = "small"
                elif string.find(line,"big") != -1:
                    size = "big"
                else:
                    print "Strange board_size in my_map: ", line
                break

    size_in_px = 300
    if size == "big":
        size_in_px = 600
    
    fieldSize       = (size_in_px,size_in_px)
    log = []
    
    pygame.init()

    # calculate field size with menu in front; pos[1] = height of menu
    
    # Loop until the user clicks the close button.
    not_done = [True]
    stop = False    
    
    print "Constructing board..."
    t = time.clock()            
    # ugly hack with not_done to have the possibility to shut the game from within
    # used just in Ants.go_home
#    pickle.dump( lib.Board(fieldSize), open( "board.p", "wb" ) )
#    myBoard = pickle.load( open( "board.p", "rb" ) )

    myBoard = lib.Board(None, fieldSize, fast_start)
    myBoard.individualize(not_done, None, my_map)   
    
    print "Construction completed. It took " + str(round(time.clock() - t, 2))\
        + "s to boot."
    
    
    clock = pygame.time.Clock()
    
    # -------- Main Program Loop -----------
    while not_done[0]:
        for event in pygame.event.get(): # User did something
            if event.type == pygame.QUIT: # If user clicked close
                not_done[0]=False # Flag that we are done so we exit this loop
            elif event.type == pygame.MOUSEBUTTONDOWN:
                coord = (pygame.mouse.get_pos())
                myMenu.mouse_down_action(coord, event.button)
            elif event.type == pygame.MOUSEBUTTONUP:
                pass
				#myMenu.mouse_up_action(pygame.mouse.get_pos())
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    stop = not stop
                    if stop:
                        print "Game is stopped."
                    else:
                        print "Game continues."
                key = pygame.key.get_pressed()
                if key[K_n]:
                    if key[K_LSHIFT]:
                        main(size = "big")
                        sys.exit(1)
                    else:
                        main(size= "small")
                        sys.exit(1)
                if key[K_m]:
                    main(map_name = map_name)
                    sys.exit(1)
    
        pygame.event.pump()
        # update the screen

        if not stop:
                myBoard.update ( )

        clock.tick(FPS)

        # to measure real_fps
#        realfps += time.clock()
#        if myBoard.round_cnt%500==0:
#            print map_name, " runs at ", realfps/.5, "ms on the Main()."
#            realfps = 0

        # to create a graph:
        if make_stat and myBoard.round_cnt%intervall == 0:
            best_perc = round(myBoard.shortest_way_found_until_now/myBoard.best_solution_length,4)
            log.append(best_perc)
            
            if break_cond != 0:
                if best_perc -1 < epsilon:
                    cnt = myBoard.round_cnt
                    while cnt < break_cond:
                        log.append(1)
                        cnt += intervall
                    return [log,(myBoard.round_cnt, myBoard.way_found_first_time, 1)]
                elif myBoard.round_cnt == break_cond:
                    # if shortest way not found return 0 for shortest way
                    return [log,(0, myBoard.way_found_first_time, best_perc)]
#                    return [log,(myBoard.round_cnt, myBoard.way_found_first_time, best_perc)]
    
    pygame.quit()

def write_log(log, map_name, times):
    
    log2 = np.copy(log[1:len(log),:])
    log3 = np.copy(log[1:len(log),:])
    empty = log2[0,0]
    maxi = 0
    mini = len(log2[0])
    for row in xrange(len(log2)):
        cnt = 0
        for col in xrange(len(log2[row])):
            if log2[row,col] == empty:
                cnt += 1
        if cnt > maxi:
            maxi = cnt
        if cnt < mini:
            mini = cnt
        new = np.zeros((len(log2[0])))
        new[0:len(log2[0])-cnt] = log2[row,cnt:]
        log2[row] = new
    
    log2 = log2[:,0:len(log2[0])-maxi]
    col_mean = log2.mean(axis=0)
    
    log3 = log3[:,maxi:]
    col_mean2 = log3.mean(axis=0) 
    
    f = file("stat/"+map_name[0:len(map_name)-4]+'_stat.txt', 'a')
    np.savetxt(f,log[0,:], fmt='%d', newline=" ")
    f.write('\n')
    np.savetxt(f,log[1:,:], fmt='%5.4f')
    f.write('\n')
    f.write(str(mini)+' '+str(maxi)+'\n')
    np.savetxt(f,col_mean, fmt='%5.4f', newline=" ")
    f.write('\n')
    np.savetxt(f,col_mean2, fmt='%5.4f', newline=" ")
    f.write('\n')
    timestring = ''
    for time in times:
        timestring += str(round(time,2))+' '
    f.write(timestring)
    f.close()
    
def start(map_name = None, make_test_series = False, make_genetic_algo = False, \
    fast_start = True, graphics = False, FPS = 60, epsilon = 0.0, break_cond=0):
#    pycallgraph.start_trace()   
    n = 1 # how many runs per parameter set
    intervall = 10 
    
    # do statistics in order to see which parameters have which influence
    if make_test_series:
        path = 'scenario/'
        listing = os.listdir(path)
        for infile in listing:
            map_name = str(infile)
            
            first_row = np.arange(intervall, break_cond+1, intervall)
            log_list = np.zeros((n+1,break_cond/intervall))
            log_list[0,:] = first_row
            times = []
            parameters = []
            for i in xrange(1,n+1):
                print map_name +" - try: "+str(i)
                t1 = time.clock()
                if graphics:
                    [log,para] = main(  map_name = "scenario/"+map_name, \
                                        make_stat = True, break_cond = break_cond, \
                                        intervall = intervall, \
                                        epsilon = epsilon, \
                                        fast_start = fast_start)
                else:
                    [log,para] = engine(map_name = "scenario/"+map_name, \
                                        make_stat = True, break_cond = break_cond, \
                                        intervall = intervall, \
                                        epsilon = epsilon, \
                                        fast_start = fast_start)
                
                parameters.append(para)
                log_list[i,0:len(log)] = log
                t2 = time.clock()
                times.append(t2-t1)
                
            write_log(log_list, map_name, times)
            return mean(parameters)
    
    # mode for making the genetic algorithm
    if make_genetic_algo:
        first_row = np.arange(intervall, break_cond+1, intervall)
        log_list = np.zeros((n+1,break_cond/intervall))
        log_list[0,:] = first_row
        times = []
        parameters = []
        for i in xrange(1,n+1):
            print map_name +" - try: "+str(i)
            t1 = time.clock()
            if graphics:
                [log,para] = main(  map_name = map_name, \
                                    make_stat = True, \
                                    break_cond = break_cond, \
                                    intervall = intervall, \
                                    epsilon = epsilon, \
                                    fast_start = fast_start)
            else:
                [log,para] = engine(map_name = map_name, \
                                    make_stat = True, \
                                    break_cond = break_cond, \
                                    intervall = intervall, \
                                    epsilon = epsilon, \
                                    fast_start = fast_start)
                                    
            parameters.append(para)                
            t2 = time.clock()
            times.append(t2-t1)
            
#        pycallgraph.make_dot_graph('test2.png')
        pygame.quit()
        return minimum(parameters)
    
    else:
        main(map_name = "map1.txt", fast_start=fast_start, FPS = FPS)


if __name__ == "__main__":
    print start("map1.txt",            # which map sould be read
                fast_start = False,     # 8 times slower at the beginning but 30% faster in the run
                graphics = True,       # display GUI
                FPS = 100,              # how many frames per second
                make_genetic_algo = False,  # mode as by the genetic optimisation; 
                                        # allows to give breaking conditions epsilon and break_cond = max round count
                epsilon = 0,           # size of epsilon environment
                break_cond = 0)         # max round count before breaking