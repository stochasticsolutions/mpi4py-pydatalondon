'''
Conway's Game Of Life With Tkinter In Python

Based on:
     https://gist.github.com/philipnorton42/dfb332ce247e9d79e29626bae79651af

See https://www.hashbangcode.com/article/conways-game-life-tkinter-python
for a detailed breakdown of this code.
'''

import math
import random
import sys

from tkinter import Canvas, Tk

USAGE = ('\nUSAGE: python game_of_life.py [CELLS-PER-EDGE [PIXELS-PER-CELL]]\n'
         ' e.g.: python game_of_life.py 100 10\n')


class GameOfLife(Tk):
    def __init__(self, width_and_height=400, resolution=100):
        super().__init__()
        self.generation = 0

        self.title("Game of life")

        # Prevent the application window from being resized.
        self.resizable(False, False)

        # Set the height and width of the application.
        self.width_and_height = width_and_height
        self.resolution = resolution
        self.size_factor = self.width_and_height / self.resolution

        # Set up the size of the canvas.
        self.geometry(
            str(self.width_and_height) + "x" + str(self.width_and_height)
        )

        # Create the canvas widget and add it to the Tkinter application window.
        self.canvas = Canvas(
            self,
            width=self.width_and_height,
            height=self.width_and_height,
            bg='white',
        )
        self.canvas.pack()

        # Set a click event on the canvas.
        self.canvas.bind('<Button-1>', self.canvas_click_event)
        self.canvas.bind('<Button1-Motion>', self.canvas_click_event)

        # Set up an empty game grid.
        self.grid = [
            [0 for x in range(self.resolution)] for x in range(self.resolution)
        ]

        # Fill the game grid with random data.
        for x in range(0, self.resolution):
            for y in range(0, self.resolution):
                self.grid[x][y] = random.randint(0, 1)

        # Generate the game board.
        self.generate_board()

        # Start the timer.
        self.after(1000, self.update_board)

    def update_board(self):
        # Clear the canvas.
        self.canvas.delete("all")
        # Run the next generation and update the game grid.
        self.grid = self.run_generation()
        # Generate the game board with the current population.
        self.generate_board()
        # Set the next tick in the timer.
        self.after(1, self.update_board)
        self.generation += 1
        print(self.generation)

    def generate_board(self):
        # Draw a square on the game board for every live cell in the grid.
        for x in range(0, self.resolution):
            for y in range(0, self.resolution):
                realx = x * self.size_factor
                realy = y * self.size_factor
                if self.grid[x][y] == 1:
                    self.draw_square(realx, realy, self.size_factor)

    def draw_square(self, y, x, size):
        # Draw a square on the canvas.
        self.canvas.create_rectangle(
            x, y, x + size, y + size, fill='black', outline='black'
        )

    def run_generation(self):
        # Generate new empty grid to populate with result of generation.
        return_grid = [
            [0 for x in range(self.resolution)] for x in range(self.resolution)
        ]

        # Iterate over the grid.
        for x in range(0, self.resolution):
            for y in range(0, self.resolution):
                neighbours = self.number_neighbours(x, y)
                if self.grid[x][y] == 1:
                    # Current cell is alive.
                    if neighbours < 2:
                        # Cell dies (rule 1).
                        return_grid[x][y] = 0
                    elif neighbours == 2 or neighbours == 3:
                        # Cell lives (rule 2).
                        return_grid[x][y] = 1
                    elif neighbours > 3:
                        # Cell dies (rule 3).
                        return_grid[x][y] = 0
                else:
                    # Current cell is dead.
                    if neighbours == 3:
                        # Make cell live (rule 4).
                        return_grid[x][y] = 1
        return return_grid

    def number_neighbours(self, x, y):
        count = 0

        '''
        Count the number of cells that are alive in the following coordiantes.
        -x -y | x -y | +x -y
        -x  y |      | +x  y
        -x +y | x +y | +x +y
        '''
        xrange = [x - 1, x, x + 1]
        yrange = [y - 1, y, y + 1]

        for x1 in xrange:
            for y1 in yrange:
                if x1 == x and y1 == y:
                    # Don't count this cell.
                    continue
                try:
                    if self.grid[x1][y1] == 1:
                        count += 1
                except IndexError:
                    continue
        return count

    def canvas_click_event(self, event):
        # Work out where the mouse is in relation to the grid.
        gridx = math.floor((event.y / self.width_and_height) * self.resolution)
        gridy = math.floor((event.x / self.width_and_height) * self.resolution)

        # Make that cell alive.
        self.grid[gridx][gridy] = 1


if __name__ == "__main__":
    board_edge = 50
    pixels_per_cell = 10
    if len(sys.argv) > 1:
        if sys.argv[1].lower() in ('-h', '--help', 'help', '-?'):
            print(USAGE)
            sys.exit(0)
        try:
            board_edge = int(sys.argv[1])
        except ValueError:
            print(USAGE, file=sys.stderr)
            sys.exit(1)
        if len(sys.argv) > 2:
            pixels_per_cell = int(sys.argv[2])

    # Create the class and kick off the Tkinter loop.
    tkinter_canvas = GameOfLife(board_edge * pixels_per_cell, board_edge)
    tkinter_canvas.mainloop()
