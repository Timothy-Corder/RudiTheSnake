import PIL
import PIL.IcnsImagePlugin
import PIL.Image
import PIL.ImageTk
from tkinter import TclError
import tkinter as tk

def setup(blkSize, rndr, root:tk.Tk = None):
    global snake, rots, blockSize, segments, render
    render = rndr
    segments = []
    blockSize = blkSize
    rots = {'u':0,'l':90,'d':180,'r':270}
    snake = {}
    def getSprites():
        global appleImg
        snek = PIL.Image.open('snek.png')
        spriteCount = 5
        sprites = []
        for i in range(spriteCount):
            sprites.append(snek.crop((0,i*8,8,(i*8)+8)))

        types = ['head', 'forward', 'r', 'l', 'tail']
        for i in range(spriteCount):
            snake[types[i]] = sprites[i]
        if render:
            appleImg = PIL.Image.open('appl.png')
            appleImg.load()
            appleImg = appleImg.resize((blockSize,blockSize),0)
            appleImg = PIL.ImageTk.PhotoImage(appleImg)
    getSprites()

class Apple():
    def __init__(self,x,y):
        self.x = x
        self.y = y
        if render:
            self._label = tk.Label(image=appleImg,border=0,width=blockSize,height=blockSize)
    def grid(self, **kwargs):
        if render:
            try:
                self._label.grid(kwargs)
            except TclError:
                pass

class Segment():
    def __init__(self, lifetime, facing, segType, x, y):
        self.lifetime = lifetime
        self.facing = facing
        self.segType = segType
        self.x = x
        self.y = y
        if render:
            image = snake['head'].resize((blockSize,blockSize),0)
            image = image.rotate(rots[self.facing])
            image = PIL.ImageTk.PhotoImage(image)
            self._label = tk.Label(image=image,border=0, width=blockSize, height=blockSize)
            self._label.image = image
    def tick(self):
        try:
            self.lifetime -= 1
            if self.lifetime == 1:
                self.segType = 'tail'
            if self.lifetime < 1:
                self.destroy()
        except RuntimeError:
            exit()
    def destroy(self):
        if render:
            self._label.destroy()
        segments[segments.index(self)] = None
    def spriteRefresh(self):
        if render:
            image = snake[self.segType].resize((blockSize,blockSize),0)
            image = image.rotate(rots[self.facing])
            img = PIL.ImageTk.PhotoImage(image)
            self._label.config(image=img)
            self._label.image = img

    def grid(self, **kwargs):
        if render:
            try:
                self._label.grid(kwargs)
            except TclError:
                pass

class Player():
    def __init__(self, x, y, direction):
        self._dirOpps = {
                        'u':'d',
                        'r':'l',
                        'l':'r',
                        'd':'u'
                        }
        self._turns = []
        self.x = x
        self.y = y
        self.direction = direction
        self.length = 3
        self.moves = 0
    def move(self, gridSize):
        if len(self._turns) > 0:
            turning = (self._turns.pop(0))
            olDir = self.direction
            self.direction = turning
        else:
            olDir = None
            turning = 'forward'
        if turning != 'forward':
            match(olDir):
                case 'u':
                    turning = turning
                case 'd':
                    turning = self._dirOpps[turning]
                case 'l':
                    match(turning):
                        case 'u':
                            turning = 'r'
                        case 'd':
                            turning = 'l'
                case 'r':
                    match(turning):
                        case 'u':
                            turning = 'l'
                        case 'd':
                            turning = 'r'
        match(self.direction):
            case 'u':
                self.y -= 1
            case 'd':
                self.y += 1
            case 'l':
                self.x -= 1
            case 'r':
                self.x += 1
        try:
            if turning != 'forward':
                segments[-1].segType = turning
                segments[-1].facing = self.direction

        except IndexError:
            pass
        self.makeSeg(self.x, self.y, 'forward', gridSize)
        self.moves += 1
        # return turning
    def addTurn(self, direct):
        if len(self._turns) == 0:
            if self.direction == self._dirOpps[direct] or self.direction == direct:
                return False
        elif self._turns[-1] == self._dirOpps[direct]:
            return False
        if len(self._turns) <= 4:
            try:
                if direct in self._turns:
                    return False
            except:
                pass
            self._turns.append(direct)
            return True
        else:
            return False
    
    def makeSeg(self, x, y, direct, gridSize):
        global segments
        segments.append(Segment(self.length, self.direction, direct, x, y))
        if x < gridSize['x'] and y < gridSize['y']:
            segments[-1].grid(column=x,row=y)
