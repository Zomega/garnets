#!/usr/bin/python
# -*- coding: utf-8 -*-

from Widget import *

from Canvas import *
from AsciiCanvas import *
from AsciiSprite import *

from Event import *
from EventType import *

SPRITE_CHARS = u'''   4000
──────┐    ─
      │    ─
     ─┤    ─
      │
 025 ─┤
      │
     ─┤    ─
      │
     ─┼──┐
──────┤01│
 023   00├──   m
──────┤99│
     ─┼──┘
      │
     ─┤    ─
      │
 020 ─┤
      │
     ─┤    ─
      │    ─
──────┘    ─'''

SPRITE_FG_MASK = u'''CCCCCCCC         
WWWWWWW    W   
WWWWWWW    W   
WWWWWWW    W   
WWWWWWW    W   
WWWWWWW    W   
WWWWWWW    W   
WWWWWWW    W   
WWWWWWW    W   
WWWWWWWYYY W   
YYYYYYYGGY W   
GGGGGG GGYYY GG
YYYYYYYGGY W   
WWWWWWWYYY W   
WWWWWWW    W   
WWWWWWW    W   
WWWWWWW    W   
WWWWWWW    W   
WWWWWWW    W   
WWWWWWW    W   
WWWWWWW    W   
WWWWWWW    W   '''

SPRITE_BG_MASK = u'''KKKKKKKK
KKKKKKK    BB 
BBBBBBK    BBB
BBBBBBK    BBB
BBBBBBK    BBB
BBBBBBK    BBB
BBBBBBK    BBB
BBBBBBK    BBB
BBBBBBK    BBB
BBBBBBKKKK BBB
KKKKKKKKKK BBB
KKKKKKKKKKKBBB KK
KKKKKKKKKK BBB
BBBBBBKKKK BBB
BBBBBBK    BBB
BBBBBBK    BBB
BBBBBBK    BBB
BBBBBBK    BBB
BBBBBBK    BBB
BBBBBBK    BBB
BBBBBBK    BBB
KKKKKKK    BB'''

SPRITE_ALTIMETER = AsciiSprite(SPRITE_CHARS, SPRITE_FG_MASK, SPRITE_BG_MASK)

class Altimeter(Widget):       
    def validate_canvas( self, canvas ):
        if not canvas.type == "AsciiCanvas":
            raise InvalidCanvasTypeError("Altimeters only support AsciiCanvases for now...")
        c_w, c_h = canvas.size
        s_w, s_h = SPRITE_ALTIMETER.size
        # TODO: Correct size.
        if not ( c_w >= s_w and c_h >= s_h ):
            raise InvalidCanvasSizeError("Altimeters need a 136x7 canvas.")
        
    def handle_event( self, event ):
        return False
        
    def render( self ):      
        self.canvas.putsprite( (0,0),  SPRITE_ALTIMETER )
