import math, pygame, logging, olpcgames
from olpcgames import textsprite
from gettext import gettext as _
from pygame.locals import *
from random import *

log = logging.getLogger( 'Cell Management' )
log.setLevel( logging.DEBUG )


################################################################################
# Colors
################################################################################
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
black = (0,0,0)
white = (255,255,255)

################################################################################
# Utility Functions
################################################################################

def dist(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    
def polToCart(r, angle):
    # here the center is (300, 300)
    angle *= math.pi / 180.0
    x = int(r * math.cos(angle)) + 300
    y = int(r * math.sin(angle)) + 300
    return x, y

  
################################################################################
# the Super Group... because regular groups aren't good enough
################################################################################

class Group(pygame.sprite.Group):
    def set_x(self, x): self.x = x
    def set_y(self, y): self.y = y


################################################################################
# Pieces
################################################################################

class Cell():
    def __init__(self, game, species):
        self.game = game
        self.species = species
        
    def seti(self, i):
        self.i = i

    def setPos(self, x, y):
        self.x = x
        self.y = y
        text = textsprite.TextSprite(text = _(str(self.species + 1)),
                                     size = 20, color = black)
        text.rect.center = (self.x, self.y - 20)
        self.text = Group((text))

    def makePrisoners(self):
        self.prisoners = Group()
        self.prisoners.set_x(self.x)
        self.prisoners.set_y(self.y)
        prisoner1 = Prisoner(self.game, self.species, self.x, self.y, 'left')
        prisoner2 = Prisoner(self.game, self.species, self.x, self.y, 'right')
        self.prisoners.add((prisoner1, prisoner2))
    
    def setMyHS(self, hs):
        self.my_hs = hs

    def getMyHS(self):
        return self.my_hs

    def setAdjHS(self, hs):
        self.adj_hs = hs

    def getAdjHS(self):
        return self.adj_hs
    
    def addPrisoner(self, prisoner):
        self.prisoners.add(prisoner)

    def update(self):
        if (len(self.prisoners) != 0 and
            self.getAdjHS().canHelp()):
            prisoner = self.prisoners.sprites()[0]
            self.prisoners.remove(prisoner)
            self.getMyHS().addPrisoner(prisoner)

        
class EscapeArea():
    def __init__(self, game):
        self.game = game
        self.prisoners = Group()
        self.prisoners.set_x(300)
        self.prisoners.set_y(300)

    def addPrisoner(self, prisoner):
        self.prisoners.add(prisoner)

           
class Hideout():
    def __init__(self, game, species, cell, HorF):
        self.game = game
        self.species = species
        self.my_cell = cell
        self.HorF = HorF
        self.prisoners = Group()
        self.escArea = game.escArea

    def seti(self, int):
        self.i = int

    def setPos(self, x, y):
        self.x = x
        self.y = y
        self.prisoners.set_x(self.x)
        self.prisoners.set_y(self.y)
        text = textsprite.TextSprite(text = _(str(self.species + 1)),
                                     size = 20, color = white)
        text.rect.center = (self.x, self.y - 20)
        self.text = Group((text))

        
    def isOccupied(self):
        if len(self.prisoners.sprites()) == 0:
            return False
        return True
    
    def vacate(self):
        if self.isOccupied():
            x = self.prisoners.sprites()[0]
            self.prisoners.remove(x)
            self.my_cell.prisoners.add(x)
            
    def canHelp(self):
        return ((self.isOccupied() and self.HorF == "f") or
                (not self.isOccupied() and self.HorF == "h"))
            
    def escape(self, prisoner):
        self.escArea.addPrisoner(prisoner)

    def addPrisoner(self, prisoner):
        if not self.isOccupied():
            self.prisoners.add((prisoner))
        else:
            self.escape(prisoner)


################################################################################
# Sprites
################################################################################

class MovingSprite(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
    
    def angle(self, x, y):
        distance = dist(self.rect.centerx, self.rect.centery, x, y)
        angle = math.acos(float(x - self.rect.centerx) / float(distance))
        angle *= 180.0 / math.pi # because pygame likes degrees
        if y > self.rect.centery:
            angle = 360 - angle
        return angle

    def move(self, angle):
        dx = math.cos(angle * math.pi / 180) * self.speed
        dy = -math.sin(angle * math.pi / 180) * self.speed
        self.rect.move_ip(dx, dy)

class Prisoner(MovingSprite):
    def __init__(self, game, species, x, y, LorR):
        MovingSprite.__init__(self)
        self.game = game
        self.species = species
        self.speed = randint(16, 22)
        self.image = pygame.image.load(str(self.species + 1) + ".gif").convert()
        self.image.set_colorkey(white)
        self.rect = self.image.get_rect()
        self.LorR = LorR
        
        if self.LorR == 'left':
            self.rect.center = (x - 16, y)
        else:
            self.rect.center = (x + 16, y)
    
    def update(self):
        m = pygame.mouse.get_pos()
        d = dist(m[0], m[1], self.rect.centerx, self.rect.centery)
        button1, button2, button3 = pygame.mouse.get_pressed()
        a = self.game.escArea.prisoners
        if ((button1 or button2 or button3) and d <= 15 and
            self in a.sprites() and not self.game.guard.moving):
            a.remove(self)
            for i in range(0,6):
                if self.species == self.game.cells[i].getMyHS().species:
                    self.game.cells[i].getMyHS().addPrisoner(self)
                    
        x = self.groups()[0].x
        y = self.groups()[0].y

        if self.LorR == 'left':
            x -= 16
        else:
            x += 16

        d = dist(x, y, 300, 300)
        if d < 65:
            angle = ((60 * self.species) - 90) % 360
            x, y = polToCart(30, angle)

        d = dist(x, y, self.rect.centerx, self.rect.centery)
        if d > self.speed:
            self.move(self.angle(x, y))
        else:
            self.rect.center = (x, y)
        
            
class Guard(MovingSprite):
    def __init__(self, game):
        MovingSprite.__init__(self)
        self.game = game
        self.speed = 15
        self.image = pygame.image.load("guard.bmp").convert()
        self.image.set_colorkey(white)
        self.rect = self.image.get_rect()
        self.moving = False
        self.rect.center = (550, 300)
        self.destx, self.desty = 600, 400
        self.i ,self.stop = 0, 0

    def setDest(self, dest):
        self.destx, self.desty = dest[0], dest[1]
        
    def circ(self, x, y):
        distance = dist(300, 300, x, y)
        angle = math.acos(float(x - 300) / float(distance))
        angle *= 180.0 / math.pi # because pygame likes degrees
        if y > 300:
            angle = 360 - angle
        angle = (480 - angle) % 360
        i = int(angle / 60)
        return i

    def path(self, i):
        d = 290
        angle = []
        for j in range(-90, 400, 60):
            angle.append(j)
        x = int(d * math.cos(angle[i] * math.pi / 180.0)) + 300
        y = int(d * math.sin(angle[i] * math.pi / 180.0)) + 300
        return (x,y)
   
    def update(self):
        m = pygame.mouse.get_pos()
        d1 = dist(m[0], m[1], 300, 300)
        button1, button2, button3 = pygame.mouse.get_pressed()
        if ((button1 or button2 or button3)
            and not self.moving and d1 > 70):
            self.moving = True
            self.i = self.circ(m[0], m[1])
            self.stop = self.i
            self.setDest(self.path(self.i))
         
        d2 = dist(self.rect.centerx,
                  self.rect.centery,
                  self.destx, self.desty)

        if d2 > self.speed and self.moving:
            self.move(self.angle(self.destx, self.desty))
        elif self.moving:
            self.game.cells[self.i].update()
            self.game.cells[self.i].getAdjHS().vacate()
            self.i = (self.i + 1) % 6
            if self.i != self.stop:
                self.setDest(self.path(self.i))
            else: self.moving = False


################################################################################
# Game
################################################################################

class Game():
    def __init__(self, cell_count = 6, fps = 30):
        pygame.init()
    
        # fullscreen
        if olpcgames.ACTIVITY:
            self.screen = pygame.display.set_mode(olpcgames.ACTIVITY.game_size)
        else:
            self.screen = pygame.display.set_mode((800, 600))
            #pygame.mouse.set_visible(0) # this makes the mouse invisible
    
        # time stuff
        self.clock = pygame.time.Clock()
        self.fps = fps
    
        # make board
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill((250, 250, 250))
        self.board = pygame.image.load("cell-background.gif")
        self.board.convert()

        # number of cells
        self.cell_count = cell_count
        
        # make pieces
        self.escArea = EscapeArea(self)
        
        hf = ["h", "f"] * (self.cell_count / 2)
        shuffle(hf)
            
        self.cells = []

        for i in range(0, cell_count):
            x = Cell(self, i)
            self.cells.append(x)
        
        nums = range(1, cell_count)
        shuffle(nums)

        n = 0
        while len(nums) != 0:
            x = nums.pop(0)
            y = Hideout(self, x, self.cells[x], hf.pop())
            self.cells[n].setAdjHS(y)
            self.cells[x].setMyHS(y)
            n = x

        y = Hideout(self, 0, self.cells[0], hf.pop())
        self.cells[n].setAdjHS(y)
        self.cells[0].setMyHS(y)
       
        # now shuffle the cells (and effectively the hiding spaces)
        shuffle(self.cells)

        # and let the cells and hiding spaces know where they've been put
        for j in range(0, cell_count):
            a = self.cells[j]
            a.seti(j)
            a.getAdjHS().seti(j)
            angle = ((60 * j) - 90) % 360
            x1, y1 = polToCart(200, angle)
            x2, y2 = polToCart(115, angle)
            a.setPos(x1, y1)
            a.getAdjHS().setPos(x2, y2)
            
            # since we're at it, let's use our crayon to color on the board
            # this is so we can tell if a space is 'hostile' or 'friendly'
            color = red
            if self.cells[j].getAdjHS().HorF == "f":
                color = green
            pygame.draw.circle(self.board, color, (x2,y2), 42) # the crayon

        # lastly... sprites
        self.guard = Guard(self)
        self.guards = Group((self.guard))
        for i in self.cells:
            i.makePrisoners()
            
    
    def mainloop(self):
        good_job = False
        running = True
        while running:
            self.clock.tick(self.fps)

            if (not self.guard.moving and
                len(self.escArea.prisoners.sprites()) == self.cell_count):
                running, good_job = False, True

            #Handle Input Events
            for event in pygame.event.get():
                # this one is for the box in the top right marked X
                if event.type == QUIT:
                    running = False      
                # and this one is for the "ESC" key
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    running = False

            # update sprites
            self.guards.update()
            self.escArea.prisoners.update()
            for i in range(0,6):
                self.cells[i].prisoners.update()
                self.cells[i].getAdjHS().prisoners.update()
                self.cells[i].text.update()
                
            # draw everything
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.board, (0, 0))
            self.guards.draw(self.screen)
            self.escArea.prisoners.draw(self.screen)
            for i in range(0,6):
                a = self.cells[i]
                a.prisoners.draw(self.screen)
                a.getAdjHS().prisoners.draw(self.screen)
                a.text.draw(self.screen)
                a.getAdjHS().text.draw(self.screen)
            pygame.display.flip()

        while good_job:
            print "yea!"
            


def main():
    cellgame = Game()
    cellgame.mainloop()

if __name__ == "__main__":
    logging.basicConfig()
    main()

pygame.quit ()
