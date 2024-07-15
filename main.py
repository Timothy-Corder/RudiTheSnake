
import tkinter as tk
from tkinter import TclError
import PIL
import PIL.IcnsImagePlugin
import PIL.Image
import PIL.ImageTk
from threading import Thread
import time
import random
import keyboard
import ai





def main():
    global controlRunning
    tick, half = makeGlobals()
    half.start()
    def kThread():
        while True:
            if not running:
                buttons.waitFor('start', tps)
                dontKill.set(False)
                break
            time.sleep(1)
    def kill(*args):
        root.destroy()
    def endGame(event):
        root.destroy()
        exit()

    root.bind("<Escape>", endGame)
    killThread = Thread(target=kThread)
    killThread.start()
    root.focus_force()
    tick.start()
    dontKill = tk.BooleanVar(root)
    dontKill.trace_add('write',kill)
    root.bind()
    root.mainloop()
    controlRunning = False
    

class Joystick():
    def __init__(self,u,l,d,r,start):
        ...
    def getPressed(self):
        pressed = []
        if keyboard.is_pressed('w'):
            pressed.append('u')
        if keyboard.is_pressed('a'):
            pressed.append('l')
        if keyboard.is_pressed('s'):
            pressed.append('d')
        if keyboard.is_pressed('d'):
            pressed.append('r')
        if keyboard.is_pressed('space'):
            pressed.append('start')
        return pressed
    def isActive(self, target):
        return (target in self.getPressed())
    def waitFor(self, target):
        while target not in self.getPressed():
            time.sleep((1/tps)/2)
    def getButtons(self):
        return []
    
class Apple():
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self._label = tk.Label(root,image=appleImg,border=0,width=blockSize,height=blockSize)
    def grid(self, **kwargs):
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
        image = snake['head'].resize((blockSize,blockSize),0)
        image = image.rotate(rots[self.facing])
        image = PIL.ImageTk.PhotoImage(image,master=root)
        self._label = tk.Label(root,image=image,border=0, width=blockSize, height=blockSize)
        self._label.image = image
    def tick(self):
        try:
            self.lifetime -= 1
            if self.lifetime == 1:
                self.segType = 'tail'
            if self.lifetime < 1:
                self._label.destroy()
                segments[segments.index(self)] = ''
        except RuntimeError:
            exit()
    def spriteRefresh(self):
            image = snake[self.segType].resize((blockSize,blockSize),0)
            image = image.rotate(rots[self.facing])
            img = PIL.ImageTk.PhotoImage(image,master=root)
            self._label.config(image=img)
            self._label.image = img

    def grid(self, **kwargs):
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
    def move(self):
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
        makeSeg(self.x, self.y, 'forward')
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
        

def makeApple():
    global apple

    apple._label.destroy()

    while True:
        x = random.randint(0,gridSize['x']-1)
        y = random.randint(0,gridSize['y']-1)
        if not checkSeg(x,y, True):
            break

    apple = Apple(x,y)
    apple.grid(column = x, row = y)





def makeGlobals():     
    global length, gridSize, blockSize, segments, tps, player, running, apple, snake, rots, buttons, controlRunning,buzzer

    rots = {'u':0,'l':90,'d':180,'r':270}

    controlRunning = True
    buttons = ai.Joystick(16,19,21,20,26)
    snake = {}
    running = True
    tps = 2
    gridSize = {'x': 15, 'y': 15}
    player = Player(gridSize['x']//2,gridSize['y']//2,'r')
    length = 3
    blockSize = 32
    segments = []
    makeWindow()
    getSprites()
    apple = Apple(0,0)
    makeApple()
    tickThread = Thread(target=tick)
    halfThread = Thread(target=controllerTick)

    return tickThread, halfThread


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
    appleImg = PIL.Image.open('appl.png')
    appleImg.load()
    appleImg = appleImg.resize((blockSize,blockSize),0)
    appleImg = PIL.ImageTk.PhotoImage(appleImg,master=root)


def controllerTick():
    while running:
        ai.aiTick(segments, apple, (player.x,player.y))

        try:
            down = buttons.getPressed()
            if 'start' in down:
                down = down[:-1]
            if down == None:
                down = []
            print(down)
        except ValueError:
            down = buttons.getPressed()

        if len(down) != 0:
            for button in down:
                player.addTurn(button)
        time.sleep((1/tps)/4)

def tick():
    global running, tps
    while running:
        if (0 <= player.x < gridSize['x']) and (0 <= player.y < gridSize['y']):
            if checkSeg(player.x, player.y):
                break
            for segment in segments:
                segment.tick()
            try:
                if segments[0] == '':
                    segments.pop(0)
            except IndexError:
                pass
            player.move()
            for segment in segments[:-1]:
                segment.spriteRefresh()
            if checkAppl(player.x, player.y):
                player.length += 1
                for segment in segments:
                    segment.lifetime += 1

                makeApple()
                if player.length % 3 == 0:
                    tps *= 1.1
            time.sleep(1/tps)
        else:
            break
    running = False


def makeSeg(x, y, direct):
    global segments
    segments.append(Segment(player.length, player.direction, direct, x, y))
    if x < gridSize['x'] and y < gridSize['y']:
        segments[-1].grid(column=x,row=y)


def checkSeg(x, y, useHead = False):
    if useHead:
        sgmnts = segments
    else:
        sgmnts = segments[:-1]
    for segment in sgmnts:
        if segment.x == x and segment.y == y:
            return True
    return False


def checkAppl(x,y): return (apple.x == x and apple.y == y)


        


def makeWindow():
    global root
    root = tk.Tk()
    root.config(background='#000000')
    root.tk.call('tk', 'scaling', '-displayof', '.', 1)
    for i in range(gridSize['x']):
        root.columnconfigure(i,minsize=blockSize,weight=1)
    for i in range(gridSize['y']):
        root.rowconfigure(i,minsize=blockSize,weight=1)
    # root.columnconfigure(gridSize['x'])
    root.resizable(False,False)



if __name__ == '__main__':
    tk.NoDefaultRoot()
    while True: 
        
        main()
        components = buttons.getButtons()
        for comp in components:
            while True:
                try:
                    comp.close()
                    break
                except:
                    time.sleep(0.5)