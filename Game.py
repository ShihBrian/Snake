""" 
TODO
-save function
-items (tongue,slow time,score multiplier )
-options menu (speed, size, num rooms...) 
-seperate modes (free play, campaign, classic...)
-rearrange GUI
-fix obj gen inside snake?
-moving mouse for multiplier
-secret room
-makes walls thin?
-dark mode
-boss fight
-campaign - reach 100 length, boss fight at end, upgrades each round or collect as many points as possible within 5 min, boss at end
- ball and yarn do something
- hard mode single block lane -genie
-traps? -genie
heart console display, hitting self
better food as length gets longer
clean up code, make modules

Upgrades:
- bombsize, probability, 
- magnetsize, duration, prob
- tunnel duration, prob
- score multipler
- teleport uses, prob, number of teleporters allowed
- more objects spawn
- heart time for tunnel increase

Current:




QOL:
bomb - drop multiple, timer on bomb, bomb chain reaction, 
bullet - shoot multiple (array),collect bullets
magnet field image, no magnet through wall
tunnel -  buy ability to tunnel through self
draw black pixel on corner
portal - opening animation, place multiple upgradable, 
heart - hit self

add new object:
generate_obj
class object.draw
collect_object

git commit
git status
-git add pygame.py
git commit -m "comment"
git push
"""

import pygame
import sys
import random
import time
import shelve
import os
import math


###########COLOURS############

BLUE = (0,0,255)
GREEN = (0,255,0)
DARKGREEN = (9,65,8)
RED = (255,0,0)
YELLOW = (255,255,0)
LIGHTYELLOW = (255,255,180)
ORANGE = (255,102,0)
WHITE = (255,255,255)
BLACK = (0,0,0)
BROWN = (210,180,140)
TRANS = (1,1,1)
##############################

#########GAMESETTINGS#########
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
BLOCKSIZE = 20
GAMESPEED = 12
MIN_ROOM_SIZE = 120 #120
MAX_ROOM_SIZE = 200 #200
NUM_ROOMS = 20
NUM_OBJECTS = 3
##############################

########PROBABILITIES#########
PROB_YARN = 10
PROB_TUNNEL = 2
PROB_MAGNET = 5
PROB_BOMB = 5
PROB_CANNEDFOOD = 40
PROB_PORTAL = 5
PROB_WATER = 200
PROB_HEART = 2
PROB_FISH = 20
PROB_MOUSE = 1
##############################

TUNNEL_DURATION = 10
MAGNET_DURATION = 10
MAGRADIUS = 1
BOMBSIZE = 13
BOMB_DURATION = 2
BULLET_SPEED = 2
NUM_PORTAL = 3
HEART_DURATION = 1
MULTDURATION = 10
MULTIPLIER = 2

class Tile:
    #a tile of the map and its properties
    def __init__(self, blocked):
        self.blocked = blocked

class projectile:
    def __init__(self,x,y):
        self.dx = 0
        self.dy = 0
        self.x = x
        self.y = y
    
    def direction(self,direc):
        self.dx, self.dy = direc
    
    def move(self):
        redraw_floor(wood_image,self.x,self.y)      
        self.x += self.dx
        self.y += self.dy
    
    def draw(self):
        if self.dx > 0 and self.dy == 0:
            screen.blit(bullet_image,(self.x,self.y))
        elif self.dx < 0 and self.dy == 0:
            rotate_image = pygame.transform.rotate(bullet_image,180)
            screen.blit(rotate_image,(self.x,self.y))
        elif self.dy > 0 and self.dx == 0:
            rotate_image = pygame.transform.rotate(bullet_image,270)
            screen.blit(rotate_image,(self.x,self.y))
        else:
            rotate_image = pygame.transform.rotate(bullet_image,90)
            screen.blit(rotate_image,(self.x,self.y))

class snake:
    def __init__(self):
        self.dx = BLOCKSIZE
        self.dy = 0
        self.position = []
        self.length = 3
    
    def direction(self, direc):
        self.dx, self.dy = direc
    
    def move(self):
        self.prev_position = self.position
        prevx = self.position[self.length-1][0]
        prevy = self.position[self.length-1][1]
        if self.position[0][0]+self.dx == self.position[1][0] and self.position[0][1]+self.dy == self.position[1][1]:
            if self.dx != 0:
                self.dx = self.dx * -1
            if self.dy != 0:
                self.dy = self.dy * -1
        for i in reversed(range(self.length)):
            if i == 0:
                self.position[i] = (self.position[i][0] + self.dx, self.position[i][1] + self.dy, self.dx,self.dy)
            else:
                self.position[i] = (self.position[i-1][0], self.position[i-1][1], self.position[i-1][2], self.position[i-1][3])
        redraw_floor(wood_image,prevx,prevy)
        map_tile[prevx/BLOCKSIZE][prevy/BLOCKSIZE].blocked = False
        
    def draw(self):
        if self.dx > 0 and self.dy == 0:
            body = body_image
            head = head_image
        elif self.dx < 0 and self.dy == 0:
            body = pygame.transform.flip(body_image,True,False)
            head = pygame.transform.flip(head_image,True,False)
        elif self.dx == 0 and self.dy > 0:
            body = pygame.transform.rotate(body_image, 270)
            head = pygame.transform.rotate(head_image, 270)
        elif self.dx == 0 and self.dy < 0:
            body = pygame.transform.rotate(body_image, 90)
            head = pygame.transform.rotate(head_image, 90)
        if self.position[self.length-2][2] > 0:
            tail = tail_image
        elif self.position[self.length-2][2] < 0:
            tail = pygame.transform.flip(tail_image,True,False)
        elif self.position[self.length-2][3] > 0:
            tail = pygame.transform.rotate(tail_image, 270)
        elif self.position[self.length-2][3] < 0:
            tail = pygame.transform.rotate(tail_image, 90)
        if ((self.position[0][2],self.position[0][3]) != (self.position[1][2],self.position[1][3]) and self.position[0][3] < 0 and self.position[1][2] > 0): #right,up
            corner = corner_image
        elif ((self.position[0][2],self.position[0][3]) != (self.position[1][2],self.position[1][3]) and self.position[0][3] < 0 and self.position[1][2] < 0):#left,up
            corner = pygame.transform.flip(corner_image,True,False)
        elif ((self.position[0][2],self.position[0][3]) != (self.position[1][2],self.position[1][3]) and self.position[0][2] < 0 and self.position[1][3] < 0):#up,left  
            corner = pygame.transform.rotate(corner_image,90)
        elif ((self.position[0][2],self.position[0][3]) != (self.position[1][2],self.position[1][3]) and self.position[0][2] > 0 and self.position[1][3] > 0):#down,right  
            corner = pygame.transform.rotate(corner_image,270)
        elif ((self.position[0][2],self.position[0][3]) != (self.position[1][2],self.position[1][3]) and self.position[0][3] > 0 and self.position[1][2] > 0): #right,down
            corner = pygame.transform.flip(corner_image,False,True)
        elif ((self.position[0][2],self.position[0][3]) != (self.position[1][2],self.position[1][3]) and self.position[0][3] > 0 and self.position[1][2] < 0): #left,down
            corner = pygame.transform.flip(corner_image,True,True)
        elif ((self.position[0][2],self.position[0][3]) != (self.position[1][2],self.position[1][3]) and self.position[0][2] > 0 and self.position[1][3] < 0):#up,right  
            corner = pygame.transform.rotate(corner_image,180)
        elif ((self.position[0][2],self.position[0][3]) != (self.position[1][2],self.position[1][3]) and self.position[0][2] < 0 and self.position[1][3] > 0):#down,left  
            corner = corner_image
        redraw_floor(wood_image,self.position[1][0],self.position[1][1])
        map_tile[self.position[1][0]/BLOCKSIZE][self.position[1][1]/BLOCKSIZE].blocked = True
        screen.blit(head, (self.position[0][0],self.position[0][1]))
        redraw_floor(wood_image,self.position[self.length-1][0],self.position[self.length-1][1])
        screen.blit(tail, (self.position[self.length-1][0],self.position[self.length-1][1]))
        if ((self.position[0][2],self.position[0][3]) != (self.position[1][2],self.position[1][3])):
            screen.blit(corner,(self.position[1][0],self.position[1][1]))
        else:
            screen.blit(body,(self.position[1][0],self.position[1][1]))
        
class Rect:
    #a rectangle on the map. used to characterize a room.
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
 
    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return (center_x, center_y)
 
    def intersect(self, other):
        #returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)
    
    def room_intersect(self,other):
        return (self.x1-BLOCKSIZE <= other.x2 and self.x2+BLOCKSIZE >= other.x1 and
                self.y1-BLOCKSIZE <= other.y2 and self.y2+BLOCKSIZE >= other.y1)
        
class Object:
    def __init__(self,x,y,type):
        self.x = x
        self.y = y
        self.points = 1
        self.type = type

    def draw(self,surface):
        if self.type == 'magnet':
            screen.blit(magnet_image,(self.x,self.y))
        elif self.type == 'bomb':
            screen.blit(bomb_image,(self.x,self.y))
        elif self.type == 'yarn':
            screen.blit(yarn_image,(self.x,self.y))
        elif self.type == 'water':
            screen.blit(water_image,(self.x,self.y))
        elif self.type == 'tunnel':
            screen.blit(paw_image,(self.x,self.y))
        elif self.type == 'cannedfood':
            screen.blit(cannedfood_image,(self.x,self.y))
        elif self.type == 'portal':
            screen.blit(portalblue_image,(self.x,self.y))
        elif self.type == 'heart':
            screen.blit(heart_image,(self.x,self.y))
        elif self.type == 'fish':
            screen.blit(fish_image,(self.x,self.y))
        elif self.type == 'mouse':
            screen.blit(mouse_image,(self.x,self.y))
        

def roundup(x, base=BLOCKSIZE):
    return int(base * round(float(x)/base))

def create_room(room):
    global map_tile
    #go through the tiles in the rectangle and make them passable
    for x in range(room.x1/BLOCKSIZE, room.x2/BLOCKSIZE):
        for y in range(room.y1/BLOCKSIZE, room.y2/BLOCKSIZE):
            map_tile[x][y].blocked = False

def create_h_tunnel(x1, x2, y):
    global map_tile
    #horizontal tunnel. min() and max() are used in case x1>x2
    for x in range(min(x1/BLOCKSIZE, x2/BLOCKSIZE), max(x1/BLOCKSIZE, x2/BLOCKSIZE)):
        map_tile[x][y/BLOCKSIZE].blocked = False

def create_v_tunnel(y1, y2, x):
    global map_tile
    #vertical tunnel
    for y in range(min(y1/BLOCKSIZE, y2/BLOCKSIZE), max(y1/BLOCKSIZE, y2/BLOCKSIZE)):
        map_tile[x/BLOCKSIZE][y].blocked = False

def wait_on_collision():
    global snake_prev, snake_state, hearts
    now = time.time()
    endtime = now + 0.015
    snake.position = snake_prev
    while now <= endtime:
        now = time.time()
        event_handle()
    if snake_tunnel:
        for i in snake.position:
            if (snake.position[1][0]+snake.dx,snake.position[1][1]+snake.dy) == (i[0],i[1]):
                game_over()
        if snake.position[1][0]+snake.dx >= WINDOW_WIDTH-BLOCKSIZE or snake.position[1][0]-snake.dx <= roundup(100):
            game_over()
        if snake.position[1][1]+snake.dy >= WINDOW_HEIGHT-BLOCKSIZE or snake.position[1][1]-snake.dy <= 0:
            if hearts == 0:
                game_over()
            else:
                temp  = snake.position[snake.length-1]
                snake.position[0] = temp
                snake.position[snake.length-1] = snake.position[0]
        else:
            snake.position[0] = (snake.position[1][0]+snake.dx, snake.position[1][1]+snake.dy,snake.dx,snake.dy)
    else:         
        if snake.position[1][0]+snake.dx >= WINDOW_WIDTH-BLOCKSIZE or snake.position[1][0]-snake.dx <= roundup(100):
            game_over()
        if snake.position[1][1]+snake.dy >= WINDOW_HEIGHT-BLOCKSIZE or snake.position[1][1]-snake.dy <= 0:
            game_over()
        if map_tile[(snake.position[1][0])/BLOCKSIZE+snake.dx/BLOCKSIZE][(snake.position[1][1])/BLOCKSIZE+snake.dy/BLOCKSIZE].blocked:
            if hearts == 0:
                game_over()
            else:
                if not snake_heart:
                    choose_redraw_wall(snake.position[0][0]/BLOCKSIZE,snake.position[0][1]/BLOCKSIZE)   
                    for i in range(4):
                        flash()
                    snake_state = 'heart_init'  
                    hearts -= 1    
        else:
            snake.position[0] = (snake.position[1][0]+snake.dx, snake.position[1][1]+snake.dy,snake.dx,snake.dy)

def flash():
    for i in snake.position:
        redraw_floor(wood_image, i[0], i[1])
    pygame.display.flip()
    pygame.time.wait(250)
    snake.draw()
    pygame.display.flip()
    pygame.time.wait(250)
       
def make_map():
    global map_tile, first_x, first_y
    rooms = []
    num_rooms = 0
    now = time.time()
    endtime = now + 1
    #fill map with "unblocked" tiles
    map_tile = [[ Tile(True)
        for y in range(0,WINDOW_HEIGHT,BLOCKSIZE) ]
            for x in range(0,WINDOW_WIDTH,BLOCKSIZE) ]

    for x in range(roundup(roundup(100))/BLOCKSIZE,WINDOW_WIDTH/BLOCKSIZE):
        y = 0
        map_tile[x][y].blocked = True
        y = WINDOW_HEIGHT/BLOCKSIZE - 1
        map_tile[x][y].blocked = True
    for y in range(0,WINDOW_HEIGHT/BLOCKSIZE-1):
        x = roundup(roundup(100))/BLOCKSIZE
        map_tile[x][y].blocked = True
        x = WINDOW_WIDTH/BLOCKSIZE-1
        map_tile[x][y].blocked = True
    
    while num_rooms < NUM_ROOMS:
        w = random.randrange(MIN_ROOM_SIZE,MAX_ROOM_SIZE,BLOCKSIZE)
        h = random.randrange(MIN_ROOM_SIZE,MAX_ROOM_SIZE,BLOCKSIZE)
        x = random.randrange(roundup(100)+BLOCKSIZE,WINDOW_WIDTH-w,BLOCKSIZE)
        y = random.randrange(BLOCKSIZE,WINDOW_HEIGHT-h,BLOCKSIZE)
        new_room = Rect(x,y,w,h)
        
        now = time.time()
        if now > endtime:
            break
        failed = False
        for other_room in rooms:
            if new_room.room_intersect(other_room):
                failed = True
                break
            
        if not failed:
            create_room(new_room)
            (new_x, new_y) = new_room.center()
            if num_rooms == 0:
                first_x = new_x
                first_y = new_y
                snake.position = [(roundup(new_x), roundup(new_y),BLOCKSIZE,0),(roundup(new_x)-snake.dx, roundup(new_y)+snake.dy,BLOCKSIZE,0),
                                  (roundup(new_x)-snake.dx*2, roundup(new_y)+snake.dy*2,BLOCKSIZE,0)]
            else:
                (prev_x, prev_y) = rooms[num_rooms-1].center()
                
                if random.randrange(0, 1) == 1:
                    #first move horizontally, then vertically
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_h_tunnel(prev_x, new_x, prev_y+BLOCKSIZE)
                    create_v_tunnel(prev_y, new_y, new_x)
                    create_v_tunnel(prev_y, new_y, new_x-BLOCKSIZE)                     
                else:
                    #first move vertically, then horizontally
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_v_tunnel(prev_y, new_y, prev_x-BLOCKSIZE)
                    create_h_tunnel(prev_x, new_x, new_y)
                    create_h_tunnel(prev_x, new_x, new_y+BLOCKSIZE)  
                    
            rooms.append(new_room)
            num_rooms += 1
            
    (last_x,last_y) =  rooms[(num_rooms-1)].center()    
    create_h_tunnel(last_x, first_x, last_y)
    create_h_tunnel(last_x, first_x, last_y+BLOCKSIZE)
    create_v_tunnel(last_y, first_y, first_x)
    create_v_tunnel(last_y, first_y, first_x-BLOCKSIZE)

def render_map():
    screen.blit(wood_image,(120,20))    
    for y in range(0, WINDOW_HEIGHT/BLOCKSIZE):
        for x in range(roundup(roundup(100))/BLOCKSIZE, WINDOW_WIDTH/BLOCKSIZE):
            wall = map_tile[x][y].blocked
            if wall:
                screen.blit(choose_wall_image(x,y),(x*BLOCKSIZE,y*BLOCKSIZE))

    pygame.display.flip() 

def choose_wall_image(map_x,map_y):
    if map_x == 79:
        right = map_tile[map_x][map_y]
        right_coord = (map_x*BLOCKSIZE,map_y*BLOCKSIZE)
    else:
        right = map_tile[map_x+1][map_y]
        right_coord = ((map_x+1)*BLOCKSIZE,map_y*BLOCKSIZE)
    if map_x == 6:
        left = map_tile[map_x][map_y]
        left_coord = (map_x*BLOCKSIZE,map_y*BLOCKSIZE)
    else:
        left = map_tile[map_x-1][map_y]
        left_coord = ((map_x-1)*BLOCKSIZE,map_y*BLOCKSIZE)
    if map_y == 1:
        up = map_tile[map_x][map_y]
        up_coord = (map_x*BLOCKSIZE,map_y*BLOCKSIZE)
    else:
        up = map_tile[map_x][map_y-1]
        up_coord = (map_x*BLOCKSIZE,(map_y-1)*BLOCKSIZE)
    if map_y == 44:
        down = map_tile[map_x][map_y]
        down_coord = (map_x*BLOCKSIZE,map_y*BLOCKSIZE)
    else:
        down = map_tile[map_x][map_y+1]
        down_coord = (map_x*BLOCKSIZE,(map_y+1)*BLOCKSIZE)
        
    for i in snake.position:
        if right_coord == (i[0],i[1]):
            right.blocked = False
        if left_coord == (i[0],i[1]):
            left.blocked = False
        if down_coord == (i[0],i[1]):
            down.blocked = False
        if up_coord == (i[0],i[1]):
            up.blocked = False
    
    if right.blocked and left.blocked and up.blocked and down.blocked:
        return wall_image
    elif up.blocked and down.blocked and right.blocked:
        wall = pygame.transform.rotate(wall1_image,180)
        return wall
    elif left.blocked and down.blocked and right.blocked:
        wall = pygame.transform.rotate(wall1_image,90)
        return wall
    elif left.blocked and down.blocked and up.blocked:
        return wall1_image
    elif left.blocked and up.blocked and right.blocked:
        wall = pygame.transform.rotate(wall1_image,270)
        return wall
    elif left.blocked and right.blocked:
        wall = pygame.transform.rotate(wall2_image,90)
        return wall
    elif up.blocked and down.blocked:
        return wall2_image
    elif down.blocked and left.blocked:
        return wallcorner_image
    elif right.blocked and down.blocked:
        wall = pygame.transform.rotate(wallcorner_image,90)
        return wall
    elif up.blocked and right.blocked:
        wall = pygame.transform.rotate(wallcorner_image,180)
        return wall
    elif up.blocked and left.blocked:
        wall = pygame.transform.rotate(wallcorner_image,270)
        return wall         
    elif left.blocked:
        wall = pygame.transform.rotate(wall3_image,90)
        return wall
    elif right.blocked:
        wall = pygame.transform.rotate(wall3_image,270)
        return wall
    elif up.blocked:
        return wall3_image
    elif down.blocked:
        wall = pygame.transform.rotate(wall3_image,180)
        return wall
    else:
        return wall4_image
        
def check_object_intersect():
    for object in objects:               
        if snake_magnet:
            snakex = snake.position[0][0]-MAGRADIUS*BLOCKSIZE
            snakex2 = snake.position[0][0]+(MAGRADIUS+1)*BLOCKSIZE
            snakey = snake.position[0][1]-MAGRADIUS*BLOCKSIZE
            snakey2 = snake.position[0][1]+(MAGRADIUS+1)*BLOCKSIZE
        else:
            snakex = snake.position[0][0]
            snakex2 = snake.position[0][0]+BLOCKSIZE
            snakey = snake.position[0][1]
            snakey2 = snake.position[0][1]+BLOCKSIZE
        if (snakex < object.x+BLOCKSIZE and snakex2 > object.x and snakey < object.y+BLOCKSIZE and snakey2 > object.y):
            redraw_floor(wood_image,object.x,object.y) 
            collect_object(object)
            
def collect_object(object):
    global snake_state, num_bombs, score, portalx1, portaly1, portal_in_inv, snake_portal, hearts, multiplier
    if object.type == 'yarn':            
        collect_object2(object)
    elif object.type == 'tunnel':
        snake_state = 'tunnel'
        generate_object(object)
    elif object.type == 'magnet':
        snake_state = 'magnet'
        generate_object(object)
    elif object.type == 'bomb':
        num_bombs += 1
        generate_object(object) 
    elif object.type == 'water':
        collect_object2(object) 
    elif object.type == 'cannedfood':
        collect_object2(object)
    elif object.type == 'portal':
        if snake_portal:
            snake_portal = False
            redraw_floor(wood_image,portalx1,portaly1)
            redraw_floor(wood_image,portalx2,portaly2)
        portalx1 = object.x
        portaly1 = object.y
        portal_in_inv = True
        generate_object(object)
    elif object.type == 'heart':
        hearts += 1
        generate_object(object)
    elif object.type == 'fish':
        collect_object2(object)
    elif object.type == 'mouse':
        snake_state = 'multiplier'
        collect_object2(object)

def collect_object2(object):     
    global score 
    snake.position.append(snake.position[snake.length-1])
    snake.length += 1
    score += object.points*multiplier
    generate_object(object)
    
def check_coord_match(x1, y1, x2, y2):
    if x1 == x2 and y1 == y2:
        return True
    else:
        return False 
                   
def drop_bomb():
    global bombx, bomby, snake_state, num_bombs
    if num_bombs != 0:
        bombx = snake.position[snake.length-1][0]
        bomby = snake.position[snake.length-1][1]
        snake_state = 'bomb'
        num_bombs -= 1

def explode_bomb():
    global bombdropped
    bombdropped = False
    redraw_floor(wood_image,bombx,bomby)
    factor = (BOMBSIZE+1)/2
    for i in range(bombx-(factor-1)*BLOCKSIZE,bombx+(factor)*BLOCKSIZE,BLOCKSIZE):
        if i > WINDOW_WIDTH-2*BLOCKSIZE:
            i = WINDOW_WIDTH-3*BLOCKSIZE
        if i < roundup(100)+BLOCKSIZE:
            i = roundup(100)+BLOCKSIZE
        for j in range(bomby-(factor-1)*BLOCKSIZE,bomby+(factor)*BLOCKSIZE,BLOCKSIZE): 
            if j < BLOCKSIZE:
                j = BLOCKSIZE
            if j > WINDOW_HEIGHT-BLOCKSIZE:
                j = WINDOW_HEIGHT-2*BLOCKSIZE  
            map_tile[i/BLOCKSIZE][j/BLOCKSIZE].blocked = False 
            choose_redraw_wall(i/BLOCKSIZE, j/BLOCKSIZE)
            redraw_floor(wood_image, i,j)
            for x in snake.position:
                if x[0] == i and x[1] == j:
                    game_over()
            for object in objects:
                if object.x == i  and object.y == j:
                    collect_object(object)
            
def draw_explosion():
    factor = (BOMBSIZE+1)/2
    if BOMBSIZE == 7:
        screen.blit(explosion_image7,(bombx-(factor-1)*BLOCKSIZE, bomby-(factor-1)*BLOCKSIZE))
    elif BOMBSIZE == 9:
        screen.blit(explosion_image9,(bombx-(factor-1)*BLOCKSIZE, bomby-(factor-1)*BLOCKSIZE))
    elif BOMBSIZE == 11:
        screen.blit(explosion_image11,(bombx-(factor-1)*BLOCKSIZE, bomby-(factor-1)*BLOCKSIZE))
    elif BOMBSIZE == 13:
        screen.blit(explosion_image13,(bombx-(factor-1)*BLOCKSIZE, bomby-(factor-1)*BLOCKSIZE))
    else:
        screen.blit(explosion_image15,(bombx-(factor-1)*BLOCKSIZE, bomby-(factor-1)*BLOCKSIZE))

def mouse_move(object):
    global mouse_dx, mouse_dy
    image = mouse_image
    redraw_floor(wood_image, object.x, object.y)
    while 1:
        if mouse_dx == BLOCKSIZE:
            choice = choose_direction([10,10,10,70])
        elif mouse_dx == -BLOCKSIZE:
            choice = choose_direction([10,10,70,10])
        elif mouse_dy == BLOCKSIZE:
            choice = choose_direction([10,70,10,10])
        elif mouse_dy == -BLOCKSIZE:
            choice = choose_direction([70,10,10,10])
        else:
            choice = choose_direction([25,25,25,25])
        
        if choice == 'UP' and mouse_dy != BLOCKSIZE:
            mouse_dx = 0
            mouse_dy = -1*BLOCKSIZE
            image = pygame.transform.rotate(mouse_image,90)
        elif choice == 'DOWN' and mouse_dy != -1*BLOCKSIZE:
            mouse_dx = 0
            mouse_dy = BLOCKSIZE
            image = pygame.transform.rotate(mouse_image,270)        
        elif choice == 'RIGHT' and mouse_dx != -1*BLOCKSIZE:
            mouse_dx = BLOCKSIZE
            mouse_dy = 0  
            image = mouse_image         
        elif choice == 'LEFT' and mouse_dx != BLOCKSIZE:
            mouse_dx = -1*BLOCKSIZE
            mouse_dy = 0
            image = pygame.transform.rotate(mouse_image,180)  
                                
        for n,i in enumerate(snake.position):
            if n != 0:
                if object.x == i[0] and object.y == i[1]:
                    in_snake = True
                    break
                else:
                    in_snake = False             
        if map_tile[object.x/BLOCKSIZE+mouse_dx/BLOCKSIZE][object.y/BLOCKSIZE+mouse_dy/BLOCKSIZE].blocked == False and not in_snake:
                object.x += mouse_dx
                object.y += mouse_dy
                break
    
    screen.blit(image,(object.x,object.y))
    
def choose_direction(chances):
    direction_chances = {}
    direction_chances['UP'] = chances[0]
    direction_chances['DOWN'] = chances[1]
    direction_chances['LEFT'] = chances[2]
    direction_chances['RIGHT'] = chances[3]
    return random_choice(direction_chances)    
        
def generate_object(object): 
    Flag = True
    MapFlag = True
    
    item_chances = {}
    item_chances['tunnel'] = PROB_TUNNEL
    item_chances['magnet'] = PROB_MAGNET
    item_chances['bomb'] = PROB_BOMB
    item_chances['cannedfood'] = PROB_CANNEDFOOD
    item_chances['portal'] = PROB_PORTAL
    item_chances['water'] = PROB_WATER
    item_chances['heart'] = PROB_HEART
    item_chances['fish'] = PROB_FISH
    item_chances['mouse'] = PROB_MOUSE
    
    
    while Flag:
        x = random.randrange(roundup(100)+BLOCKSIZE,WINDOW_WIDTH-BLOCKSIZE,BLOCKSIZE)
        y = random.randrange(BLOCKSIZE,WINDOW_HEIGHT-BLOCKSIZE,BLOCKSIZE)
        for i in snake.position:
            SnakeFlag = check_coord_match(i[0], i[1], x, y)
            if SnakeFlag:
                break
        for i in objects:
            ObjFlag = check_coord_match(i.x, i.y, x, y)
            if ObjFlag:
                break
        if map_tile[x/BLOCKSIZE][y/BLOCKSIZE].blocked != True:
            MapFlag = False
        if SnakeFlag == False and ObjFlag == False and MapFlag == False:
            Flag = False
    for i in range(5):
        choice = random_choice(item_chances)
        if choice == 'tunnel':
            object.points = 0
            object.type = 'tunnel' 
        elif choice == 'magnet':
            object.points = 0
            object.type = 'magnet'
        elif choice == 'bomb':
            object.points = 0
            object.type = 'bomb'
        elif choice == 'cannedfood':
            object.points = 2
            object.type = 'cannedfood'
        elif choice == 'portal':
            object.points = 0
            object.type = 'portal'
        elif choice == 'water':
            object.points = 1
            object.type = 'water' 
        elif choice == 'heart':
            object.points = 0
            object.type = 'heart'
        elif choice == 'fish':
            object.points = 3
            object.type = 'fish'
        elif choice == 'mouse':
            object.points = 5
            object.type = 'mouse'
    object.x = x
    object.y = y

def random_choice_index(chances):  #choose one option from list of chances, returning its index
    #the dice will land on some number between 1 and the sum of the chances
    dice = random.randrange(0,sum(chances),1)
    #go through all chances, keeping the sum so far
    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w
 
        #see if the dice landed in the part that corresponds to this choice
        if dice <= running_sum:
            return choice
        choice += 1

def random_choice(chances_dict):
    #choose one option from dictionary of chances, returning its key
    chances = chances_dict.values()
    strings = chances_dict.keys()
 
    return strings[random_choice_index(chances)]

def event_handle():
    global pause
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if game_state == 'Menu':
                if event.key == pygame.K_1:
                    #load_save()
                    new_game()
                elif event.key == pygame.K_2 or event.key == pygame.K_ESCAPE:
                    sys.exit()                  
            elif game_state == 'Playing':
                if event.key == pygame.K_UP and snake.dy != BLOCKSIZE:
                    snake.direction((0,-BLOCKSIZE))
                elif event.key == pygame.K_DOWN and snake.dy != -BLOCKSIZE:
                    snake.direction((0,BLOCKSIZE))
                elif event.key == pygame.K_LEFT and snake.dx != BLOCKSIZE:
                    snake.direction((-BLOCKSIZE,0))
                elif event.key == pygame.K_RIGHT and snake.dx != -BLOCKSIZE:
                    snake.direction((BLOCKSIZE,0))
                elif event.key == pygame.K_w and snake.dy != BLOCKSIZE:
                    snake.direction((0,-BLOCKSIZE))
                elif event.key == pygame.K_s and snake.dy != -BLOCKSIZE:
                    snake.direction((0,BLOCKSIZE))
                elif event.key == pygame.K_a and snake.dx != BLOCKSIZE:
                    snake.direction((-BLOCKSIZE,0))
                elif event.key == pygame.K_d and snake.dx != -BLOCKSIZE:
                    snake.direction((BLOCKSIZE,0))       
                elif event.key == pygame.K_ESCAPE:
                    main_menu()
                elif event.key == pygame.K_1:
                    if not bombdropped:
                        drop_bomb()
                elif event.key == pygame.K_2:
                    if portal_in_inv:
                        drop_portal()  
                elif event.key == pygame.K_KP_PLUS:
                    snake.position.append(snake.position[snake.length-1])
                    snake.length += 1
                elif event.key == pygame.K_SPACE:
                    bullet.x, bullet.y = (snake.position[0][0],snake.position[0][1])
                    bullet.direction((snake.dx,snake.dy))
                    shoot_bullet() 
                elif event.key == pygame.K_p:
                    pause = not pause
            elif game_state == 'Game Over':
                if event.key == pygame.K_ESCAPE:
                    main_menu()
                elif event.key == pygame.K_RETURN:
                    new_game() 
                elif event.key == pygame.K_SPACE:
                    upgrade_menu()
            elif game_state == 'Upgrade':
                if event.key == pygame.K_ESCAPE:
                    main_menu()
                elif event.key == pygame.K_RETURN:
                    new_game() 
        elif event.type == pygame.MOUSEMOTION:
            pos = pygame.mouse.get_pos()
            if game_state == 'Upgrade':
                check_mouse_hover(pos[0],pos[1])
                pygame.display.update((564,20,408,136))
        elif event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            if game_state == 'Menu':
                if pos[0] > 700 and pos[0] < 900 and pos[1] > 318 and pos[1] < 361:
                    new_game()
                if pos[0] > 700 and pos[0] < 900 and pos[1] > 445 and pos[1] < 488:
                    sys.exit()
            elif game_state == 'Game Over':
                if pos[0] > 680 and pos[0] < 880 and pos[1] > 630 and pos[1] < 674:
                    upgrade_menu()
                elif pos[0] > 680 and pos[0] < 880 and pos[1] > 690 and pos[1] < 734:
                    new_game()
                elif pos[0] > 680 and pos[0] < 880 and pos[1] > 750 and pos[1] < 794:
                    main_menu()
            elif game_state == 'Upgrade':
                check_click_upgrade(pos[0],pos[1])

def check_click_upgrade(x,y):
    global BOMBSIZE, score, bomb_size_level, PROB_BOMB, bomb_chance_level
    if in_circle(x,y,20,130,30):
        BOMBSIZE += 2
        bomb_size_level += 1
        score -= 0
        screen.blit(shop_image,(0,0))
    elif in_circle(x,y,120,130,30):
        PROB_BOMB += 5
        bomb_chance_level += 1
        score -= 0
        screen.blit(shop_image,(0,0))
    check_mouse_hover(x,y)
    pygame.display.flip()
    #save_game()

def check_mouse_hover(x,y):
    if in_circle(x,y,20,130,30):
        draw_sentence("Bomb Size Current Level: "+str(bomb_size_level), BLACK,768,58)
        draw_sentence("Next Level Price: "+str((((bomb_size_level**2)*10)+50)),BLACK,768,110)
    elif in_circle(x,y,120,130,30):
        draw_sentence("Bomb Chance Current Level: "+str(bomb_chance_level), BLACK,768,58)
        draw_sentence("Next Level Price: "+str((((bomb_chance_level**2)*10)+50)),BLACK,768,110)
    elif in_circle(x,y,20,350,30):
        draw_sentence("Magnet Duration",BLACK,768,88)
    elif in_circle(x,y,120,350,30):
        draw_sentence("Magnet Chance",BLACK,768,88)
    elif in_circle(x,y,20,570,30):
        draw_sentence("Tunnel Duration",BLACK,768,88) 
    elif in_circle(x,y,120,570,30):
        draw_sentence("Tunnel Chance",BLACK,768,88)    
    else:
        screen.blit(shop_image,(0,0))

def draw_sentence(phrase,colour,centerx,centery):      
    text = font28.render(phrase,0,colour)
    textpos = text.get_rect()
    textpos.centerx = centerx
    textpos.centery = centery
    screen.blit(text,textpos)

def in_circle(mouse_x,mouse_y,circle_x,circle_y,radius):
    circle_x += radius
    circle_y += radius
    sqx = (mouse_x-circle_x)**2
    sqy = (mouse_y-circle_y)**2
    
    if math.sqrt(sqx+sqy) < radius:
        return True
    else:
        return False

def mouse_upgrade(x,y):
    global NUM_OBJECTS, score
    if x > 100 and x < 1500 and y > 20 and y < 800:
        NUM_OBJECTS = 5
        score -= 50   
    
def drop_portal():
    global snake_portal,portalx2,portaly2, portal_use,portal_in_inv
    portalx2 = snake.position[snake.length-1][0]
    portaly2 = snake.position[snake.length-1][1]
    snake_portal = True
    portal_use = NUM_PORTAL
    portal_in_inv = False

def shoot_bullet():
    global snake_bullet
    snake_bullet = True
    for i in range(BULLET_SPEED):
        bullet.move()
        for object in objects:
            if bullet.x == object.x and bullet.y == object.y:
                collect_object(object)
        for i in snake.position:
            if bullet.x == i[0] and bullet.y == i[1]:
                game_over()        
        if map_tile[bullet.x/BLOCKSIZE][bullet.y/BLOCKSIZE].blocked:
            map_tile[bullet.x/BLOCKSIZE][bullet.y/BLOCKSIZE].blocked = False
            redraw_floor(wood_image,bullet.x,bullet.y)
            choose_redraw_wall(bullet.x/BLOCKSIZE, bullet.y/BLOCKSIZE)
            snake_bullet = False
            bullet.x,bullet.y = (0,0)
        else:
            bullet.draw()

def redraw_floor(image,x,y):
    screen.blit(image,(x,y),(x-(roundup(100)+BLOCKSIZE), y-BLOCKSIZE, BLOCKSIZE, BLOCKSIZE))  

def choose_redraw_wall(map_x,map_y):
    right = (map_x+1,map_y)
    left = (map_x-1,map_y)
    up = (map_x,map_y-1)
    down = (map_x,map_y+1)
    right_flag = True
    left_flag = True
    up_flag = True
    down_flag = True
    for i in snake.position:
        if (right[0]*BLOCKSIZE,right[1]*BLOCKSIZE) == (i[0],i[1]):
            right_flag = False
        if (left[0]*BLOCKSIZE,left[1]*BLOCKSIZE) == (i[0],i[1]):
            left_flag = False
        if (up[0]*BLOCKSIZE,up[1]*BLOCKSIZE) == (i[0],i[1]):
            up_flag = False
        if (down[0]*BLOCKSIZE,down[1]*BLOCKSIZE) == (i[0],i[1]):
            down_flag = False    
    if right_flag:
        redraw_floor(wood_image,right[0],right[1])    
        redraw_wall(right[0],right[1])
    if left_flag:
        redraw_floor(wood_image,left[0],left[1])   
        redraw_wall(left[0],left[1])
    if up_flag:
        redraw_floor(wood_image,up[0],up[1])   
        redraw_wall(up[0],up[1])
    if down_flag:
        redraw_floor(wood_image,down[0],down[1])   
        redraw_wall(down[0],down[1])

def redraw_wall(map_x,map_y):    
    if map_tile[map_x][map_y].blocked == False:
        return
    screen.blit(choose_wall_image(map_x,map_y),(map_x*BLOCKSIZE,map_y*BLOCKSIZE))
   
def arrow_key():
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                snake.direction((0,-BLOCKSIZE))
                play_game()
            elif event.key == pygame.K_DOWN:
                snake.direction((0,BLOCKSIZE))
                play_game()
            elif event.key == pygame.K_LEFT:
                snake.direction((-BLOCKSIZE,0))
                play_game()
            elif event.key == pygame.K_RIGHT:
                snake.direction((BLOCKSIZE,0))
                play_game() 
            elif event.key == pygame.K_w:
                snake.direction((0,-BLOCKSIZE))
                play_game()
            elif event.key == pygame.K_s:
                snake.direction((0,BLOCKSIZE))
                play_game()
            elif event.key == pygame.K_a:
                snake.direction((-BLOCKSIZE,0))
                play_game()
            elif event.key == pygame.K_d:
                snake.direction((BLOCKSIZE,0))
                play_game()
            elif event.key == pygame.K_ESCAPE:
                sys.exit()             

def check_snake_collision(head_x, head_y):
    if head_x >= WINDOW_WIDTH-BLOCKSIZE or head_x < roundup(100)+BLOCKSIZE:
        wait_on_collision()
    if head_y > WINDOW_HEIGHT-BLOCKSIZE*2 or head_y < BLOCKSIZE:
        wait_on_collision()
    for n,i in enumerate(snake.position):
        if ((head_x,head_y) == (i[0],i[1])) and n!= 0:
            wait_on_collision()
    if (snake_tunnel or snake_heart) and map_tile[(head_x)/BLOCKSIZE][(head_y)/BLOCKSIZE].blocked:
        screen.blit(wood_image,(head_x,head_y),(head_x-(roundup(100)+BLOCKSIZE),head_y-BLOCKSIZE, BLOCKSIZE, BLOCKSIZE))
        map_tile[(head_x)/BLOCKSIZE][(head_y)/BLOCKSIZE].blocked = False
        choose_redraw_wall(head_x/BLOCKSIZE,head_y/BLOCKSIZE)
    else:
        if map_tile[(head_x)/BLOCKSIZE][(head_y)/BLOCKSIZE].blocked:
            wait_on_collision()

def check_enter_portal():
    global portal_use, snake_portal
    
    head = (snake.position[0][0],snake.position[0][1])
    tail = (snake.position[snake.length-1][0]-snake.position[snake.length-1][2],snake.position[snake.length-1][1]-snake.position[snake.length-1][3])
    if portal_use == 0:
        if (tail == (portalx1,portaly1)) or (tail == (portalx2,portaly2)):
            redraw_floor(wood_image,portalx1,portaly1)
            redraw_floor(wood_image,portalx2,portaly2)
            portal_use = NUM_PORTAL
            snake_portal = False
        
    if snake_portal:
        if head == (portalx1,portaly1):
            snake.position[0] = (portalx2,portaly2,snake.position[0][2],snake.position[0][3])
            portal_use -= 1  
    
        if head == (portalx2,portaly2):
            snake.position[0] = (portalx1,portaly1,snake.position[0][2],snake.position[0][3])
            portal_use -= 1  

def draw_console():
    screen.blit(grass_image,(0,0))
    text = font20.render(str(score),1,WHITE)
    console.blit(text, (5,30))
    pygame.draw.rect(screen, GREEN, (5, 55, BLOCKSIZE, BLOCKSIZE)) 
    pygame.draw.rect(screen, YELLOW, (5, 80, BLOCKSIZE, BLOCKSIZE))
    pygame.draw.rect(screen, BLACK, (5,110,BLOCKSIZE,BLOCKSIZE)) 
    text = font20.render(str(int(round(now-starttime,0))),1,WHITE)
    console.blit(text, (5,5))
    text = font20.render(str(num_bombs),1,WHITE)
    console.blit(text, (30,110))
    
    if snake_tunnel:
        text = font20.render(str(TUNNEL_DURATION - round(now-tunnelstart,1)),1,WHITE)
        console.blit(text, (25,55))
    if snake_magnet:
        text = font20.render(str(MAGNET_DURATION - round(now-magnetstart,1)),1,WHITE)
        console.blit(text, (25,80))         

def drawGrid():
    for x in range(0, WINDOW_WIDTH, BLOCKSIZE): # draw vertical lines
        pygame.draw.line(screen, BLACK, (x, 0), (x, WINDOW_HEIGHT))
    for y in range(0, WINDOW_HEIGHT, BLOCKSIZE): # draw horizontal lines
        pygame.draw.line(screen, BLACK, (0, y), (WINDOW_WIDTH, y))        
    
def render_all():
    global snake_portal
    #drawGrid()
    draw_console()
    screen.blit(border_image,(roundup(100),0))
    for object in objects:
        if object.type == 'mouse':
            time = now-starttime
            if (time % 0.4) < 0.10:
                mouse_move(object)
        else:
            object.draw(screen)
    snake.draw()
    if snake_portal:
        draw_portals()
    pygame.display.flip()

def unique_state(state):
    global tunnelstart, tunnelend, snake_tunnel, magnetstart, magnetend, snake_magnet, now, snake_state, bombdropped, bombend, bombstart, snake_heart, heartend, multiplierend, multiplierstart, multiplier, snake_mult
    now = time.time()    
    if snake_state != prev_snake_state and snake_state == state:
        if state == 'tunnel':
            tunnelstart = now
            tunnelend = tunnelstart + TUNNEL_DURATION
            snake_tunnel = True
            snake_state = 'normal' 
        elif state == 'magnet':
            magnetstart = now
            magnetend = magnetstart + MAGNET_DURATION
            snake_magnet = True
            snake_state = 'normal'
        elif state == 'heart_init':
            heartstart = now
            heartend = heartstart + HEART_DURATION
            snake_heart = True
            snake_state = 'normal' 
        elif state == 'multiplier':
            multiplier = MULTIPLIER
            multiplierstart = now
            multiplierend = multiplierstart + MULTDURATION
            snake_mult = True
            snake_state = 'normal'
    if snake_state == 'bomb':
            bombstart = now
            bombend = bombstart + BOMB_DURATION
            bombdropped = True
            snake_state = 'normal'        
    if snake_tunnel:
        if now > tunnelend:
            snake_tunnel = False 
    if snake_magnet:
        if now > magnetend:
            snake_magnet = False
    if bombdropped:
        if now + 0.013 > bombend:
            draw_explosion()
            if now > bombend:
                explode_bomb()
        else:
            screen.blit(bomb_image,(bombx,bomby))
    if snake_heart:
        if now > heartend:
            snake_heart = False
    if snake_mult:
        if now > multiplierend:
            snake_mult = False
            multiplier = 1

def draw_portals():
        
        screen.blit(portalblue_image,(portalx1,portaly1)) 
        screen.blit(portalpurp_image,(portalx2,portaly2))    
                           
def main_menu():
    global game_state
    screen.blit(start_image,(0,0))
    game_state = 'Menu'
    pygame.display.flip()
    while 1:
        event_handle()

def load_save():
    load_game()
    new_game()

def new_game():
    global game_state,score, snake_state, snake_tunnel, snake_magnet, starttime, bombdropped, num_bombs, snake_bullet,pause, snake_portal 
    global portal_in_inv, portal_use, hearts, snake_heart, mouse_object, mouse_dx, mouse_dy, multiplier, snake_mult, bomb_size_level, bomb_chance_level
    game_state = 'New Game'
    screen.blit(grass_image,(0,0))
    snake.direction((BLOCKSIZE,0))
    snake.length = 3
    snake_state = 'normal'
    bomb_size_level = 1
    bomb_chance_level = 1
    portal_use = NUM_PORTAL
    score = 0
    snake_tunnel = False
    snake_magnet = False
    snake_portal = False
    starttime = time.time()
    num_bombs = 0
    bombdropped = False
    snake_bullet = False
    pause = False
    portal_in_inv = False
    snake_heart = False
    mouse_object = False
    snake_mult = False
    mouse_dx = 0
    mouse_dy = 0
    multiplier = 1
    hearts = 0
    make_map()
    for i in range(NUM_OBJECTS):
        add_object()
    render_map()
    screen.blit(border_image,(roundup(100),0))
    text = font20.render("Press An Arrow Key To Start",1,BLUE)
    textpos = text.get_rect()
    textpos.centerx = screen.get_rect().centerx
    textpos.centery = screen.get_rect().centery
    screen.blit(text,textpos)
    snake.draw()
    pygame.display.flip()
    load_game()
    while 1:
        arrow_key()

def play_game():
    global game_state, snake_prev, snake_state, prev_snake_state
    game_state = 'Playing'
    screen.fill(BLACK)
    prev_snake_state = snake_state
    for object in objects:
        generate_object(object)
    render_map()
    while 1:
        if not pause:
            clock.tick(GAMESPEED)
            prev_snake_state = snake_state
            check_object_intersect()
            snake_prev = snake.position
            unique_state('tunnel')
            unique_state('magnet')
            unique_state('bomb')
            unique_state('heart_init')
            unique_state('multiplier')
            if snake_bullet == True:
                shoot_bullet()
            snake.move() 
            check_enter_portal()
            check_snake_collision(snake.position[0][0], snake.position[0][1])
            render_all()
            event_handle()
            print BOMBSIZE
        else:
            event_handle()
        
def game_over():
    global game_state, score
    for i in range(NUM_OBJECTS):
        objects.pop()
    game_state = 'Game Over'
    screen.blit(game_over_image,(0,0))
    draw_sentence("Upgrades", BLACK, 780, 652)
    draw_sentence("Restart", BLACK, 780, 712)
    draw_sentence("Menu", BLACK, 780, 772)
    pygame.display.flip()
    save_game()
    while 1:
        event_handle()

def upgrade_menu():
    global game_state
    game_state = 'Upgrade'
    screen.fill(BLACK)
    screen.blit(shop_image,(0,0))
    pygame.display.flip()
    while 1:
        event_handle()
        
def calc_highscore(score):
    global highscore
    
    if highscore is None:
        highscore = score
    if score > highscore:
        highscore = score
    
def save_game():
    save = shelve.open('savegame')
    save['highscore'] = highscore
    save['BOMBSIZE'] = BOMBSIZE
    save['TUNNEL_DURATION'] = TUNNEL_DURATION
    save['MAGNET_DURATION'] = MAGNET_DURATION
    save['MAGRADIUS'] = MAGRADIUS
    save['NUM_PORTAL'] = NUM_PORTAL
    save['GAMESPEED'] = GAMESPEED
    save['score'] = score
    save.close()

def load_game():
    global highscore,BOMBSIZE, TUNNEL_DURATION, MAGNET_DURATION, MAGRADIUS, NUM_PORTAL, score
    save = shelve.open('savegame')
    highscore = save['highscore']
    BOMBSIZE = save['BOMBSIZE']
    TUNNEL_DURATION = save['TUNNEL_DURATION']
    MAGNET_DURATION = save['MAGNET_DURATION']
    MAGRADIUS = save['MAGRADIUS']
    NUM_PORTAL = save['NUM_PORTAL'] 
    score = save['score']
    save.close()

def load_image(imagename,colour): 
    filename = 'resources/images/'+imagename
    image = pygame.image.load(filename).convert()
    image.set_colorkey(colour)
    return image

def add_object():
    obj = Object(0,0, 'unassigned')
    objects.append(obj)
    generate_object(objects[-1])

################################
# Image Initialization
################################  
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
console = screen.subsurface(0,0,roundup(100),900)
bullet_image = load_image('bullet.png',WHITE)
magnet_image = load_image('magnet.png',WHITE)
bomb_image = load_image('bomb.png',WHITE)
explosion_image7 = load_image('explosion7.png',WHITE)
explosion_image9 = load_image('explosion9.png',WHITE)
explosion_image11 = load_image('explosion11.png',WHITE)
explosion_image13 = load_image('explosion13.png',WHITE)
explosion_image15 = load_image('explosion15.png', WHITE)    
head_image = load_image('Head.png',WHITE)
body_image = load_image('Body.png',WHITE)
tail_image = load_image('Tail.png',WHITE)
corner_image = load_image('Body Corner.png',WHITE)
mouse_image = load_image('mouse.png',WHITE)
yarn_image = load_image('yarn.png',WHITE)
wood_image = load_image('wood.png',WHITE)
wall_image = load_image('wall.png',WHITE)
wall1_image = load_image('wall1.png',WHITE)
wall2_image = load_image('wall2.png',WHITE)
wall3_image = load_image('wall3.png',WHITE)
wall4_image = load_image('wall4.png',WHITE)
wallcorner_image = load_image('wallcorner.png',WHITE)
border_image = load_image('border.png',WHITE)
paw_image = load_image('paw.png',WHITE)
cannedfood_image = load_image('cannedfood.png',WHITE)
portalblue_image = load_image('portal.png',WHITE)
portalpurp_image = load_image('portal2.png',WHITE)
start_image = load_image('start_screen.png',TRANS)
grass_image = load_image('grass.png',WHITE)
water_image = load_image('water.png',WHITE)
game_over_image = load_image('GameOver.png',WHITE)
fish_image = load_image('fish.png', WHITE)
heart_image = load_image('heart.png',WHITE)
shop_image = load_image('shop.png', TRANS)
################################
# Initialization
################################

clock = pygame.time.Clock()
font20 =  pygame.font.Font("Calibri.ttf", 20)
font36 =  pygame.font.Font("Calibri.ttf", 36)
font24 =  pygame.font.Font("Calibri.ttf", 24)
font28 =  pygame.font.Font("Calibri.ttf", 28)
snake = snake()
objects = []
bullet = projectile(0,0)
highscore = 0
main_menu()