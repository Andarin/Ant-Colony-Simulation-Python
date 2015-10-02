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
import sys
import math
import string
import main
from help_functions import *

import Ants

# just for testing
import time

class Board ():
    def __init__(self, screen, fieldSize, fast_start):
        
        # changeable parameters, default values; new values read from map
        
        # Board parameters
        self.evaporating_time = 20000
        self.field_smell_memory_lim = 40 # -1 means no limitation
        
        # Ant parameters
        self.scouter = 0
        self.stampede = 0
        self.straight_forward = 0


        # intern parameters
        self.fieldSize = fieldSize
        self.normal_start = fast_start # if False, lose 6s at the start of the game but run 5% fast

        self.board_border =3 

        if fieldSize[0] == 300:
            self.menu_size = 39
        elif fieldSize[0] == 600:
            self.menu_size = 79
        else: 
            print "Strange size" + str(fieldSize)
        
        self.screen = screen
        self.round_cnt = 0
        
        self.food = None
        self.colony = None
        self.best_solution_length = 1
        self.shortest_way_found_until_now = 1000000
        self.way_found_first_time = 0
        self.first_food_consumed_time_rnd = 0
        self.first_food_consumed_time_time = 0
        self.list_of_solution_length = []

        self.board = []
        perception_dict = {}
        for x in xrange(fieldSize[0]):
            self.board.append([])

            if x%(fieldSize[0]/8) == 0:
                self.draw_progress_bar(x/(fieldSize[0]/8))
                
            for y in xrange(fieldSize[1] + self.menu_size ):                
                
                if self.menu_size - self.board_border < y:
                    recent_field = Field(x,y, self, memory_size = self.field_smell_memory_lim)
                    self.board[x].append( recent_field )

                    if not self.normal_start:
                        # create dictionary
                        for i in xrange(-3,4):
                            for j in xrange(-3,4):
                                xnew = i + x
                                ynew = j + y
                                if (xnew >= 0 and xnew < fieldSize[0]):
                                    if ynew >= self.menu_size - self.board_border and ynew < fieldSize[1] + self.menu_size:
                                        perception_dict.setdefault((xnew,ynew), []).append(recent_field)

                    # set frame left, right, up and down that ants dont go nowhere
                    if (x <= self.board_border or x >= fieldSize[0]- self.board_border
                        or y <= self.menu_size
                        or y >= fieldSize[1] - self.board_border + self.menu_size):
                        barrier = Barrier((x,y), self.board_border)
                        recent_field.set_barrier(barrier)

                else:
                    # case for the fields covered by the menu
                    self.board[x].append( None )

        if not self.normal_start:
            self.perception_dict = perception_dict
            self.cgive_back_small_board2 = self.give_back_small_board_dict

        self.colony_box = pygame.sprite.RenderUpdates()
        self.ant_box = pygame.sprite.RenderUpdates()
        self.food_box = pygame.sprite.RenderUpdates()
        self.barrier_box = pygame.sprite.RenderUpdates()
        
        self.regulary_change = pygame.sprite.RenderUpdates()

    def individualize(self, not_done, image, map_name):
        self.not_done = not_done
        self.image = image
        
        if map_name is not None:
            self.read_map(map_name)
        if self.best_solution_length > 0:
            print "Best solution possible:", self.best_solution_length
        
    def update (self):
        self.round_cnt += 1
        
        self.colony_box.update(self.round_cnt)

        self.ant_box.update()

        
    def cgive_back_small_board2(self, x, y, percept_range):
        small_board = []
        xnew = -1
        for i in xrange(x-percept_range, x+percept_range+1):
            small_board.append([])
            xnew = xnew + 1
            for j in xrange(y-percept_range, y+percept_range+1):
                self.cdelete_old_smells(self.board[i][j].smell)
                small_board[xnew].append(self.board[i][j])
        return small_board

#    def delete_old_smells(self, smell):
#        for cnt, sm in enumerate(reversed(smell[0])):
#            if self.round_cnt - sm.creation_time < self.evaporating_time:
#                del(smell[0][cnt+1:len(smell[0])])
#        for cnt, sm in enumerate(reversed(smell[1])):
#            if self.round_cnt - sm.creation_time < self.evaporating_time:
#                del(smell[1][cnt+1:len(smell[1])])

    def cdelete_old_smells(self, smells):
        # needs sorted list smells by creation time
        round_cnt = self.round_cnt
        evaporating_time = self.evaporating_time
        leng = len(smells[0])
        i = leng - 1         
        while i >= 0 and round_cnt - smells[0][i].creation_time > evaporating_time:
                i = i-1
        if i < leng-1: del smells[0][(i+1):leng] 
        
        leng = len(smells[1])
        i = leng - 1         
        while i >= 0 and round_cnt - smells[1][i].creation_time > evaporating_time:
                i = i-1
        if i < leng-1: del smells[1][(i+1):leng]

    def give_back_small_board_dict(self, x, y, percept_range):
        return self.perception_dict[(x,y)]

    # not used as real distance by way ants walk is square_root_2_distance
    def calculate_euclidian_distance(self, coord):
        self.best_solution_length = math.sqrt(\
                (self.colony.rect.center[0] - coord[0])**2 \
                + (self.colony.rect.center[1] - coord[1])**2)
                
    def square_root_2_distance(self, coord1, coord2):
        (x1, y1) = coord1
        (x2, y2) = coord2
        difx = abs(x1-x2)
        dify = abs(y1-y2)
        if difx < dify:
            return difx * math.sqrt(2) + dify - difx
        else:
            return dify * math.sqrt(2) + difx - dify

    def square_root_2_distance_over_corner(self, coord1, coord2, corner1, corner2):
        # 5 is added because they have to go around the corner
        self.best_solution_length =5 + min(self.square_root_2_distance(coord1, corner1) + self.square_root_2_distance(coord2, corner1),\
                                        self.square_root_2_distance(coord1, corner2) + self.square_root_2_distance(coord2, corner2))
        print self.best_solution_length

    def new_ant_spawned (self, ant):
        self.ant_box.add(ant)
    
    def new_colony_set (self, colony):
        self.colony = colony
        self.colony_box.add(colony)

    def new_food_set (self, food):
        self.food = food
        self.food_box.add(food)            

    def new_barrier_line_set (self, coord1, coord2):
        liste = linecoords_between_coords (coord1, coord2)
        for item in liste:
            self.new_barrier_set (item)

    def delete_barrier_line (self, coord1, coord2):
        liste = linecoords_between_coords (coord1, coord2)
        for item in liste:
            self.delete_barrier (item)

    def delete_barrier (self, coord):
        radius = 4
        [x,y] = coord
        for xadd in xrange(-radius, radius+1):
            newx =x+xadd
            if 0<= newx <= self.fieldSize[0]:
                for yadd in xrange(-radius, radius+1):
                    newy = y+yadd
                    if 0<= newy <= self.fieldSize[1]:
                        self.board[newx][newy].delete_barrier()

    def new_barrier_set (self, coord):
        radius = 2
        barrier = Barrier(coord, radius)
        self.barrier_box.add(barrier)
        [x,y] = coord
        for xadd in xrange(-radius, radius+1):
            newx =x+xadd
            if 0<= newx <= self.fieldSize[0]:
                for yadd in xrange(-radius, radius+1):
                    newy = y+yadd
                    if 0<= newy <= self.fieldSize[1]:
                        self.board[newx][newy].set_barrier(barrier)

    def draw_board(self, particular_change = None):
        
        self.regulary_change.add(self.ant_box)
        self.regulary_change.add(self.colony_box)
        self.regulary_change.add(self.food_box)
        self.regulary_change.add(self.barrier_box)
        
        if particular_change is not None:
            self.regulary_change.add(particular_change) # for menu stuff
        
        rectlist = self.regulary_change.draw(self.screen)
        pygame.display.update(rectlist)
        if particular_change is not None:
            # don't erase menu changes
            self.regulary_change.remove(particular_change)
            
        self.regulary_change.clear(self.screen, self.image)

    def read_map(self, map):
        if map is not None:
            for line in map:
                if len(line) > 0 and line[0] == "#":
                    continue
                
            # check if parameters are given
                if string.find(line,"evaporating_time") != -1:
                    (self.evaporating_time, i) = get_next_float(line)
                if string.find(line,"field_smell_memory_lim") != -1:
                    (self.field_smell_memory_lim, i) = get_next_float(line)
                if string.find(line,"self.stampede") != -1:
                    (self.stampede, i) = get_next_float(line)
#                    print "stampede =", self.stampede
                if string.find(line,"self.straight_forward") != -1:
                    (self.straight_forward, i) = get_next_float(line)
                if string.find(line,"self.scouter") != -1:
                    (self.scouter, i) = get_next_int(line)
                
            for line in map:
                if len(line) > 0 and line[0] == "#":
                    continue
            # colony statement made (colony placed somewhere)
                if string.find(line,"colony") != -1:
                    ind = string.find(line,"coord")
                    if ind != -1:
                        (xcoord, i) = get_next_int(line[ind:len(line)])
                        (ycoord, j) = get_next_int(line[ind+i:len(line)])
                    ind = string.find(line,"ant")
                    if ind != -1:
                        (ant_number, i) = get_next_int(line[ind:len(line)])
                    try:
                        self.board[xcoord][ycoord].set_colony(ant_number)
                        if self.food is not None:
                            self.best_solution_length = self.square_root_2_distance(self.colony.rect.center, self.food.rect.center)
                    except:
                        print "Map instruction because of error ignored: ", line
                        
            # food statement made (food placed somewhere)
                if string.find(line,"food") != -1:
                    ind = string.find(line,"coord")
                    if ind != -1:
                        (xcoord, i) = get_next_int(line[ind:len(line)])
                        (ycoord, j) = get_next_int(line[ind+i:len(line)])
                    ind = string.find(line,"amount")
                    if ind != -1:
                        (amount, i) = get_next_int(line[ind:len(line)])
                    try:
                        self.board[xcoord][ycoord].set_food(amount)
                        if self.colony is not None:
                            self.best_solution_length = self.square_root_2_distance(self.colony.rect.center, self.food.rect.center)
                    except:
                        print "Map instruction because of error ignored: ", line
                        
            # barrier statement made (barrier placed somewhere)
                if string.find(line,"barrier") != -1:
                    ind = string.find(line,"coord")
                    if ind != -1:
                        (x1, i) = get_next_int(line[ind:len(line)])
                        (y1, j) = get_next_int(line[ind+i:len(line)])
                        (x2, g) = get_next_int(line[ind+i+j:len(line)])
                        (y2, h) = get_next_int(line[ind+i+j+g:len(line)])
                    try:
                        pass
                    except:
                        print "Map instruction because of error ignored: ", line
                    self.new_barrier_line_set((x1,y1),(x2,y2))
    # it is left to the tester that the barrier is actually between the food and the colony
                    if self.colony is not None and self.food is not None:
                        self.square_root_2_distance_over_corner(self.colony.rect.center,\
                                                                self.food.rect.center,\
                                                                (x1, y1), (x2, y2))

    def draw_progress_bar(self, progress):
        if self.screen is not None:
            if progress == 8: progress = 7
            if self.fieldSize[0] == 300:
                logo = load_image ("src/small/load_"+str(progress)+".png", colorkey=(0,0,0))
                pos = [90,230]
            elif self.fieldSize[0] == 600:
                logo = load_image ("src/big/load_"+str(progress)+".png", colorkey=(0,0,0))
                pos = [180,510]
            
            self.screen.blit ( logo , pos)
            pygame.display.flip()

class Menu_Button (pygame.sprite.DirtySprite):
    def __init__ (self, buttontype, size, coord):
        pygame.sprite.DirtySprite.__init__(self)
        
        self.type = buttontype
        self.size = size
        self.board = None
        path_unklick = "src/" + size + "/" + buttontype + "_" + size + ".png"
        path_klick = "src/" + size + "/" + buttontype + "_" + size + "k" + ".png"
        self.image_unklicked = load_image(path_unklick)
        self.image_klicked = load_image(path_klick)
        self.image_special = None # for right click function of barrier button
        self.image = self.image_unklicked
        
        self.rect = self.image.get_rect()
        self.rect.topleft = coord
        
        self.klicked = False
        self.special_klicked = False # for barrier button right klick
        self.start_coord = None
    
    def klick (self):
        self.klicked = True
        self.image = self.image_klicked

    def special_klick(self):
        self.klicked = True
        self.special_klicked = True
        if self.image_special is None:
            path = "src/" + self.size + "/no_barrier_" + self.size + "k.png"
            self.image_special = load_image(path)
        self.image = self.image_special

    def button_action (self, coord):
        
        if self.type == "barrier":
            if self.start_coord is None:
                self.start_coord = coord
            else:
                if self.special_klicked:
                    self.board.delete_barrier_line (self.start_coord, coord)
                else:
                    self.board.new_barrier_line_set (self.start_coord, coord)
                self.start_coord = coord

        elif self.type == "new":
            # rectangel coords are bizarr; maybe should be thought about later
            fac = 1
            if self.size == "big":
                fac *= 2
            if self.rect.left < coord[0] < self.rect.right*2:
                if self.rect.bottom < coord[1] < self.rect.bottom +60*fac/2:
                    main.main(size= "small")
                    sys.exit(1)
                elif self.rect.bottom +60*fac/2 <= coord[1] < self.rect.bottom+60*fac:
                    main.main(size= "big")
                    sys.exit(1)

        elif self.type == "anthill_big":
            self.board.board [coord[0]] [coord[1]] .set_colony(30)
        elif self.type == "anthill_small":
            self.board.board [coord[0]] [coord[1]] .set_colony(10)
        elif self.type == "food_big":
            self.board.board [coord[0]] [coord[1]] .set_food(2500)
        elif self.type == "food_small":
            self.board.board [coord[0]] [coord[1]] .set_food(500)
        
    def unklick (self):
        self.klicked = False
        self.special_klicked = False
        self.image = self.image_unklicked
        self.start_coord = None
        
    def set_board(self, board):
        self.board = board

class Menu ():
    def __init__(self, screen, size = "small"):
        self.size = size
        self.screen = screen
        
        self.menu = pygame.sprite.RenderUpdates()
        self.add_buttons()
        
        self.button_klicked = None
        self.messagebox = None
        
        self.board = None

    def add_buttons(self):
        fac = 1
        if self.size == "big":
            fac = 2
        self.menu.add( Menu_Button("new",           self.size, (0   * fac,0)) )
        self.menu.add( Menu_Button("anthill_big",   self.size, (43  * fac,0)) )
        self.menu.add( Menu_Button("anthill_small", self.size, (86  * fac,0)) )
        self.menu.add( Menu_Button("food_big",      self.size, (129 * fac,0)) )
        self.menu.add( Menu_Button("food_small",    self.size, (172 * fac,0)) )
        self.menu.add( Menu_Button("barrier",       self.size, (215 * fac,0)) )
        self.menu.add( Menu_Button("info",          self.size, (258 * fac,0)) )
 
    def set_board(self, board):
        self.board = board
        for button in self.menu:
            button.set_board(board)

    def draw(self):
        rectlist = self.menu.draw(self.screen)
        pygame.display.update(rectlist)
        if self.board is not None:
            self.menu.clear(self.screen, self.board.image)

    def draw_messagebox(self, name):
        if name == "blank":
            self.messagebox.kill()
            self.messagebox = None
            self.draw()

        elif name == "info":
            self.messagebox = Menu_Button ("info_text", self.size, (0, self.board.menu_size))
            self.menu.add(self.messagebox)

        elif name == "new":
            self.messagebox = Menu_Button ("new_text", self.size, (0, self.board.menu_size))
            self.menu.add(self.messagebox)

    def mouse_down_action(self, coord, mouse_button):
        
        if self.messagebox is not None:
            self.draw_messagebox("blank")
        
        # check if there is a button selected; evt. make button action
        if self.button_klicked is not None:
            if self.coord_is_in_board(coord):
                self.button_klicked.button_action(coord)
            
                if self.button_klicked.type != "barrier":
                    self.button_klicked.unklick()
                    self.button_klicked = None
                    self.draw()
            
            else:
                self.button_klicked.unklick()
                self.button_klicked = None
                self.draw()
            
        
        # maybe a button was klicked
        for button in self.menu:
            if button.rect.collidepoint(coord):
                if button.type == "barrier":
                    if mouse_button > 1: # not left-click
                        button.special_klick()
                    else:
                        button.klick()
                    
                else:
                    button.klick()
                self.button_klicked = button
                if button.type == "info":
                    self.draw_messagebox("info")
                if button.type == "new":
                    self.draw_messagebox("new")
                self.draw()
                break

    def coord_is_in_board(self, coord):
        (x,y) = coord
        if (self.board.board_border <= x < self.board.fieldSize[0] - self.board.board_border
            and self.board.menu_size < y \
                < self.board.fieldSize[1] + self.board.menu_size - self.board.board_border):
            return True
        return False

    def mouse_up_action (self, coord):
        for button in self.menu:
            if (button.type == "barrier"
                and button.klicked
                and button.start_coord is not None):
                button.button_action(coord)
                
class Field ():
    
    def __init__(self, x, y, board, memory_size = -1):
        self.food = None
        self.smell = [[],[]]
        self.barrier = None
        self.colony = None
        self.ants = set()
        self.coord = (x,y)
        self.board = board
        self.memory = memory_size # -1 -> no memory limitation
        if not self.board.normal_start:
            self.set_smell2 = self.set_smell_dict
            self.food_smell_min = 1000000
            self.home_smell_min = 1000000

    def __str__ (self):
        return "x: "+str(self.coord[0]) + " - y: "+ str(self.coord[1])

    def set_food(self, food_amount):
        self.food = Food (food_amount, self.coord)
        self.board.new_food_set (self.food)
        print "Food set."
    
    def consume_food(self, amount_max_consumed):
        if (self.board.first_food_consumed_time_rnd == 0):
            self.board.first_food_consumed_time_rnd = self.board.round_cnt
            self.board.first_food_consumed_time_time = time.clock()

        really_consumed = self.food.vanish (amount_max_consumed)
        if self.food.food_amount == 0:
            self.food = None
        return really_consumed

    def set_smell2(self, information):
        if information.aim == "food":
            self.smell[0].insert(0,information)
        elif information.aim == "home":
            self.smell[1].insert(0,information)
        else:
            print "Strange aim in set_smell2", information.aim

        if (len(self.smell[0]) > self.memory):
            del(self.smell[0][-1])
        if (len(self.smell[1]) > self.memory):
            del(self.smell[1][-1])
            
    def set_smell_dict(self, information):
        if information.aim == "food":
            self.smell[0].insert(0,information)
            self.food_smell_min = min(self.food_smell_min, information.distance)
        elif information.aim == "home":
            self.smell[1].insert(0,information)
            self.home_smell_min = min(self.home_smell_min, information.distance)
        else:
            print "Strange aim in set_smell2", information.aim

        if (len(self.smell[0]) > self.memory):
            del(self.smell[0][-1])
        if (len(self.smell[1]) > self.memory):
            del(self.smell[1][-1])
            
    def set_colony(self, number_of_ants):
        self.colony = Colony (number_of_ants, self, self.board, self.board.stampede, self.board.straight_forward, self.board.scouter)
        self.board.new_colony_set (self.colony)
        print "Colony set."
        
    def ant_goes_on_this_field (self, ant):
        self.ants.add(ant)
        
    def new_ant_spawned_on_this_field (self, ant):
        self.board.new_ant_spawned (ant)
        self.ant_goes_on_this_field(ant)
    
    def ant_leaves_this_field (self, ant):
        self.ants.discard(ant)
    
    def set_barrier(self, barrier):
        self.barrier = barrier
        self.barrier.on_fields.append(self)
        self.food = None
        self.smell = [[],[]]
        self.colony = None
        while len(self.ants) > 0:
            ant_on_field = self.ants.pop()
            if ant_on_field.alive():
                ant_on_field.dies()
    
    def delete_barrier(self):
        if self.barrier is not None:
            self.barrier.kill()
            
            # delete this barrier on all field it stands on
            for field in self.barrier.on_fields:
                if field is not self:
                    field.barrier = None
                    
        self.barrier = None

class Barrier(pygame.sprite.DirtySprite):
    
    def __init__(self, coord, radius):
        pygame.sprite.DirtySprite.__init__(self)
        
        Barrier.image = pygame.Surface([2*radius+1,2*radius+1])
        Barrier.image.fill( (205,102,29) )
            
        self.image = Barrier.image.convert(Barrier.image)
  
        self.rect = self.image.get_rect()
        self.rect.center = coord
        self.dirty = 1

        # set of fields where barrier stands on
        self.on_fields = []
        
class Food(pygame.sprite.DirtySprite):
    image = None
    
    def __init__(self, food_amount, coord):
        pygame.sprite.DirtySprite.__init__(self)
        
        if Food.image is None:
            # This is the first time this class has been instantiated.
            # So, load the image for this and all subsequence instances.
            Food.image = pygame.Surface([3, 3])
            Food.image.fill( (255,0,0) )

        self.image = Food.image.convert(Food.image)

        self.rect = self.image.get_rect()
        self.rect.center = coord
        
        self.food_amount = food_amount
              
    def vanish (self, amount_of_food_desired_to_eat):
        really_consumed = min (self.food_amount, amount_of_food_desired_to_eat)
        self.food_amount = self.food_amount - really_consumed
        
        if self.food_amount == 0:
            self.kill()
        
        return really_consumed
    
class Colony(pygame.sprite.DirtySprite):
    image = None
    
    def __init__(self, number_of_ants, field, board, stampede, straight_forward, scouter):
        pygame.sprite.DirtySprite.__init__(self)
        
        if Colony.image is None:
            # This is the first time this class has been instantiated.
            # So, load the image for this and all subsequence instances.
            Colony.image = pygame.Surface([3, 3])
            Colony.image.fill( (0,0,255) )

        self.image = Colony.image.convert(Colony.image)

        self.rect = self.image.get_rect()
        self.rect.center = field.coord
        
        self.board = board
        self.number_of_ants = number_of_ants

        self.spawn_ratio_in_rounds = 1
        self.colony_round = 0
        self.ants_of_colony = pygame.sprite.RenderUpdates()
        self.field = field        
        
        self.stampede = stampede
        self.straight_forward = straight_forward  
        self.scouter = scouter
        
        self.food_stored = 0
    
    def spawn(self):
        if self.number_of_ants > 0:
            self.number_of_ants -= 1
            new_ant = Ants.Ant(len(self.ants_of_colony)+1, self.field, self.board, self.stampede, self.straight_forward, self.scouter)
            self.ants_of_colony.add(new_ant)
            self.field.new_ant_spawned_on_this_field(new_ant)
    
    def update (self, round_cnt):
        if round_cnt - self.colony_round > self.spawn_ratio_in_rounds:
            self.spawn()
            self.colony_round = round_cnt

    def increase_food(self, amount):
        self.food_stored += amount
    
