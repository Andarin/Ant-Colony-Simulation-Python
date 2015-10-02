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
import math
import numpy as np
import pyximport; pyximport.install()
import Ant_mod
cimport numpy as np
FLOAT = np.float
ctypedef np.float_t FLOAT_t
import cython

from itertools import chain

# just for testing reasons
import time

cdef inline int direction (int number): return -1 if number < 0 else 1

class Ant(pygame.sprite.DirtySprite, Ant_mod.Ant_mod):
    image = None

    def __init__(self, name, field, board, stampede, straight_forward, scouter):
        # changeable parameters
        
        # how many ants are scouter and by that have stampede so they possibly
        # discover a shorter way; 1 = every ant, 3 = one in three, 10 = one in 10
        self.scouter = scouter        
        
        # how likely the ant just heads of a random field; 
        # 0 = deterministic, 1 = ant thinks never
        if scouter != 0 and name%scouter == 0:
            self.stampede = stampede
        else:
            self.stampede = 0
        
        # how likely in percent is that ant goes on the field in front of her; 1 = always
        self.straight_forward = straight_forward
        
        # how much ant can carry
        self.maxLoad = 1
        
        # speed in fields; if >2, it has to be changed a few things in self.approach        
        self.velocity = 2
        
        # how far can ant look in fields;
        # ATTENTION: if >4 -> change perception_dict creation and borderthickness in lib
        self.range_of_perception = 3

        # intern parameters
        pygame.sprite.DirtySprite.__init__(self)

        if Ant.image is None:
            # This is the first time this class has been instantiated.
            # So, load the image for this and all subsequence instances.
            Ant.image = pygame.Surface([2, 2])
            Ant.image.fill( (0,0,0) )

        self.image = Ant.image.convert(Ant.image)

        self.rect = self.image.get_rect()
        self.rect.center = field.coord
        self.dirty = 2

        self.board = board
        self.name = name
        self.load = 0
        self.perception = None
        self.field_standing_on = field
        self.targetField = None
        self.stampedeField = None
        self.aim = "food"
        self.distance_from_last_found = 0
        self.size_of_last_found = 0
        self.index_smells_good = 1
        self.index_smells_bad = 0
        self.preferation_matrix = None
        self.preferation_matrix_old = None
        self.memory = [0,0]

        # control variables for seeing what the ant does and how long it takes
        self.print_status = False
        if not self.board.normal_start: 
            self.choose_best_field_to_go2 = self.choose_best_field_to_go_dict
            self.ctake_step = self.ctake_step_dict
            
    def update(self):
        
        self.walk()

    def walk(self):
        enteringField = None
        #self.perception = self.board.give_back_small_board2(self.rect.center, self.range_of_perception)
        self.perception = self.board.cgive_back_small_board2(self.rect.center[0], self.rect.center[1], self.range_of_perception)   
        if self.print_status: print "Ant's position: ", self.field_standing_on.coord
        
        if self.stampedeField is not None:
            enteringField = self.approach(self.stampedeField)
        else:     
    
            self.relative_coord = [self.range_of_perception,self.range_of_perception]
    
            dim = self.range_of_perception*2+1
            self.preferation_matrix = np.cast[np.float](np.random.rand(dim,dim))       
            self.preferation_matrix += self.like_straight_forward(dim, self.straight_forward)
            
            if np.random.rand() < self.stampede:
                enteringField = self.run_stampede()
            elif self.aim == "food":
                if self.print_status: print "Ant looks for food. "
                enteringField = self.find_food2()
            elif self.aim == "home":
                if self.print_status:
                    print "Ant wants to go home.",
                enteringField = self.find_home2()
            else:
                print "Strange aim in ant " + str(self.name)

        if enteringField is not None:
            self.field_standing_on.ant_leaves_this_field(self)
            if self.print_status: print "Ant left field: ", self.field_standing_on.coord
            enteringField.ant_goes_on_this_field(self)        
            
            self.memory = [enteringField.coord[0] - self.field_standing_on.coord[0],\
                           enteringField.coord[1] - self.field_standing_on.coord[1]]
            self.field_standing_on = enteringField
            self.rect.center = enteringField.coord
            self.set_mark()
#            print enteringField, self.memory
#            if self.name == 1:
##                print self.preferation_matrix
#                print self.field_standing_on.coord

    def approach2(self, target):
        (x,y) = self.field_standing_on.coord
        step = [0,0]
        stepDist=0

        directionInX = direction (target.coord[0] - x)
        directionInY = direction (target.coord[1] - y)
        if (x != target.coord[0] and y != target.coord[1]):
            step = [directionInX, directionInY]
            stepDist += math.sqrt(2)

        else:
            stepInX = min(self.velocity, abs(x - target.coord[0]))
            step[0] = stepInX * directionInX

            stepInY = min(self.velocity - abs(step[0]), abs(y - target.coord[1]))
            step[1] = stepInY * directionInY
            stepDist = stepInX + stepInY

        # if with this step target is reached, empty target
        if (x + step[0] == target.coord[0]
            and y + step[1] == target.coord[1]):
            self.targetField = None


        self.increase_distance_from_last_found(stepDist)

        if self.board.normal_start:
            # if no saved small_boards
            return self.perception[step[0]+self.range_of_perception][step[1]+self.range_of_perception]
        else:
            return self.perception[(step[0]+self.range_of_perception)*(self.range_of_perception*2+1)+step[1]+self.range_of_perception]

    def approach(self, target):
        (xh,yh) = self.field_standing_on.coord
        (xt, yt) = target.coord
        step = [0,0]
        stepDist=0
        test = 10

        xdistance = abs(xt - xh)
        ydistance = abs(yt - yh)

        directionInX = direction (xt - xh)
        directionInY = direction (yt - yh)
        
        if xdistance > 1:
            if ydistance > 1:
                test = 2
            elif ydistance != 0:
#                test = 2*np.random.random_integers(0,1)
                test = 2
            else:
                test = 0            

        elif ydistance > 1:
            if xdistance != 0:
#                test = 1 + np.random.random_integers(0,1)
                test = 2
            else:
                test = 1
            
        elif xdistance != 0:
            if ydistance != 0:
                test = 2
            else:
                test = 0
            
        elif ydistance != 0:
            test = 1
             
        if test == 0:
            stepInX = min(self.velocity, xdistance)
            step[0] = stepInX * directionInX
            stepDist = stepInX        
        elif test == 1:
            stepInY = min(self.velocity, ydistance)
            step[1] = stepInY * directionInY
            stepDist = stepInY
        elif test == 2:
            step = [directionInX, directionInY]
            stepDist = math.sqrt(2)            

        # if with this step target is reached, empty target

        if (xh + step[0] == xt
            and yh + step[1] == yt):
            self.targetField = None
            self.stampedeField = None

        self.increase_distance_from_last_found(stepDist)
        if self.board.normal_start:
            # if no saved small_boards
            return self.perception[step[0]+self.range_of_perception][step[1]+self.range_of_perception]
        else:
            return self.perception[(step[0]+self.range_of_perception)*(self.range_of_perception*2+1)+step[1]+self.range_of_perception]

    def increase_distance_from_last_found(self, step_dist):
        self.distance_from_last_found += step_dist

    def set_mark(self):
        information = Information (self.aim, self.distance_from_last_found, \
                                self.board.round_cnt, self.size_of_last_found)
        self.field_standing_on.set_smell2(information)

    def find_food2(self):
        if self.food_on_field():
            return self.eat()

        return self.ctake_step()

    def find_home2(self):
        if self.field_standing_on.colony:
            return self.go_home()

        return self.ctake_step()

    def like_straight_forward2(self, dim, straight_forward):
        [xmem, ymem] = self.memory 
        basis = np.zeros((dim,dim))
        one_vec = straight_forward*np.ones((5))
        one_vec_short = straight_forward*np.ones((3))

        if xmem == 0:
            if ymem < 0:
                basis[0,1:dim-1] = one_vec
            elif ymem > 0:
                basis[dim-1,1:dim-1] = one_vec  
        elif xmem < 0:
            if ymem < 0:
                basis[0,0:3] = one_vec_short
                basis[0:3,0] = one_vec_short
            elif ymem > 0:
                basis[dim-1,0:3] = one_vec_short
                basis[dim-3:dim,0] = one_vec_short
            elif ymem == 0:
                basis[1:dim-1,0] = one_vec
        elif xmem > 0:
            if ymem < 0:
                basis[0,dim-3:dim] = one_vec_short
                basis[0:3,dim-1] = one_vec_short
            elif ymem > 0:
                basis[dim-1,dim-3:dim] = one_vec_short
                basis[dim-3:dim,dim-1] = one_vec_short 
            elif ymem == 0:
                basis[1:dim-1,dim-1] = one_vec
            
        return basis

    def like_straight_forward(self, dim, straight_forward):
        [xmem, ymem] = self.memory
        basis = np.zeros((dim,dim))
        basis[self.range_of_perception+xmem,self.range_of_perception+ymem]=straight_forward
        return basis

    def run_stampede(self):
        run_into_wall = True
        while run_into_wall:
            self.targetField = self.choose_best_field_to_go2(self.preferation_matrix)
            self.stampedeField = self.targetField
            if self.targetField.barrier is None:
                run_into_wall = False
            else:
                (xtar,ytar) = self.targetField.coord
                (xself, yself) = self.field_standing_on.coord
                self.preferation_matrix[ytar-yself+self.range_of_perception,xtar-xself+self.range_of_perception] -= 100000
                
        return self.approach(self.targetField)

    def change_marks(self, size = 0):
        self.distance_from_last_found = 0
        self.size_of_last_found = size

    def change_aim(self):
        if self.aim == "food":
            self.aim = "home"

            # intern vars for deciding between smells
            self.index_smells_good = 0
            self.index_smells_bad = 1
        elif self.aim == "home":
            self.aim = "food"

            # intern vars for deciding between smells
            self.index_smells_good = 1
            self.index_smells_bad = 0
        else: print "Problem in change_aim of ant " + str(self.name)

    def go_home(self):
        if self.print_status: print "Ant delivered food."
        self.board.list_of_solution_length.append(self.distance_from_last_found)

        if self.field_standing_on.colony is not None:
            self.field_standing_on.colony.increase_food(self.load)
        else:
            print "Error in go_home"
            raise Exception
        self.load = 0
        self.targetField = None
        
# ugly hack to see shortest distance
        sd = self.distance_from_last_found
        if sd < self.board.shortest_way_found_until_now:
            self.board.shortest_way_found_until_now = sd
            if self.board.way_found_first_time == 0 : self.board.way_found_first_time = self.board.round_cnt
            percent = round(sd/self.board.best_solution_length,4)
            print percent*100,'% of best solution after', self.board.round_cnt, 'rounds.'
#            if percent - 1 < 0.01:
#                self.board.not_done[0] = False
        
        self.change_aim()
        self.change_marks()

    def eat(self):
        if self.print_status: print "Ant eats."
        if self.field_standing_on.food is not None:
            self.load = self.field_standing_on.consume_food(self.maxLoad)
            self.targetField = None
            self.change_aim()
            if self.field_standing_on.food is not None:
                self.change_marks(self.field_standing_on.food.food_amount)
            else:
                self.change_marks()

    def food_on_field(self):
        if self.field_standing_on.food is not None:
            return True
        else: return False

    def dies (self):
        print "Ant " + str(self.name) + " died."
        self.kill()

    def choose_best_field_to_go2(self, preferation_matrix):
        cdef int dim = self.range_of_perception*2+1
        cdef int ind_max = preferation_matrix.flatten('F').argmax()
        cdef int x, y
        x = ind_max/dim
        y = ind_max%dim
#        print "max ", ind_max, x, y
        return self.perception[x][y]
        
    def choose_best_field_to_go_dict(self, preferation_matrix):
        cdef int ind_max = preferation_matrix.flatten('F').argmax()
        return self.perception[ind_max]

cdef class Information:
    cdef public float creation_time
    cdef public str aim
    cdef public float distance
    cdef public float size
    
    def __init__(self, str aim, float dist, float creation_time, float size = 0):
        self.creation_time = creation_time
        self.aim = aim
        self.distance = dist
        self.size = size

    def __str__(self):
        return str(self.distance)