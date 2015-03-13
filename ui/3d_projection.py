from math import sin, cos, pi
import time

t = 0

dt = 0.1

omega = 0.7

theta = 0

class Cylinder:
        def __init__( self, center, radius, mark = '*' ):
                self.center = center
                self.radius = radius
                
                self.mark = mark

def rotate( cyl, theta ):
        radius = cyl.radius
        c_x, c_y = cyl.center
        n_x = cos(theta) * c_x - sin(theta) * c_y
        n_y = sin(theta) * c_x + cos(theta) * c_y
        return Cylinder( (n_x, n_y), radius, cyl.mark )
        
booster1 = Cylinder((6,0), 2.5, '1')
booster2 = Cylinder((0,6), 2.5, '2')
booster3 = Cylinder((-6,0), 2.5, '3')
booster4 = Cylinder((0,-6), 2.5, '4')
booster5 = Cylinder((0,0), 2.5, '5')

boosters = [ booster1, booster2, booster3, booster4, booster5 ]

x_offset = 10

def render_cyls( cyls ):
        row = []
        y_row = []
        def ins(i, char, y):
            while len(row) <= i:
                row.append(' ')
                y_row.append(None)
            if y_row[i] == None or y_row[i] > y:
                row[i] = char
                y_row[i] = y
                
        for cyl in cyls:
                for i in range( (x_offset + int(round( cyl.center[0] - cyl.radius ) )), (1 + x_offset + int(round( cyl.center[0] + cyl.radius ) )) ):
                    ins( i, cyl.mark, cyl.center[1] ) 
        print ''.join(row)
        print ''.join(row)
        print ''.join(row)
        

while True:
        time.sleep(0.05)
        theta = omega * t
        render_cyls( [ rotate( booster, theta ) for booster in boosters] )
        print "____________________"
        t += dt

