#!/usr/bin/python
# -*- coding: latin 1 -*-

import curses

from AsciiCanvas import AsciiCanvas

from Event import *

class ColorManager:
    def __init__( self ):
        self.pairs = {
            (curses.COLOR_WHITE, curses.COLOR_BLACK) : 0
        }
        
        self.fg_default = curses.COLOR_WHITE
        self.bg_default = curses.COLOR_BLACK
    
    def convert_char_code( self, c ):
        if c == 'K':
            return curses.COLOR_BLACK
        if c == 'W':
            return curses.COLOR_WHITE
        if c == 'R':
            return curses.COLOR_RED
        if c == 'G':
            return curses.COLOR_GREEN
        if c == 'B':
            return curses.COLOR_BLUE
        if c == 'Y':
            return curses.COLOR_YELLOW
        if c == 'M':
            return curses.COLOR_MAGENTA
        if c == 'C':
            return curses.COLOR_CYAN
        # TODO: Throw Appropriate exception
        
    def lookup( self, fg_color = None, bg_color = None ):
        if isinstance(fg_color, basestring):
            fg_color = self.convert_char_code( fg_color )
        if isinstance(bg_color, basestring):
            bg_color = self.convert_char_code( bg_color )
            
        if fg_color == None:
            fg_color = self.fg_default
        if bg_color == None:
            bg_color = self.bg_default
            
        if (fg_color, bg_color) in self.pairs:
            return self.pairs[ fg_color, bg_color ]
        curses.init_pair( len(self.pairs), fg_color, bg_color )
        self.pairs[ fg_color, bg_color ] = len(self.pairs)
        return len(self.pairs) - 1

class CursesApplication:
    def __init__( self, model, widget, controller ):
        
        self.model = model
        self.widget = widget
        self.controller = controller
        
    def __enter__( self ):
        self.window = curses.initscr()
        height, width = self.window.getmaxyx()
        
        # Start up colors
        curses.start_color()
        self.color_manager = ColorManager()
        
        # Hide the cursor
        curses.curs_set(0)
        
        # Make sure we don't echo key presses
        curses.noecho()
        
        # Ensure that function / keypad keys work.
        self.window.keypad(1)
        
        # Ensure we're alerted of all mouse events.
        curses.mousemask( curses.ALL_MOUSE_EVENTS )
        
        # Make watching for key presses non-blocking
        self.window.nodelay(1)
        
        self.altchar_table = {
            u'\u250c' : curses.ACS_ULCORNER,
            u'\u2500' : curses.ACS_HLINE,
            u'\u2510' : curses.ACS_URCORNER,
            u'\u2502' : curses.ACS_VLINE,
            u'\u2514' : curses.ACS_LLCORNER,
            u'\u2518' : curses.ACS_LRCORNER,
            u'\u2524' : curses.ACS_RTEE,
            u'\u2534' : curses.ACS_BTEE,
            u'\u252c' : curses.ACS_TTEE,
            u'\u251c' : curses.ACS_LTEE,
            u'\u253c' : curses.ACS_PLUS }
        
        # TODO: Elegant way to handle errors?
        # TODO: Sizing?
        # TODO: Resizing?
        self.canvas = AsciiCanvas( width-1, height-1, self, 0, 0 )
        
        self.widget.set_canvas( self.canvas )
        
        return self
        
    def putchr( self, pos, c, fg_color = None, bg_color = None ):
        color = curses.color_pair( self.color_manager.lookup( fg_color, bg_color ) )
        
        x, y = pos
        if c in self.altchar_table:
            self.window.addch(y, x, self.altchar_table[c], color)
        else:
            self.window.addch(y, x, ord(c), color)
        
    def run( self ):
        while True:
            keycode = self.window.getch()
            if keycode != curses.ERR:
                # Check for mouse event...
                if keycode == curses.KEY_MOUSE:
                    (id, x, y, z, bstate) = curses.getmouse() # TODO: Include click types...
                    self.widget.handle_event( MouseClickEvent((x,y)) )
                else:
                    self.widget.handle_event( KeypressEvent(keycode) )
            self.controller.update()
            self.canvas.clear() # TODO: Make sure this  can be turned off for some canvases?
            self.widget.render()
            self.window.refresh()
            
    def __exit__( self, type, value, traceback ):
        curses.endwin()
        print self.color_manager.pairs
