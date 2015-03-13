#!/usr/bin/python
# -*- coding: utf-8 -*-

from Widget import *

from Canvas import *
from AsciiCanvas import *
from AsciiSprite import *

from Event import *
from EventType import *

SPRITE_CHARS = u'''──────┬─
  100─┤
      │
  90 ─┤
      │
  80 ─┤
      │
  70 ─┤
      │
  60 ─┤
      │
  50 ─┤
      │
  40 ─┤
      │
  30 ─┤
      │
  20 ─┤
      │
  10 ─┤
      │
   0 ─┤
──────┴─'''

SPRITE_FG_MASK = u'''
WWWWWWWW
  WWWWW
      W
  WW WW
      W
  WW WW
      W
  WW WW
      W
  WW WW
      W
  WW WW
      W
  WW WW
      W
  WW WW
      W
  WW WW
      W
  WW WW
      W
   W WW
WWWWWWWW'''

SPRITE_BG_MASK = u'''KKKKKKKK
BBBBBBK
BBBBBBK
BBBBBBK
BBBBBBK
BBBBBBK
BBBBBBK
BBBBBBK
BBBBBBK
BBBBBBK
BBBBBBK
BBBBBBK
BBBBBBK
BBBBBBK
BBBBBBK
BBBBBBK
BBBBBBK
BBBBBBK
BBBBBBK
BBBBBBK
BBBBBBK
BBBBBBK
KKKKKKKK'''

THROTTLE_SPRITE = AsciiSprite(SPRITE_CHARS, SPRITE_FG_MASK, SPRITE_BG_MASK)

class Throttle(Widget):       
    def validate_canvas( self, canvas ):
        if not canvas.type == "AsciiCanvas":
            raise InvalidCanvasTypeError("Throttles only support AsciiCanvases for now...")
        c_w, c_h = canvas.size
        s_w, s_h = THROTTLE_SPRITE.size
        # TODO: Correct size.
        if not ( c_w >= s_w and c_h >= s_h ):
            raise InvalidCanvasSizeError("Throttles need a larger canvas.")
        
    def handle_event( self, event ):
        return False
        
    def render( self ):      
        self.canvas.putsprite( (0,0),  THROTTLE_SPRITE )

        t_y = int( 21 - 19.5 * self.model.throttle / 100 ) # TODO: Tweak this formula to get slightly better transitions...

        self.canvas.putchr((7,t_y), '<', 'Y', 'K')
        
        self.canvas.putstr((0,t_y),u'──')
        if t_y % 2 == 0:
            self.canvas.putstr((2,t_y),u'──')
        if t_y != 1:
            self.canvas.putstr((4,t_y),u'──')
        if t_y == 21:
            self.canvas.putstr((2,t_y),u'─')
        self.canvas.paint_rect( (0,t_y), (5,t_y), 'B', 'Y' )
