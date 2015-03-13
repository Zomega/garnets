class Player:
    def __init__( self, color ):
        self.color = []
        
class Board:
    def __init__( self ):
        self.tiles = set() # OR A MAP, location to tile...
        self.cities = set()
        self.road = set()
        self.robber = None # TODO: Desert location

class TileType:
    FOREST = 'FOREST'
    MOUNTAIN = 'MOUNTAIN'
    PLAINS = 'PLAINS'
    FIELDS = 'FIELDS'
    PASTURE = 'PASTURE'
    DESERT = 'DESERT'
    PORT = 'PORT'
            
class Tile:
    def __init__( self, board, type, location, roll ):
        self.type = type
        
    def produced_resources( self, roll ):
        return self.roll == roll

class City:
    def __init__( self, name, tier, location ):
        self.name = name
        self.tier = tier
        self.location = location
        
    def gleaned_resources( self, roll ):
        pass
        
roll = randint(1,6) + random.randint(1,6)
