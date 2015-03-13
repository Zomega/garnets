#!/usr/bin/python
# -*- coding: utf-8 -*-

from AsciiSprite import AsciiSprite

DIRMAP_CHARS = u'''       
  z     
       x 
  y     
       '''
       
DIRMAP_FG_MASK = u'''       
  W     
       W 
  W     
       '''
       
DIRMAP_BG_MASK = u'''       
  B     
       B 
  B     
       '''
DIRMAP_SPRITE = AsciiSprite(DIRMAP_CHARS, DIRMAP_FG_MASK, DIRMAP_BG_MASK)

WOOD_CHARS ='''       
        
  WOOD   
        
       '''
''' 
  @───@
 /     \
@ WHEAT @
 \     /
  @───@
  
  @───@
 /     \
@  ORE  @
 \     /
  @───@
  
  @───@
 /     \
@ CLAY  @
 \     /
  @───@
  
  @───@
 /     \
@ SHEEP @
 \     /
  @───@
  
  
  
Ports

  @───@
 /PORT \
@ WOOD  @
 \ 2:1 /
  @───@
  
  @───@
 /PORT \
@ WHEAT @
 \ 2:1 /
  @───@
  
  @───@
 /PORT \
@  ORE  @
 \ 2:1 /
  @───@
  
  @───@
 /PORT \
@ CLAY  @
 \ 2:1 /
  @───@
  
  @───@
 /PORT \
@ SHEEP @
 \ 2:1 /
  @───@
  
  @───@
 /PORT \
@  ANY  @
 \ 3:1 /
  @───@

Other Tiles

  @───@
 /     \
@DESERT @
 \     /
  @───@
  
  @───@
 /     \
@  SEA  @
 \     /
  @───@
'''
