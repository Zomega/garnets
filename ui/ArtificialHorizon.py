#!/usr/bin/python
# -*- coding: utf-8 -*-

from Widget import *

from Canvas import *
from AsciiCanvas import *
from AsciiSprite import *

from Event import *
from EventType import *

from math import sin, cos

SPRITE_CHARS = u'''
     ┌───────────────────┐
  ┌──┘      prograde     └──┐
 ┌┴─────────────────────────┴┐   o
┌┘            ───            └┐    
│              ─              │  
│         45 ───── 45         │  
│              ─              │  o
│             ─┼─             │  
│              ┼              │  
│   ─────┐ ───< >─── ┌─────   │ ───
│              ┼              │  
│             ─┼─             │  
│              ─              │  o
│         45 ───── 45         │  
│              ─              │  
└┐            ───            ┌┘   
 └┬─────────────────────────┬┘   o
  └──┐       #####       ┌──┘    
     └───────────────────┘               
 o      o      │      o      o'''

SPRITE_FG_MASK = u'''
     WWWWWWWWWWWWWWWWWWWWW
  WWWWWWWWWWWWWWWWWWWWWWWWWWW
 WWWWWWWWWWWWWWWWWWWWWWWWWWWWW   W
WW            WWW            WW  W 
W              W              W  W
W            WWWWW            W  W
W              W              W  W
W             WRW             W  W
W              R              W  W
W   WWWWWW RRRR RRRR WWWWWW   W RRR
W              R              W  W
W             WRW             W  W
W              W              W  W
W            WWWWW            W  W
W              W              W  W
WW            WWW            WW  W
 WWWWWWWWWWWWWWWWWWWWWWWWWWWWW   W
  WWWWWWWWWWWWWWWWWWWWWWWWWWW    
     WWWWWWWWWWWWWWWWWWWWW       
 WWWWWWWWWWWWWWRWWWWWWWWWWWWWW'''

SPRITE_BG_MASK = u'''
     KKKKKKKKKKKKKKKKKKKKK
  KKKK                   KKKK   BBB
 KK                         KK  BBB
KK                           KK BBB
K                             K BBB
K                             K BBB
K                             K BBB
K                             K BBB
K                             K BBB
K                             K BBB
K                             K BBB
K                             K BBB
K                             K BBB
K                             K BBB
K                             K BBB
KK                           KK BBB
 KK                         KK  BBB
  KKKK                   KKKK   BBB
     KKKKKKKKKKKKKKKKKKKKK                    
BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'''

SKY_BG_MASK = u'''
                                   
      *******************   
   *************************  
  *************************** 
 ***************************** 
 ***************************** 
 ***************************** 
 ***************************** 
 ***************************** 
 ***************************** 
 ***************************** 
 ***************************** 
 ***************************** 
 ***************************** 
 ***************************** 
  *************************** 
   *************************  
      *******************      
     
'''

def is_bg( x, y ):
    lines = SKY_BG_MASK.split('\n')
    if y >= len( lines ):
        return False
    if x >= len( lines[y] ):
        return False
    if lines[y][x] == '*':
        return True
    return False

SPRITE_ALTIMETER = AsciiSprite(SPRITE_CHARS, SPRITE_FG_MASK, SPRITE_BG_MASK)

class ArtificialHorizon(Widget):
    def validate_canvas( self, canvas ):
        if not canvas.type == "AsciiCanvas":
            raise InvalidCanvasTypeError("ArtificialHorizons only support AsciiCanvases for now...")
        c_w, c_h = canvas.size
        s_w, s_h = SPRITE_ALTIMETER.size
        # TODO: Correct size.
        if not ( c_w >= s_w and c_h >= s_h ):
            raise InvalidCanvasSizeError("ArtificialHorizons need a larger canvas.")
        
    def handle_event( self, event ):
        return False
        
    def render( self ):      
        self.canvas.putsprite( (0,0),  SPRITE_ALTIMETER )
        self.draw_horizon()
        #self.add_marker( 0, 0, 'C' )
        
    def draw_horizon( self ):
    
        A,B,C = sin(self.model.roll), cos(self.model.roll), self.model.above_horizon 
        
        ASPECT_RATIO = 0.5 # char_height / char_width
        # A x + B y > C is the sky.
        x_c = 15.5
        y_c = 10.5
        def is_sky(x, y):
            return A * ( x - x_c ) + B * ( ( y - y_c ) / ASPECT_RATIO ) > C
        width, height = SPRITE_ALTIMETER.size
        for x in range( width ):
            for y  in range( height ):
                if is_bg( x, y ):
                    if is_sky(x, y):
                        self.canvas.paint_rect( (x,y), (x,y), bg_color = 'Y' )
                    else:
                        self.canvas.paint_rect( (x,y), (x,y), bg_color = 'B' )
                        
    # TODO: Markers given in u v / spherical coords?
    def add_marker( self, x, y, color ):
        x_c = 15
        y_c = 10
        
        x += x_c
        y += y_c
        if is_bg( x, y ):
            self.canvas.paint_rect( (x,y), (x,y), bg_color = color )
            pass
