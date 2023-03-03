'''
Requirements
1. Create a recursive program that finds the solution path for each of the provided mazes.
'''

import math
from screen import Screen
from maze import Maze
import cv2
import sys

SCREEN_SIZE = 800
COLOR = (0, 0, 255)


def solve(maze, row, col, solution_path):
    # Mark the current cell as visited
    maze.move(row, col, COLOR)

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
            if solve(maze, move_row, move_col, solution_path):
                return True

            # If we didn't find a solution from the new position, backtrack
            
            solution_path.pop()
            maze.restore(row, col)

    # If we have tried all possible moves and haven't found a solution, return False
    return False


def get_solution_path(filename):
    # create a Screen Object that will contain all of the drawing commands
    screen = Screen(SCREEN_SIZE, SCREEN_SIZE)
    screen.background((255, 255, 0))

    maze = Maze(screen, SCREEN_SIZE, SCREEN_SIZE, filename)

    row, col = maze.start_pos
    solution_path = [(row, col)]

    solve(maze, row, col, solution_path)

    print(f'Number of drawing commands for {filename}: {screen.get_command_count()}')

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

    return solution_path


def find_paths():
    files = ('./verysmall.bmp', './verysmall-loops.bmp',
             './small.bmp', './small-loops.bmp',
             './small-odd.bmp', './small-open.bmp', './large.bmp', './large-loops.bmp')

    print('*' * 40)
    print('Part 1')
    for file_path in files:
        print()
        print(f'File: {file_path}')
        solution_path = get_solution_path(file_path)
        print(f'Found path has length   = {len(solution_path)}')
    print('*' * 40)


def main():
    # prevent crashing in case of infinite recursion
    sys.setrecursionlimit(5000)
    find_paths()


if __name__ == "__main__":
    main()
