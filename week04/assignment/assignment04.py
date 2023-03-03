'''
Requirements
1. Using two threads, put cars onto a shared queue, with one thread consuming
   the items from the queue and the other producing the items.
2. The size of queue should never exceed 10.
3. Do not call queue size to determine if maximum size has been reached. This means
   that you should not do something like this: 
        if q.size() < 10:
   Use the blocking semaphore function 'acquire'.
4. Produce a Plot of car count vs queue size (okay to use q.size since this is not a
   condition statement).
   
Questions:
1. Do you need to use locks around accessing the queue object when using multiple threads? 
   Why or why not?
   >No you do not
   >You do not need to because queues are thread safe
2. How would you define a semaphore in your own words?
   >A semaphore is a lock that doesn't allow for race condition.
   >It is a list or account of locks.
3. Read https://stackoverflow.com/questions/2407589/what-does-the-term-blocking-mean-in-programming.
   What does it mean that the "join" function is a blocking function? Why do we want to block?
   >The join function is a blocking function because it will prevent the threads or code from moving on past the join until all the threads are finished
   >We want to block to make sure that you are not exceding limited resources.
   >We also want to block because one portion of the code may need to finish for logic before continuing.
'''

from datetime import datetime
import time
import threading
import random
# DO NOT import queue

from plots import Plots

# Global Constants
MAX_QUEUE_SIZE = 10
SLEEP_REDUCE_FACTOR = 50

#########################
# NO GLOBAL VARIABLES!
#########################


class Car():
    """ This is the Car class that will be created by the factories """

    # Class Variables
    car_makes = ('Ford', 'Chevrolet', 'Dodge', 'Fiat', 'Volvo', 'Infiniti', 'Jeep', 'Subaru',
                 'Buick', 'Volkswagen', 'Chrysler', 'Smart', 'Nissan', 'Toyota', 'Lexus',
                 'Mitsubishi', 'Mazda', 'Hyundai', 'Kia', 'Acura', 'Honda')

    car_models = ('A1', 'M1', 'XOX', 'XL', 'XLS', 'XLE', 'Super', 'Tall', 'Flat', 'Middle', 'Round',
                  'A2', 'M1X', 'SE', 'SXE', 'MM', 'Charger', 'Grand', 'Viper', 'F150', 'Town', 'Ranger',
                  'G35', 'Titan', 'M5', 'GX', 'Sport', 'RX')

    car_years = [i for i in range(1990, datetime.now().year)]

    def __init__(self):
        # Make a random car
        self.model = random.choice(Car.car_models)
        self.make = random.choice(Car.car_makes)
        self.year = random.choice(Car.car_years)

        # Sleep a little.  Last statement in this for loop - don't change
        time.sleep(random.random() / (SLEEP_REDUCE_FACTOR))

        # Display the car that has just be created in the terminal
        self.display()

    def display(self):
        print(f'{self.make} {self.model}, {self.year}')


class QueueTwoFiftyOne():
    """ This is the queue object to use for this assignment. Do not modify!! """

    def __init__(self):
        self.items = []

    def size(self):
        return len(self.items)

    def put(self, item):
        self.items.append(item)

    def get(self):
        return self.items.pop(0)


class Manufacturer(threading.Thread):
    """ This is a manufacturer.  It will create cars and place them on the car queue """

    def __init__(self, semMax: threading.Semaphore, semEmpty: threading.Semaphore, q: QueueTwoFiftyOne, CARS_TO_PRODUCE):
        threading.Thread.__init__(self)
        self.semMax = semMax
        self.semEmpty = semEmpty
        self.q = q
        self.car_count = CARS_TO_PRODUCE

    def run(self):
        for i in range(self.car_count):
            """
            create a car
            place the car on the queue
            signal the dealer that there is a car on the queue
           """
            self.semMax.acquire()
            make_car = Car() # make a car using the Car class
            self.q.put(make_car) # put car on the queue
            self.semEmpty.release()
            

        # signal the dealer that there there are no more cars
        self.semMax.acquire()
        self.q.put(None) #This will end the while loop in Dealership
        self.semEmpty.release()


class Dealership(threading.Thread):
    """ This is a dealership that receives cars """

    def __init__(self, semMax: threading.Semaphore, semEmpty: threading.Semaphore, q: QueueTwoFiftyOne, queue_stats, lock):
        threading.Thread.__init__(self)
        self.semMax = semMax
        self.semEmpty = semEmpty
        self.q = q
        self.stats = queue_stats
        self.lock = lock

    def run(self):
        while True:
            """
            take the car from the queue
            signal the factory that there is an empty slot in the queue
            """
            self.semEmpty.acquire()
            with self.lock: #use a lock to protect data from being compromised by other threads
                car_to_sell = self.q.get() # remove item from queue
            if car_to_sell == None:
                break #end of production, end while loop
            self.stats[self.q.size()] += 1
            self.semMax.release()

            # Sleep a little after selling a car
            # Last statement in this for loop - don't change
            time.sleep(random.random() / (SLEEP_REDUCE_FACTOR))

            


def main():
    # Start a timer
    begin_time = time.perf_counter()

    # random amount of cars to produce
    CARS_TO_PRODUCE = random.randint(500, 600)

    semMax = threading.Semaphore(10) #create a lock that doesn't let it go past the limit
    semEmpty = threading.Semaphore(0)#create a lock to block it when empty
    q = QueueTwoFiftyOne()
    lock = threading.Lock()

    # This tracks the length of the car queue during receiving cars by the dealership,
    # the index of the list is the size of the queue.
    queue_stats = [0] * MAX_QUEUE_SIZE

    threads = []
    #create a manufacturer
    car_manufacturer = Manufacturer(semMax, semEmpty, q, CARS_TO_PRODUCE) 
    threads.append(car_manufacturer)

    #create a dealership
    car_dealership = Dealership(semMax, semEmpty, q, queue_stats, lock) 
    threads.append(car_dealership)

    # Start manufacturer and dealership
    for t in threads:
        t.start()

    #Wait for manufacturer and dealership to complete
    for t in threads:
        t.join()

    total_time = "{:.2f}".format(time.perf_counter() - begin_time)
    print(f'Total time = {total_time} sec')

    # Plot car count vs queue size
    xaxis = [i for i in range(1, MAX_QUEUE_SIZE + 1)]
    plot = Plots()
    plot.bar(xaxis, queue_stats,
             title=f'{sum(queue_stats)} Produced: Count VS Queue Size', x_label='Queue Size', y_label='Count')


if __name__ == '__main__':
    main()
