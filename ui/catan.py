#!/usr/bin/python
# -*- coding: utf-8 -*-

class HexGridTile:
    def __init__( self, x, y ):
        z = None
        self._x = int(x)
        self._y = int(y) # TODO Assert...
        if z != None:
            assert x + y + z == 0
            
    def __hash__(self):
        return hash((self._x,self._y))
        
    @property
    def x(self):
        return self._x
        
    @property
    def y(self):
        return self._y
        
    @property
    def z(self):
        return -1 * ( self._x + self._y )
        
    @property
    def neighbors(self):
        return set([ HexGridTile(x + dx, y + dy) for dx, dy, dz in HexGridEdge.directions ])
        
    @property
    def corners(self):
        return set([ HexGridCorner(self, direction) for direction in HexGridCorner.directions ])
        
    @property
    def edges(self):
        return set([ HexGridEdge(self, direction) for direction in HexGridEdge.directions ])

class HexGridCorner:
    X = 1
    negY = 2
    Z = 3
    negX = 4
    Y = 5
    negZ = 6
    directions = [X, Y, Z, negX, negY, negZ]
    
    # Canonical directions are X, negX
    
    def __init__( self, hexloc, corner_direction ):
        x = hexloc.x
        y = hexloc.y

        if corner_direction == self.X:
            self.direction = self.X
            self.hexloc = hexloc
            
        elif corner_direction == self.Y:
            self.direction = self.X
            self.hexloc = HexGridTile( x - 1, y + 1 )
            
        elif corner_direction == self.Z:
            self.direction = self.X
            self.hexloc = HexGridTile( x - 1, y )
            
        elif corner_direction == self.negX:
            self.direction = self.negX
            self.hexloc = hexloc
                    
        elif corner_direction == self.negY:
            self.direction = self.negX
            self.hexloc = HexGridTile( x + 1, y - 1)
            
        elif corner_direction == self.negZ:
            self.direction = self.negX
            self.hexloc = HexGridTile( x + 1, y )
            
        else:
            raise InvalidDirectionError()
            
    @property
    def edges(self):
        if self.direction == self.X:
            return set([    HexGridEdge(self.hexloc, HexGridEdge.YX),
                            HexGridEdge(self.hexloc, HexGridEdge.XZ),
                            HexGridEdge(HexGridTile(self.hexloc.x + 1, self.hexloc.y), HexGridEdge.ZY) ])
        else:
            return set([    HexGridEdge(self.hexloc, HexGridEdge.XY),
                            HexGridEdge(self.hexloc, HexGridEdge.ZX),
                            HexGridEdge(HexGridTile(self.hexloc.x - 1, self.hexloc.y), HexGridEdge.YZ) ])
    
    @property
    def neighbors(self):
        if self.direction == self.X:
            return set([    HexGridCorner(self.hexloc, HexGridCorner.negY),
                            HexGridCorner(self.hexloc, HexGridCorner.negZ),
                            HexGridCorner(HexGridTile(self.hexloc.x + 2, self.hexloc.y - 1), HexGridCorner.negX)])
        else:
            return set([    HexGridCorner(self.hexloc, HexGridCorner.Y),
                            HexGridCorner(self.hexloc, HexGridCorner.Z),
                            HexGridCorner(HexGridTile(self.hexloc.x - 2, self.hexloc.y + 1), HexGridCorner.X)])
                            
            
    @property
    def tiles(self):
        if self.direction == self.X:
            return set([ self.hexloc ]) #TODO: Others
        else:
            return set([ self.hexloc ]) #TODO: Others
            
class HexGridEdge:
    XZ = (1,0,-1)
    XY = (1,-1,0)
    YZ = (0,1,-1)
    YX = (-1,1,0)
    ZY = (0,-1,1)
    ZX = (-1,0,1)
    directions = [XZ, XY, YZ, YX, ZY, ZX]
    
    # Canonical directions are XY, YZ, ZX
    
    def __init__( self, hexloc, edge_direction ):
        x = hexloc.x
        y = hexloc.y
        
        if edge_direction == self.XY:
            self.direction = self.XY
            self.hexloc = hexloc
        
        elif edge_direction == self.YX:
            self.direction = self.XY
            self.hexloc = HexGridTile( x + 1, y - 1 )
            
        elif edge_direction == self.YZ:
            self.direction = self.YZ
            self.hexloc = hexloc
            
        elif edge_direction == self.ZY:
            self.direction = self.YZ
            self.hexloc = HexGridTile( x, y - 1 )
            
        elif edge_direction == self.ZX:
            self.direction = self.ZX
            self.hexloc = hexloc
            
        elif edge_direction == self.XZ:
            self.direction = self.ZX
            self.hexloc = HexGridTile( x + 1, y )
            
        else:
            raise InvalidDirectionError()
            
    @property
    def ends(self):
        pass #TODO
        
    @property    
    def neighbors(self):
        pass #TODO
    
    @property    
    def tiles(self):
        pass #TODO
print HexGridEdge.directions
    

###
# Find the canvas coordanates to draw a sprite based on a hexloc
###        
def tile_coords( hexloc ):
    #########################
    # y_h # x_h # x_c # y_c #
    #########################
    # 0   # 0   # 0   # 0   #
    # 1   # 0   # 0   # 4   #
    # -1  # 1   # 12  # 0   #
    #########################
    
    # We expect a linear combination...
    
    x_h = hexloc.x
    y_h = hexloc.y
    return (6*x_h, 2*x_h + 4*y_h)
    
def corner_coords( cornerloc ):
    tile_x, tile_y = tile_coords( cornerloc.hexloc )
    if cornerloc.direction == HexGridCorner.X:
        return tile_x + 8, tile_y + 2
    else:
        return tile_x, tile_y + 2
        
def edge_coords( edgeloc ):
    tile_x, tile_y = tile_coords( edgeloc.hexloc )
    if edgeloc.direction == HexGridEdge.XY:
        return tile_x + 1, tile_y + 3
    if edgeloc.direction == HexGridEdge.YZ:
        return tile_x + 3, tile_y + 4
    else:
        return tile_x + 1, tile_y + 1   
    
#!/usr/bin/python
# -*- coding: utf-8 -*-

from Widget import *

from Canvas import *
from AsciiCanvas import *
from AsciiSprite import *

from Event import *
from EventType import *

SPRITE_CHARS = u'''  @───@
 /z    \\
@      x@
 \\y    /
  @───@'''
  
SPRITE_FG_MASK = u'''  BWWWG
 WW    W
R      WR
 WW    W
  GWWWB'''
  
SPRITE_BG_MASK = u'''  KKKKK
 KCCCCCK
KCCCCCCCK
 KCCCCCK
  KKKKK'''


THROTTLE_SPRITE = AsciiSprite(SPRITE_CHARS, SPRITE_FG_MASK, SPRITE_BG_MASK)

from catan_sprites import DIRMAP_SPRITE

def pseudorand(x, n):
    return int(hash(x)) % n
    
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
        
    def render_corner( self, corner, fg_color = None, bg_color = None ):
        self.canvas.putchr( corner_coords( corner ), '@', fg_color, bg_color )
        
    def render_edge( self, edge, fg_color = None, bg_color = None ):
        if edge.direction == HexGridEdge.XY:
            self.canvas.putchr( edge_coords( edge ), '\\', fg_color, bg_color )
        if edge.direction == HexGridEdge.YZ:
            x_, y_ = edge_coords( edge )
            self.canvas.putstr( edge_coords( edge ), u'───', fg_color, bg_color )
        if edge.direction == HexGridEdge.ZX:
            x_, y_ = edge_coords( edge )
            self.canvas.putchr( edge_coords( edge ), '/', fg_color, bg_color )
        
    def render( self ):
        for y in range(-20, 30):
            for x in range(-20, 30):
                hexloc = HexGridTile(x,y)
                cartloc = tile_coords(hexloc)
                if cartloc[0] < 0 or cartloc[1] < 0 or cartloc[0] >= self.canvas.size[0] - THROTTLE_SPRITE.size[0] or cartloc[1] >= self.canvas.size[1] - THROTTLE_SPRITE.size[1]: 
                    continue
                    
                for corner in hexloc.corners:
                    self.render_corner( corner )
                    
                for edge in hexloc.edges:
                    self.render_edge( edge )
                        
                self.canvas.putstr( ( cartloc[0] + 4, cartloc[1] + 1 ), str(x) )
                self.canvas.putstr( ( cartloc[0] + 4, cartloc[1] + 3 ), str(y) )
                
        hexloc = HexGridTile(3,1)
        for corner in hexloc.corners:
            self.render_corner( corner, 'Y' )
        for edge in hexloc.edges:
            self.render_edge( edge, 'G' )
            
        corner = HexGridCorner( hexloc, HexGridCorner.Y )
        self.render_corner( corner, 'B' )
        for edge in corner.edges:
            self.render_edge( edge, 'M' )
        for corner_ in corner.neighbors:
            self.render_corner( corner_, 'R' )

from CursesApplication import CursesApplication

from Controller import Controller
from Model import Model

model = Model()
widget = Throttle(model)
controller = Controller(model)

with CursesApplication( model, widget, controller ) as app:
    app.run()
