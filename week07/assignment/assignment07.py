'''
Requirements
1. Create a multiprocessing program that connects the processes using Pipes.
2. Create a process from each of the following custom process classes, 
   Marble_Creator, Bagger, Assembler, and Wrapper.
3. The Marble_Creator process will send a marble to the Bagger process using
   a Pipe.
4. The Bagger process will create a Bag object with the required number of
   marbles. 
5. The Bagger process will send the Bag object to the Assembler using a Pipe.
6. The Assembler process will create a Gift object and send it to the Wrapper
   process using a Pipe.
7. The Wrapper process will write to a file the current time followed by the 
   gift string.
8. The program should not hard-code the number of marbles, the various delays,
   nor the bag count. These should be obtained from the settings.txt file.
   
Questions:
1. Why can you not use the same pipe object for all the processes (i.e., why 
   do you need to create three different pipes)?
   > You have to create different pipes because they are flowing between different functions
   >I think of pipes more like convayer belts
2. Compare and contrast pipes with queues (i.e., how are the similar or different)?
   >Pipes and queues are similar because they still have a first in first out concept
   >Pipes are different because you have to have a parent and a child end to the pipe connection.
'''

from datetime import datetime
import json
import multiprocessing as mp
import os
import random
import time

CONTROL_FILENAME = 'settings.txt'
BOXES_FILENAME = 'boxes.txt'

# Settings constants
MARBLE_COUNT = 'marble-count'
CREATOR_DELAY = 'creator-delay'
BAG_COUNT = 'bag-count'
BAGGER_DELAY = 'bagger-delay'
ASSEMBLER_DELAY = 'assembler-delay'
WRAPPER_DELAY = 'wrapper-delay'

# No Global variables


class Bag():
    def __init__(self):
        self.items = []

    def add(self, marble):
        self.items.append(marble)

    def get_size(self):
        return len(self.items)

    def __str__(self):
        return str(self.items)


class Gift():
    def __init__(self, large_marble, marbles):
        self.large_marble = large_marble
        self.marbles = marbles

    def __str__(self):
        marbles = str(self.marbles)
        marbles = marbles.replace("'", "")
        return f'Large marble: {self.large_marble}, marbles: {marbles[1:-1]}'


class Marble_Creator(mp.Process):
    """ This class "creates" marbles and sends them to the bagger """

    colors = ('Gold', 'Orange Peel', 'Purple Plum', 'Blue', 'Neon Silver',
              'Tuscan Brown', 'La Salle Green', 'Spanish Orange', 'Pale Goldenrod', 'Orange Soda',
              'Maximum Purple', 'Neon Pink', 'Light Orchid', 'Russian Violet', 'Sheen Green',
              'Isabelline', 'Ruby', 'Emerald', 'Middle Red Purple', 'Royal Orange', 'Big Dip O’ruby',
              'Dark Fuchsia', 'Slate Blue', 'Neon Dark Green', 'Sage', 'Pale Taupe', 'Silver Pink',
              'Stop Red', 'Eerie Black', 'Indigo', 'Ivory', 'Granny Smith Apple',
              'Maximum Blue', 'Pale Cerulean', 'Vegas Gold', 'Mulberry', 'Mango Tango',
              'Fiery Rose', 'Mode Beige', 'Platinum', 'Lilac Luster', 'Duke Blue', 'Candy Pink',
              'Maximum Violet', 'Spanish Carmine', 'Antique Brass', 'Pale Plum', 'Dark Moss Green',
              'Mint Cream', 'Shandy', 'Cotton Candy', 'Beaver', 'Rose Quartz', 'Purple',
              'Almond', 'Zomp', 'Middle Green Yellow', 'Auburn', 'Chinese Red', 'Cobalt Blue',
              'Lumber', 'Honeydew', 'Icterine', 'Golden Yellow', 'Silver Chalice', 'Lavender Blue',
              'Outrageous Orange', 'Spanish Pink', 'Liver Chestnut', 'Mimi Pink', 'Royal Red', 'Arylide Yellow',
              'Rose Dust', 'Terra Cotta', 'Lemon Lime', 'Bistre Brown', 'Venetian Red', 'Brink Pink',
              'Russian Green', 'Blue Bell', 'Green', 'Black Coral', 'Thulian Pink',
              'Safety Yellow', 'White Smoke', 'Pastel Gray', 'Orange Soda', 'Lavender Purple',
              'Brown', 'Gold', 'Blue-Green', 'Antique Bronze', 'Mint Green', 'Royal Blue',
              'Light Orange', 'Pastel Blue', 'Middle Green')

    def __init__(self, sender, marble_count, creator_delay):
        mp.Process.__init__(self)
        self.sender = sender
        self.marble_count = marble_count
        self.creator_delay = creator_delay

    def run(self):
        '''
        for each marble:
            send the marble (one at a time) to the bagger
              - A marble is a random name from the colors list above
            sleep the required amount
        Let the bagger know there are no more marbles
        '''
        for m in range(self.marble_count):
            color = random.choice(self.colors)
            self.sender.send(color)
            time.sleep(self.creator_delay)
        self.sender.send("DONE")
        self.sender.close()


class Bagger(mp.Process):
    """ Receives marbles from the marble creator, then there are enough
        marbles, the bag of marbles are sent to the assembler """

    def __init__(self, receiver, sender, bag_count: int, bagger_delay: float):
        mp.Process.__init__(self)
        self.sender = sender
        self.receiver = receiver
        self.bag_count = bag_count
        self.bagger_delay = bagger_delay

    def run(self):
        '''
        while there are marbles to process
            collect enough marbles for a bag
            send the bag to the assembler
            sleep the required amount
        tell the assembler that there are no more bags
        '''
        bag = Bag()
        while True:
            marble = self.receiver.recv()
            if marble == "DONE":
                self.sender.send("DONE")
                break
            bag.add(marble)
            if bag.get_size() == self.bag_count:
                self.sender.send(bag)
                time.sleep(self.bagger_delay)
                bag = Bag()
        self.sender.close()
        self.receiver.close()


class Assembler(mp.Process):
    """ Take the set of marbles and create a gift from them.
        Sends the completed gift to the wrapper """
    marble_names = ('Lucky', 'Spinner', 'Sure Shot', 'The Boss',
                    'Winner', '5-Star', 'Hercules', 'Apollo', 'Zeus')

    def __init__(self, receiver, sender, assembler_delay: float):
        mp.Process.__init__(self)
        self.sender = sender
        self.receiver = receiver
        self.assembler_delay = assembler_delay
        

    def run(self):
        '''
        while there are bags to process
            create a gift with a large marble (random from the name list) and the bag of marbles
            send the gift to the wrapper
            sleep the required amount
        tell the wrapper that there are no more gifts
        '''
        while True:
            bag = self.receiver.recv()
            if bag == "DONE":
                self.sender.send("DONE")
                break
            gift = Gift(random.choice(self.marble_names), bag)
            self.sender.send(gift)
            time.sleep(self.assembler_delay)
        self.sender.close()
        self.receiver.close()

class Wrapper(mp.Process):
    """ Takes created gifts and wraps them by placing them in the boxes file """

    def __init__(self, receiver, gift_count, wrapper_delay: float):
        mp.Process.__init__(self)
        self.receiver = receiver
        self.gift_count = gift_count
        self.wrapper_delay = wrapper_delay

    def run(self):
        '''
        open file for writing
        while there are gifts to process
            save gift to the file with the current time
            sleep the required amount
        (see prepare00.md for helpful file operations)
        '''
        while True:
            gift = self.receiver.recv()
            if gift == "DONE":
                break
            with open(BOXES_FILENAME, "a") as file:
                file.writelines(f"Created - {str(datetime.now().time())}: {str(gift)}\n")
            self.gift_count.value += 1
            time.sleep(self.wrapper_delay)
        self.receiver.close()
        

def display_final_boxes(filename):
    """ Display the final boxes file to the log file -  Don't change """
    if os.path.exists(filename):
        print(f'Contents of {filename}')
        with open(filename) as boxes_file:
            for line in boxes_file:
                print(line.strip())
    else:
        print(
            f'ERROR: The file {filename} doesn\'t exist.  No boxes were created.')


def load_json_file(filename):
    if os.path.exists(filename):
        with open(filename) as json_file:
            data = json.load(json_file)
        return data
    else:
        return {}


def main():
    """ Main function """

    # Start a timer
    begin_time = time.perf_counter()

    # Load settings file
    settings = load_json_file(CONTROL_FILENAME)
    if settings == {}:
        print(f'Problem reading in settings file: {CONTROL_FILENAME}')
        return

    print(f'Marble count                = {settings[MARBLE_COUNT]}')
    print(f'settings["creator-delay"]   = {settings[CREATOR_DELAY]}')
    print(f'settings["bag-count"]       = {settings[BAG_COUNT]}')
    print(f'settings["bagger-delay"]    = {settings[BAGGER_DELAY]}')
    print(f'settings["assembler-delay"] = {settings[ASSEMBLER_DELAY]}')
    print(f'settings["wrapper-delay"]   = {settings[WRAPPER_DELAY]}')

    
    marble_count = settings[MARBLE_COUNT]
    creator_delay = settings[CREATOR_DELAY]
    bag_count = settings[BAG_COUNT]
    bagger_delay = settings[BAGGER_DELAY]
    assembler_delay = settings[ASSEMBLER_DELAY]
    wrapper_delay = settings[WRAPPER_DELAY]
    
    # create Pipes between creator -> bagger -> assembler -> wrapper
    creator_start_pipe, creator_end_pipe = mp.Pipe()
    bagger_start_pipe, bagger_end_pipe = mp.Pipe()
    assembler_start_pipe, assembler_end_pipe = mp.Pipe()
    
    # create variable to be used to count the number of gifts
    gift_count = mp.Manager().Value("i", 0)
    # delete final boxes file
    if os.path.exists(BOXES_FILENAME):
        os.remove(BOXES_FILENAME)

    print('Create the processes')

    # Create the processes (ie., classes above)
    creator = Marble_Creator(creator_start_pipe, marble_count, creator_delay)
    bagger = Bagger(creator_end_pipe, bagger_start_pipe, bag_count, bagger_delay)
    assembler = Assembler(bagger_end_pipe, assembler_start_pipe, assembler_delay)
    wrapper = Wrapper(assembler_end_pipe, gift_count, wrapper_delay)
    
    print('Starting the processes')
    creator.start()
    bagger.start()
    assembler.start()
    wrapper.start()

    print('Waiting for processes to finish')
    creator.join()
    bagger.join()
    assembler.join()
    wrapper.join()

    display_final_boxes(BOXES_FILENAME)

    # Print the number of gifts created.
    print(f"{gift_count.value} gifts created")

if __name__ == '__main__':
    main()
