#!/usr/bin/python
# -*- coding: utf-8 -*-

from Widget import *

from Canvas import *
from AsciiCanvas import *
from AsciiSprite import *

from Event import *
from EventType import *

SPRITE_ZERO  = AsciiSprite(u"┌────┐\n│    │\n│    │\n│    │\n└────┘")
SPRITE_ONE   = AsciiSprite(u"   ┐  \n   │  \n   │  \n   │  \n   ┴  ")
SPRITE_TWO   = AsciiSprite(u"┌────┐\n     │\n┌────┘\n│     \n└────┘")
SPRITE_THREE = AsciiSprite(u"┌────┐\n     │\n ────┤\n     │\n└────┘")
SPRITE_FOUR  = AsciiSprite(u"┬    ┬\n│    │\n└────┤\n     │\n     ┴")
SPRITE_FIVE  = AsciiSprite(u"┌────┐\n│     \n└────┐\n     │\n└────┘")
SPRITE_SIX   = AsciiSprite(u"┌────┐\n│     \n├────┐\n│    │\n└────┘")
SPRITE_SEVEN = AsciiSprite(u"┌────┐\n     │\n     │\n     │\n     ┴")
SPRITE_EIGHT = AsciiSprite(u"┌────┐\n│    │\n├────┤\n│    │\n└────┘")
SPRITE_NINE  = AsciiSprite(u"┌────┐\n│    │\n└────┤\n     │\n└────┘")
SPRITE_COLON = AsciiSprite(u"\n*\n\n*\n")

SPRITE = {
    '0':SPRITE_ZERO,
    '1':SPRITE_ONE,
    '2':SPRITE_TWO,
    '3':SPRITE_THREE,
    '4':SPRITE_FOUR,
    '5':SPRITE_FIVE,
    '6':SPRITE_SIX,
    '7':SPRITE_SEVEN,
    '8':SPRITE_EIGHT,
    '9':SPRITE_NINE,
    ':':SPRITE_COLON
}

SPRITE_APOLLO_CLOCK = AsciiSprite(u"┌─────────────────── MISSION  TIMER ───────────────────┐\n         HOURS                MIN             SEC       ")

class MissionTimer(Widget):        
    def validate_canvas( self, canvas ):
        if not canvas.type == "AsciiCanvas":
            raise InvalidCanvasTypeError("Mission Clocks only support AsciiCanvases for now...")
        w, h = canvas.size
        if not ( w >= 136 and h >= 7 ):
            raise InvalidCanvasSizeError("Mission Clocks need a 136x7 canvas.")
        
    def handle_event( self, event ):
        return False
        
    def render( self ):
        self.canvas.putsprite( (0,0), SPRITE_APOLLO_CLOCK )
        
        t = self.model.time
        
        self.canvas.putsprite( (2,2),  SPRITE_ZERO )
        self.canvas.putsprite( (9,2),  SPRITE[t[0]] )
        self.canvas.putsprite( (16,2), SPRITE[t[1]] )
        self.canvas.putsprite( (23,2), SPRITE_COLON )
        self.canvas.putsprite( (25,2), SPRITE[t[3]] )
        self.canvas.putsprite( (32,2), SPRITE[t[4]] )
        self.canvas.putsprite( (39,2), SPRITE_COLON )
        self.canvas.putsprite( (41,2), SPRITE[t[6]] )
        self.canvas.putsprite( (48,2), SPRITE[t[7]] )
