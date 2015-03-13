from Canvas import Canvas, Paradigm

class AsciiCanvas(Canvas):
    def __init__( self, width, height, parent = None, parent_x_offset = None, parent_y_offset = None ):
        # TODO: Ensure consistent units of chars
        Canvas.__init__( self, width, height, parent, parent_x_offset, parent_y_offset )
        self.__contents__ = [ [ ' ' for _ in range( self.width ) ] for _ in range( self.height ) ]
        self.__fg__ = [ [ None for _ in range( self.width ) ] for _ in range( self.height ) ]
        self.__bg__ = [ [ None for _ in range( self.width ) ] for _ in range( self.height ) ]
        
    def subcanvas( self, x, y, width, height ):
        return AsciiCanvas( width, height, self, x, y)
        
    def clear( self ):
        for x in range(self.width):
            for y in range(self.height):
                self.putchr( (x,y), ' ', None, None )
        
    @property
    def type( self ):
        return "AsciiCanvas"
        
    @property
    def paradigm( self ):
        return Paradigm.ASCII
        
    def putchr( self, pos, c, fg_color = None, bg_color = None ):
        x, y  = pos
        # TODO: Safety checks
        self.__contents__[y][x] = c
        self.__fg__[y][x] = fg_color
        self.__bg__[y][x] = bg_color
        if self.parent:
            self.parent.putchr( ( x + self.parent_x_offset, y + self.parent_y_offset), c, fg_color, bg_color )
    def putstr( self, pos, s, fg_color = None, bg_color = None ):
        if s == '':
            return
        self.putchr(pos, s[0], fg_color, bg_color )
        x, y = pos
        self.putstr( ( x + 1, y ), s[1:], fg_color, bg_color )
        
    def putsprite( self, pos, sprite ):
        x, y = pos
        width, height = sprite.size
        for dx in range(width):
            for dy in range(height):
                c, fg_color, bg_color = sprite.get( dx, dy )
                if c == ' ' and ( fg_color == None or fg_color == ' ' ) and ( bg_color == None or bg_color == ' ' ):
                    continue # in this case, we shouldn't draw anything, designated transparent?
                self.putchr( (x+dx,y+dy), c, fg_color, bg_color )
    def paint_rect( self, tl, br, fg_color = None, bg_color = None ):
        x, y = tl
        x_, y_ = br
        width = x_ - x + 1
        height = y_ - y + 1
        for dx in range(width):
            for dy in range(height):
                c = self.__contents__[y+dy][x+dx]
                
                fg = fg_color
                if fg == None:
                    fg = self.__fg__[y+dy][x+dx]
                
                bg = bg_color
                if bg == None:
                    bg = self.__bg__[y+dy][x+dx]
                    
                self.putchr( (x+dx,y+dy), c, fg, bg )
        
    def __repr__( self ):
        return '<--->\n' + '\n'.join([ ''.join(row) for row in self.__contents__ ]) + '\n<--->'
