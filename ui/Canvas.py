class Canvas:
    def __init__( self, width, height, parent = None, parent_x_offset = None, parent_y_offset = None ):
    
        self.__width = width
        self.__height = height
        
        self.parent = parent
        self.parent_x_offset = parent_x_offset
        self.parent_y_offset = parent_y_offset
        
    @property
    def width( self ):
        return self.__width
        
    @property
    def height( self ):
        return self.__height
        
    @property
    def size( self ):
        return self.__width, self.__height
        
    def subcanvas( self, x, y, width, height ):
        raise NotImplementedError("Subclasses of canvas must implement a subcanvas method.")
        
    def transform_parent_point( self, x, y ):
        if not self.parent:
            raise InvalidCanvasLocationError("Requested a transform from a non-existent parent!")
        x_new = x - parent_x_offset
        
class Paradigm:
    ASCII = 0
    PIXEL = 1
    VECTOR = 2
