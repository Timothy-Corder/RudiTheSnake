import time
import keyboard

class Joystick():
    def __init__(self,u,l,d,r,start):
        ...
    def getPressed(self):
        global should
        pressed = []
        if should['up']:
            pressed.append('u')
        if should['left']:
            pressed.append('l')
        if should['down']:
            pressed.append('d')
        if should['right']:
            pressed.append('r')
        if keyboard.is_pressed('space'):
            pressed.append('start')
        return pressed
    def isActive(self, target):
        return (target in self.getPressed())
    def waitFor(self, target, tps):
        while target not in self.getPressed():
            time.sleep((1/tps)/2)
    def getButtons(self):
        return []

should = \
{
    'up': False,
    'down': False,
    'left': False,
    'right': False,
}

def checkSeg(x, y, useHead = False):
    if x < 0 or y < 0 or x > 14 or y > 14:
        return True
    if useHead:
        sgmnts = segments[1:]
    else:
        sgmnts = segments[1:-1]
    for segment in sgmnts:
        try:
            if segment.x == x and segment.y == y:
                return True
        except AttributeError:
            pass
    return False


def checkAppl(x,y): return (apple.x == x and apple.y == y)

priorities = \
{
    'toApple': 1.0,
    'awayWall': 0.1,
}

def aiTick(segs, apl, pos, gridSize):
    global segments, apple, should, last, size
    segments = segs
    apple = apl
    size = gridSize

    should['right'] = False
    should['left'] = False
    should['up'] = False
    should['down'] = False

    x = pos[0]
    y = pos[1]
    leftDist = x
    rightDist = size['x'] - (x + 1)
    topDist = y
    botDist = size['y'] - (y + 1)
    appleDistX = pos[0] - apple.x
    appleDistY = pos[1] - apple.y
    segL = checkSeg(pos[0]-1,pos[1])
    segR = checkSeg(pos[0]+1,pos[1])
    segU = checkSeg(pos[0],pos[1]-1)
    segD = checkSeg(pos[0],pos[1]+1)

    def sortDict(dictionary:dict): return dictionary[list(dictionary.keys())[0]]
    def predict(dictionary:dict):
        sortDict(dictionary)
        predictX = {}
        [list(dictionary.keys())[0]]

    leftWeight = (leftDist * priorities['awayWall']) + (appleDistX * priorities['toApple']) - (1000 * int(segL))
    rightWeight = (rightDist * priorities['awayWall']) + (-appleDistX * priorities['toApple']) - (1000 * int(segR))
    upWeight = (topDist * priorities['awayWall']) + (appleDistY * priorities['toApple']) - (1000 * int(segU))
    downWeight = (botDist * priorities['awayWall']) + (-appleDistY * priorities['toApple']) - (1000 * int(segD))
    weights = [{'left':leftWeight},{'right':rightWeight},{'up':upWeight},{'down':downWeight}]
    weight = sorted(weights,key=predict,reverse=True)[0]
    print(weights)
    should[list(weight.keys())[0]] = True
    # match(weight):
    #     case 'left':
    #         should['left'] = True
    #     case 'right':
    #         should['right'] = True
    #     case 'up':
    #         should['up'] = True
    #     case 'down':
    #         should['down'] = True
    
    
    """
    if pos[0] < apl.x and not checkSeg(pos[0]+1,pos[1]):
        should['right'] = True
        last = 'horizontal'
    elif pos[0] > apl.x and not checkSeg(pos[0]-1,pos[1]):
        should['left'] = True
        last = 'horizontal'
    elif pos[1] > apl.y and not checkSeg(pos[0],pos[1]-1):
        should['up'] = True
        last = 'vertical'
    elif pos[1] < apl.y and not checkSeg(pos[0],pos[1]+1):
        should['down'] = True
        last = 'vertical'
    chosen = False
    for key in should:
        if should[key]:
            chosen = True
    if not chosen:
        match last:
            case 'horizontal':
                if not checkSeg(pos[0],pos[1]-1):
                    should['up'] = True
                    chosen = True
                elif not checkSeg(pos[0],pos[1]+1):
                    should['down'] = True
                    chosen = True
            case 'vertical':
                if not checkSeg(pos[0]-1,pos[1]):
                    should['left'] = True
                    chosen = True
                elif not checkSeg(pos[0]+1,pos[1]):
                    should['right'] = True
                    chosen = True
    if not chosen:
        panic(pos)
    
def panic(pos):
    print('PANIC!')
    if not checkSeg(pos[0],pos[1]-1):
        should['up'] = True
        last = 'vertical'
    elif not checkSeg(pos[0],pos[1]+1):
        should['down'] = True
        last = 'vertical'
    elif not checkSeg(pos[0]+1,pos[1]):
        should['right'] = True
        last = 'horizontal'
    elif not checkSeg(pos[0]-1,pos[1]):
        should['left'] = True
        last = 'horizontal'

"""

# def toNums():
#     array = []
#     for _ in range(15):
#         arRow = []
#         for __ in range(15):
#             arRow.append(0)
#         array.append(arRow)
#     for i in range(15):
#         for j in range(15):
#             if checkSeg(i, j, True):
#                 array[i][j] = 1
#     array[position[1]][position[0]] == 2
#     array[apple.x][apple.y] == 3
            
#     print()
#     for row in array:
#         print(row)