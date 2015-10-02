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

def sign (number):
    if number > 0:
        return 1
    elif number <0:
        return -1
    return 0

def load_image(name, colorkey=None):
    try:
        image = pygame.image.load(name)
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey)
    return image

def load_map(name):
    try:
        f = open(name, 'r')
        map = f.read()
        f.close()
        print "Map successfully loaded."
    except:
        print name+" not loaded."
        map = None
    return map

def linecoords_between_coords (coord1, coord2):
    xdif = abs(coord2[0]-coord1[0])
    ydif = abs(coord2[1]-coord1[1])

    xsign = sign( coord2[0]-coord1[0] )
    ysign = sign( coord2[1]-coord1[1] )

    if xdif == 0:
        return [(coord1[0], coord1[1]+ i*ysign ) for i in xrange(ydif+1)]

    if ydif == 0:
        return [(coord1[0] + i*xsign, coord1[1]) for i in xrange(xdif+1)]

    xdiv = 1.0*xdif / ydif
    ydiv = 1.0*ydif / xdif

    xmod, ymod = 0, 0
    xtemp, ytemp = coord1[0], coord1[1]
    liste = [(xtemp, ytemp)]
    cnt, max_calc_before_abort = 0, 600
    while ((xtemp != coord2[0] or ytemp != coord2[1])
        and cnt < max_calc_before_abort):
        cnt += 1
        xmod += xdiv
        ymod += ydiv
        if xtemp != coord2[0] and xmod >= 1:
            xmod -= 1
            xtemp += xsign

        if ytemp != coord2[1] and ymod >= 1:
            ymod -= 1
            ytemp += ysign

        liste.append((xtemp, ytemp))

    if cnt < max_calc_before_abort:
        return liste
    else:
        print "Error in barrier line calculation."
        return [coord1]

def seticon(iconname):
    """
    give an iconname, a bitmap sized 32x32 pixels, black (0,0,0) will be alpha channel

    the windowicon will be set to the bitmap, but the black pixels will be full alpha channel

    can only be called once after pygame.init() and before somewindow = pygame.display.set_mode()
    """
    icon=pygame.Surface((32,32))
    icon.set_colorkey((111,111,111))#and call that color transparant
    rawicon=pygame.image.load(iconname)#must be 32x32, black is transparant
    for i in range(0,32):
        for j in range(0,32):
            icon.set_at((i,j), rawicon.get_at((i,j)))
    pygame.display.set_icon(icon)#set wind

def get_next_int(text):
    out = None
    boo = False
    for i, char in enumerate(text):
        if char.isdigit():
            for j,char2 in enumerate(text[i:len(text)]):
                if not char2.isdigit():
                    boo = True
                    break
        if boo: break
    
    if not boo:
        print "No int found in line"
        raise Exception
    out = int(text[i:i+j])
    return (out, i+j)

def get_next_float(text):
    cnt = 1
    for t in text.split():
        try:
            return (float(t),cnt)
        except ValueError:
            pass
        cnt += 1
    print "Nothing found in help_functions.get_next_float()"
    return 0


def inc_priority():
    """ Set the priority of the process to below-normal."""
    try:
        sys.getwindowsversion()
    except:
        isWindows = False
    else:
        isWindows = True

    if isWindows:
        # Based on:
        #   "Recipe 496767: Set Process Priority In Windows" on ActiveState
        #   http://code.activestate.com/recipes/496767/
        try:
            import win32api, win32process, win32con
            pid = win32api.GetCurrentProcessId()
            handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
            win32process.SetPriorityClass(handle, win32process.HIGH_PRIORITY_CLASS)
        except:
            print "Process priority keeps unchanged as win32api is not installed."
#    else:
#        import os
#
#        os.nice(-2)

def minimum(matrix):
    min_list = []
    for i in xrange(len(matrix[0])):    
        min_list.append(0)
        
    for row in matrix:
        if row[0] > 0:
            if min_list[0]==0 or row[0] < min_list[0]:
                min_list = row
                
    if min_list[0] == 0:
        for row in matrix:
            if min_list[-1]==0 or row[-1] < min_list[-1]:
                min_list = row
                
    return min_list        
