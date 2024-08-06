import tkinter as tk
import random

import SnkDefs
import sys

import threading
import time

class SnakeGame:
    def __init__(self, network, render=True, show=False):
        self.render = render
        self.show = show
        if __name__ == '__main__':
            self.render = False if (len(sys.argv) == 2 and sys.argv[1] == '--no-render') else True
        self.failId = ''
        self.noFitness = False
        self.tps = 60
        self.gridSize = {'x': 15, 'y': 15}
        self.blockSize = 32
        self.player = SnkDefs.Player(self.gridSize['x']//2, self.gridSize['y']//2, 'r')
        self.lastCheck = self.player.length
        if self.render:
            self.root = tk.Tk()
            SnkDefs.setup(self.blockSize, self.render, self.root)
            self.setupWindow()
        else:
            SnkDefs.setup(self.blockSize, self.render)
            self.failThread = threading.Thread(target=self.renderlessFail)
            self.failThread.start()
        self.makeApple()
        self.running = False
        self.network = network

    def renderlessFail(self):
        while True:
            length = self.player.length
            time.sleep(2)
            if self.player.length != length:
                self.running = False
                break

    def setupWindow(self):
        self.root.title('Snake AI')
        self.root.config(background='#000000')
        self.root.tk.call('tk', 'scaling', '-displayof', '.', 1)
        for i in range(self.gridSize['x']):
            self.root.columnconfigure(i, minsize=self.blockSize, weight=1)
        for i in range(self.gridSize['y']):
            self.root.rowconfigure(i, minsize=self.blockSize, weight=1)
        self.root.resizable(False, False)
        self.root.bind("<Escape>", self.endGame)
        self.root.bind("<space>", self.newGame)

    def makeApple(self):
        while True:
            x = random.randint(0, self.gridSize['x']-1)
            y = random.randint(0, self.gridSize['y']-1)
            if not self.checkSeg(x, y, True):
                break
        try:
            self.apple._label.destroy()
        except:
            pass
        self.apple = SnkDefs.Apple(x, y)
        if self.render:
            self.apple.grid(column=x, row=y)

    def checkSeg(self, x, y, useHead=False):
        segments = SnkDefs.segments if useHead else SnkDefs.segments[:-1]
        return any(segment.x == x and segment.y == y for segment in segments)

    def checkAppl(self, x, y):
        return self.apple.x == x and self.apple.y == y

    def start(self):
        self.running = True
        if self.render:
            self.root.after(int(1000/self.tps), self.gameLoop)
            if not self.show:
                self.failId = self.root.after(3000, self.failCheck)
            self.root.mainloop()
        else:
            while self.running:
                self.gameLoop()
        return self.player.length, self.player.moves

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

            if self.render:
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
                if self.render:
                    self.root.after(int(1000/self.tps), self.controllerTick)
                    self.root.after(int(1000/self.tps), self.gameLoop)
                else:
                    self.controllerTick()
        else:
            self.stop()

    def controllerTick(self):
        from ai import aiTick
        if not self.running:
            return
        else:
            outputs = aiTick(self.network, SnkDefs.segments, self.apple, (self.player.x, self.player.y), self.gridSize, self.player.length)
            
            down = []
            
            for key in outputs:
                if outputs[key]:
                    down.append(key[0])

            for button in down:
                self.player.addTurn(button)

    def stop(self, event = None):
        self.running = False
        if self.render:
            self.root.after(200, self.root.destroy)

    def endGame(self, event):
        self.stop()
        if self.render:
            self.root.quit()
        exit()
    
    def failCheck(self):
        if self.player.length == self.lastCheck:
            self.stop(None)
        if (self.player.moves / max(self.player.length - 3, 1)) > 300:
            self.stop(None)
        else:
            self.lastCheck = self.player.length
            if self.render:
                self.failId = self.root.after(5000, self.failCheck)

    def newGame(self, event):
        if self.render:
            self.noFitness = True
        self.stop()
        
    def cleanup(self):
        if self.render and self.failId != '':
            self.root.after_cancel(self.failId)

if __name__ == '__main__':
    import ai
    # while True:
    #     game = SnakeGame()
    #     game.start()
    #     game.cleanup()