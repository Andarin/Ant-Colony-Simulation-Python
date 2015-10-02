"""
Created on Mon Apr 16 18:28:56 2012

@author: Luc
"""

import numpy as np
cimport numpy as np
FLOAT = np.float
ctypedef np.float_t FLOAT_t
import cython

cdef inline int max_int(int a, int b): return a if a > b else b

class Ant_mod():

    @cython.wraparound(False)
    def ctake_step (self):
        cdef np.ndarray[FLOAT_t, ndim=2] preferation_matrix = self.preferation_matrix
        cdef list perception = self.perception
        cdef list col, list_of_good_smells
        cdef str aim = self.aim
        cdef int index_smells_good = self.index_smells_good
        cdef int index_smells_bad = self.index_smells_bad
        cdef int p_range = len(perception)
        cdef int x, y, obj_looking_for
        cdef int i, dist, minimum
 
        for x in xrange(p_range):
            col = perception[x]
            for y in xrange(p_range):
                
                # if ant cannot go on the field
                if col[y].barrier:
                    preferation_matrix[y,x] += -1000000
                    continue

                # is aim near
                obj_looking_for = 0
                if aim == "food" and col[y].food is not None:
                    obj_looking_for = 1
                elif aim == "home" and col[y].colony is not None:
                    obj_looking_for = 1

################################################################################
###################### EDITING FROM THIS POINT ON ##############################
################################################################################

                # if object the ant is looking for is in sight
                if obj_looking_for == 1:
                    preferation_matrix[y,x] += 100000
                    continue
                
                # if food mark is near
                list_of_good_smells = col[y].smell[index_smells_good]
                if len(list_of_good_smells)>0:
                    
                    minimum = list_of_good_smells[0].distance
                        
                # Possibility: if following lines are outcommented, the ant 
                # just takes the first smell to decide about the field
                # if they are executed, the ant looks for the best smell on the field
                    for i in xrange(len(list_of_good_smells)):
                        dist = list_of_good_smells[i].distance
                        #print dist,
                        if dist < minimum:
                            minimum = dist
                    #print "minimum:",minimum, x, y
                    preferation_matrix[y,x] = preferation_matrix[y,x] + max_int(100000-5*minimum,5)

                # if there are ants with same aim near
                preferation_matrix[y,x] += -len(col[y].smell[index_smells_bad])/10

        self.targetField = self.choose_best_field_to_go2(preferation_matrix)
        return self.approach(self.targetField)

    @cython.wraparound(False)
    def ctake_step_dict(self):
        cdef np.ndarray[FLOAT_t, ndim=2] preferation_matrix = self.preferation_matrix
        cdef list perception = self.perception
        cdef list list_of_good_smells
        cdef str aim = self.aim
        cdef int index_smells_good = self.index_smells_good
        cdef int index_smells_bad = self.index_smells_bad
        cdef int p_range = len(perception)
        cdef int x, y, obj_looking_for, col, row
        cdef int i, dist, minimum        
        
        cdef int r_o_p = self.range_of_perception*2 + 1
 
 
        for i in xrange(p_range):
            entry = perception[i]
            col = i/r_o_p
            row = i%r_o_p

            # if ant cannot go on the field
            if entry.barrier:
                preferation_matrix[row,col] += -1000000
                continue

            # is aim near
            obj_looking_for = 0
            if aim == "food" and entry.food is not None:
                obj_looking_for = 1
            elif aim == "home" and entry.colony is not None:
                obj_looking_for = 1

################################################################################
###################### EDITING FROM THIS POINT ON ##############################
################################################################################

            # if object the ant is looking for is in sight
            if obj_looking_for == 1:
                preferation_matrix[row,col] += 100000
                continue
            
            # if food mark is near
            # Possibility: if following lines but the first 3 are outcommented, the ant 
            # just takes the first smell to decide about the field
            # if they are executed, the ant looks for the best smell on the field
#            list_of_good_smells = entry.smell[index_smells_good]
#            if len(list_of_good_smells)>0:
#                minimum = list_of_good_smells[0].distance
#                for i in xrange(len(list_of_good_smells)):
#                    dist = list_of_good_smells[i].distance
#                    #print dist,
#                    if dist < minimum:
#                        minimum = dist

            # second possibility: short cut which works only if no information disappears
            if aim == "food":
                minimum = entry.home_smell_min
            elif aim == "home":
                minimum = entry.food_smell_min


            preferation_matrix[row,col] = preferation_matrix[row,col] + max_int(100000-5*minimum,5)

            # if there are ants with same aim near
            preferation_matrix[row,col] += -len(entry.smell[index_smells_bad])/10

        self.targetField = self.choose_best_field_to_go2(preferation_matrix)
        return self.approach(self.targetField)