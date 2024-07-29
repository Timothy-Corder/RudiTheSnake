import tkinter as tk
import time
import random
import ai
import SnkDefs
import sys

render = False if (len(sys.argv) == 2 and sys.argv[1] == '--no-render') else True

class SnakeGame:
    def __init__(self):
        self.failId = ''
        self.root = tk.Tk()
        self.noFitness = False
        self.tps = 30
        self.gridSize = {'x': 15, 'y': 15}
        self.blockSize = 32
        self.player = SnkDefs.Player(self.gridSize['x']//2, self.gridSize['y']//2, 'r')
        SnkDefs.setup(self.blockSize, self.root, render)
        self.makeApple()
        self.lastCheck = self.player.length
        self.buttons = ai.Joystick()
        ai.getModel()
        self.setupWindow()
        self.running = False

    def setupWindow(self):
        self.root.title(('Snake AI' if render else 'Training...'))
        self.root.config(background='#000000')
        self.root.tk.call('tk', 'scaling', '-displayof', '.', 1)
        if render:
            for i in range(self.gridSize['x']):
                self.root.columnconfigure(i, minsize=self.blockSize, weight=1)
            for i in range(self.gridSize['y']):
                self.root.rowconfigure(i, minsize=self.blockSize, weight=1)
        self.root.resizable(False, False)
        self.root.bind("<Escape>", self.endGame)
        self.root.bind("<space>", self.newGame)

    def makeApple(self):
        if hasattr(self, 'apple'):
            self.apple._label.destroy()
        while True:
            x = random.randint(0, self.gridSize['x']-1)
            y = random.randint(0, self.gridSize['y']-1)
            if not self.checkSeg(x, y, True):
                break
        self.apple = SnkDefs.Apple(x, y, self.root)
        if render:
            self.apple.grid(column=x, row=y)

    def checkSeg(self, x, y, useHead=False):
        segments = SnkDefs.segments if useHead else SnkDefs.segments[:-1]
        return any(segment.x == x and segment.y == y for segment in segments)

    def checkAppl(self, x, y):
        return self.apple.x == x and self.apple.y == y

    def start(self):
        self.running = True
        self.root.after(int(1000/self.tps), self.gameLoop)
        self.root.after(5000, self.failCheck)
        self.root.mainloop()

    def gameLoop(self):
        if not self.running:
            return

        if (0 <= self.player.x < self.gridSize['x']) and (0 <= self.player.y < self.gridSize['y']):
            if self.checkSeg(self.player.x, self.player.y):
                self.stop()
                return
            

            for segment in SnkDefs.segments:
                segment.tick()

            SnkDefs.segments = [seg for seg in SnkDefs.segments if seg is not None]

            self.player.move(self.gridSize)

            for segment in SnkDefs.segments[:-1]:
                segment.spriteRefresh()

            if self.checkAppl(self.player.x, self.player.y):
                self.player.length += 1
                for segment in SnkDefs.segments:
                    segment.lifetime += 1
                self.makeApple()
                if self.player.length % 3 == 0:
                    self.tps *= 1.1

            if self.running:
                self.root.after(int(1000/self.tps), self.controllerTick)
                self.root.after(int(1000/self.tps), self.gameLoop)
        else:
            self.stop()

    def controllerTick(self):
        if not self.running:
            return
        else:
            ai.aiTick(SnkDefs.segments, self.apple, (self.player.x, self.player.y), self.gridSize, self.player.length)
            try:
                down = self.buttons.getPressed()
                if 'start' in down:
                    down = down[:-1]
                if down is None:
                    down = []
            except ValueError:
                down = self.buttons.getPressed()

            for button in down:
                self.player.addTurn(button)
            

    def stop(self):
        self.running = False
        self.root.after(200, self.root.destroy)
        if self.failId != '':
            self.root.after_cancel(self.failId)

    def endGame(self, event):
        self.stop()
        self.root.quit()
        exit()
    
    def failCheck(self):
        if self.player.length == self.lastCheck:
            self.newGame(None)
        else:
            self.lastCheck = self.player.length
            self.failId = self.root.after(5000,self.failCheck)

    def newGame(self, event):
        if render:
            self.noFitness = True
        self.stop()
        
    def cleanup(self):
        if not self.noFitness:
            print('Calculating new Fitness')
            print(f'New Fitness: {ai.getFitness(self.player.length)}')
        components = self.buttons.getButtons()
        for comp in components:
            while True:
                try:
                    comp.close()
                    break
                except:
                    time.sleep(0.5)

if __name__ == '__main__':
    while True:
        game = SnakeGame()
        game.start()
        game.cleanup()