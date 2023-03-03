'''
Requirements
1. Create a recursive, multithreaded program that finds the exit of each maze.
   
Questions:
1. It is not required to save the solution path of each maze, but what would
   be your strategy if you needed to do so?
   >I would create a dictionary of the maze file for the key and a tuple of tupled coordinates for each maze for the value.
   >It would be shared between each thread so I would need to put a lock in place. It would only add the maze if it didn't already exist and only once it found the final path
2. Is using threads to solve the maze a depth-first search (DFS) or breadth-first search (BFS)?
   Which search is "better" in your opinion? You might need to define better. 
   (see https://stackoverflow.com/questions/20192445/which-procedure-we-can-use-for-maze-exploration-bfs-or-dfs)
   >BFS returns the shortest path. In my opinion this is better because it is more efficient. 
   >DFS will give one path including backtracking, I believe. So for memory sake, BFS should be better.
'''

import math
import threading
from screen import Screen
from maze import Maze
import sys
import cv2

SCREEN_SIZE = 800
COLOR = (0, 0, 255)
COLORS = (
    (0, 0, 255),
    (0, 255, 0),
    (255, 0, 0),
    (255, 255, 0),
    (0, 255, 255),
    (255, 0, 255),
    (128, 0, 0),
    (128, 128, 0),
    (0, 128, 0),
    (128, 0, 128),
    (0, 128, 128),
    (0, 0, 128),
    (72, 61, 139),
    (143, 143, 188),
    (226, 138, 43),
    (128, 114, 250)
)

# Globals
current_color_index = 0
thread_count = 0
stop = False


def get_color():
    """ Returns a different color when called """
    global current_color_index
    if current_color_index >= len(COLORS):
        current_color_index = 0
    color = COLORS[current_color_index]
    current_color_index += 1
    return color


def solve_find_end(maze):
    """ finds the end position using threads.  Nothing is returned """
    global thread_count
    thread_count += 1

    def find_end_recursive(maze, row, col, solution_path):
        """ Recursive function to find the end position """
        maze.move(row, col, get_color())

    # Base case: if we have reached the end position, return True
        if (row, col) == maze.end_pos:
            solution_path.append((row, col))
            return True

        # Check all possible moves
        possible_moves = maze.get_possible_moves(row, col)
        for move_row, move_col in possible_moves:
            if maze.can_move_here(move_row, move_col):
                # Add the current position to the solution path
                solution_path.append((move_row, move_col))

                # Recursively try to solve the maze from the new position
                if find_end_recursive(maze, move_row, move_col, solution_path):
                    return True

                # If we didn't find a solution from the new position, backtrack
                solution_path.pop()

            # Recursively search in all four directions
            directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
            for d in directions:
                new_row, new_col = row + d[0], col + d[1]
                new_path = solution_path + [(new_row, new_col)]
            # if not maze.is_valid(new_row, new_col):
            #     continue
                t = threading.Thread(target=find_end_recursive, args=(new_row, new_col, new_path), name=f'Thread {thread_count}')
                t.start()
        # If we have tried all possible moves and haven't found a solution, return False
            start_row, start_col = maze.get_start_pos()
            find_end_recursive(maze, start_row, start_col, solution_path)
        return False

        

    # Start recursive search from the start position
    


def find_end(filename, delay):

    global thread_count

    # create a Screen Object that will contain all of the drawing commands
    screen = Screen(SCREEN_SIZE, SCREEN_SIZE)
    screen.background((255, 255, 0))

    maze = Maze(screen, SCREEN_SIZE, SCREEN_SIZE, filename, delay=delay)

    solve_find_end(maze)

    print(f'Number of drawing commands = {screen.get_command_count()}')
    print(f'Number of threads created  = {thread_count}')

    done = False
    speed = 1
    while not done:
        if screen.play_commands(speed):
            key = cv2.waitKey(0)
            if key == ord('+'):
                speed = max(0, speed - 1)
            elif key == ord('-'):
                speed += 1
            elif key != ord('p'):
                done = True
        else:
            done = True


def find_ends():
    files = (
        ('verysmall.bmp', True),
        ('verysmall-loops.bmp', True),
        ('small.bmp', True),
        ('small-loops.bmp', True),
        ('small-odd.bmp', True),
        ('small-open.bmp', False),
        ('large.bmp', False),
        ('large-loops.bmp', False)
    )

    print('*' * 40)
    print('Part 2')
    for filename, delay in files:
        print()
        print(f'File: {filename}')
        find_end(filename, delay)
    print('*' * 40)


def main():
    # prevent crashing in case of infinite recursion
    sys.setrecursionlimit(5000)
    find_ends()


if __name__ == "__main__":
    main()
