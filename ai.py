import time
import keyboard
import json
import random

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

def checkSeg(x, y, useHead = False, useEdges = True):
    if x < 0 or y < 0 or x > 14 or y > 14 and useEdges:
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
    'enclosed': 0.6,
}


def getModel():
    global priorities
    with open('model.model') as model:
        jsonDecoder = json.JSONDecoder()
        jsModel = jsonDecoder.decode(model.read())
        priorities = jsModel 
    randomizeStats()


def logAI(weights, weight):
    print(weights, list(weight.keys())[0].upper(), ' ' * (120 - (len(str(weights)) + len(str(weight)))), sep=': ', end='\r')


def randomizeStats():
    randomize = random.choice(['toApple', 'awayWall', 'enclosed'])
    change = random.randrange(-20,20,1)/100
    priorities[randomize] += change
    print(priorities)


def getFitness(score):
    try:
        aplX = (2 / ((pos[0] - abs(apple.x))))
        aplY = (2 / ((pos[0] - abs(apple.y))))
    except ZeroDivisionError:
        aplX = 0
        aplY = 0
    fitness = round(((aplX + aplY)/100) * score,2)
    if fitness > priorities['fitness']:
        priorities['fitness'] = fitness
        with open('model.model', 'w') as model:
            json.dump(priorities, model)



def aiTick(segs, apl, position, gridSize):
    global segments, apple, should, last, size, pos
    segments = segs
    apple = apl
    size = gridSize
    pos = position

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

    def predict(dictionary:dict):
        name = list(dictionary.keys())[0]
        predictX = {'left':-1,'right':1,'up':0,'down':0}
        predictY = {'left':0,'right':0,'up':-1,'down':1}
        neighbors = 0
        if checkSeg(pos[0]-1+predictX[name],pos[1]+predictY[name], useEdges=False): neighbors += 1
        if checkSeg(pos[0]+1+predictX[name],pos[1]+predictY[name], useEdges=False): neighbors += 1
        if checkSeg(pos[0]+predictX[name],pos[1]-1+predictY[name], useEdges=False): neighbors += 1
        if checkSeg(pos[0]+predictX[name],pos[1]+1+predictY[name], useEdges=False): neighbors += 1
        if neighbors < 3:
            dictionary[name] -= neighbors * priorities['enclosed']
        else:
            dictionary[name] -= 1000
        return round(dictionary[name],1)

    leftWeight = round((leftDist * priorities['awayWall']) + (appleDistX * priorities['toApple']) - (1000 * int(segL)),2)
    rightWeight = round((rightDist * priorities['awayWall']) + (-appleDistX * priorities['toApple']) - (1000 * int(segR)),2)
    upWeight = round((topDist * priorities['awayWall']) + (appleDistY * priorities['toApple']) - (1000 * int(segU)),2)
    downWeight = round((botDist * priorities['awayWall']) + (-appleDistY * priorities['toApple']) - (1000 * int(segD)),2)
    weights = [{'left':leftWeight},{'right':rightWeight},{'up':upWeight},{'down':downWeight}]
    weight = sorted(weights,key=predict,reverse=True)[0]
    # logAI(weights, weight)
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