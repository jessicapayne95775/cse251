'''
Requirements
1. Using multiple threads, put cars onto a shared queue, with one or more thread consuming
   the items from the queue and one or more thread producing the items.
2. The size of queue should never exceed 10.
3. Do not call queue size to determine if maximum size has been reached. This means
   that you should not do something like this: 
        if q.size() < 10:
   Use the blocking semaphore function 'acquire'.
4. Produce a Plot of car count vs queue size (okay to use q.size since this is not a
   condition statement).
5. The number of cars produced by the manufacturer must equal the number of cars bought by the 
   dealership. Use necessary data objects (e.g., lists) to prove this. There is an assert in 
   main that must be used.
   
Questions:
1. How would you define a barrier in your own words?
   > a barrier is something that doesn't allow the threads to pass until a certain condtion is met which
   > is making sure the threads finish a section of code before moving on
2. Why is a barrier necessary in this assignment?
   > It is necessary to prevent a sentinal being sent before the cars are actually done 
   > being manufactured by multiple manufacturers. 
'''

from datetime import datetime, timedelta
import time
import threading
import random

# Global Constants
MAX_QUEUE_SIZE = 10
SLEEP_REDUCE_FACTOR = 50

# NO GLOBAL VARIABLES!


class Car():
    """ This is the Car class that will be created by the manufacturers """

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

        # Display the car that has was just created in the terminal
        #self.display()

    def display(self):
        print(f'{self.make} {self.model}, {self.year}')


class QueueTwoFiftyOne():
    """ This is the queue object to use for this assignment. Do not modify!! """

    def __init__(self):
        self.items = []
        self.max_size = 0

    def get_max_size(self):
        return self.max_size

    def put(self, item):
        self.items.append(item)
        if len(self.items) > self.max_size:
            self.max_size = len(self.items)

    def get(self):
        return self.items.pop(0)


class Manufacturer(threading.Thread):
    """ This is a manufacturer.  It will create cars and place them on the car queue """

    def __init__(self, semMax: threading.Semaphore, semEmpty: threading.Semaphore, q: QueueTwoFiftyOne, barrier: threading.Barrier, manufacturer_stats, thread_id, dealer_count):
        self.cars_to_produce = random.randint(200, 300)     # Don't change
        threading.Thread.__init__(self)
        self.semMax = semMax
        self.semEmpty = semEmpty
        self.q = q
        self.barrier = barrier
        self.stats = manufacturer_stats
        self.thread_id = thread_id
        self.dealer_count = dealer_count

    def run(self):
        for i in range(self.cars_to_produce):
            """
            create a car
            place the car on the queue
            signal the dealer that there is a car on the queue
           """
            self.semMax.acquire()
            make_car = Car() # make a car using the Car class
            self.q.put(make_car) # put car on the queue
            self.semEmpty.release()
            self.stats[self.thread_id] += 1
            #wait until all of the manufacturers are finished producing cars
        # "Wake up/signal" the dealerships one more time. 
        # Select one manufacturer to do this (hint: pass in and use the manufacturer_id)
        self.barrier.wait()
        if self.thread_id == 0: #putting the sentinal on only 1 manufacturer
            for d in range(self.dealer_count):
                self.semMax.acquire()
                self.q.put(None) #This will end the while loop in Dealership
                self.semEmpty.release()


class Dealership(threading.Thread):
    """ This is a dealer that receives cars """

    def __init__(self, semMax: threading.Semaphore, semEmpty: threading.Semaphore, q: QueueTwoFiftyOne, dealer_stats, lock, thread_id):
        threading.Thread.__init__(self)
        self.semMax = semMax
        self.semEmpty = semEmpty
        self.q = q
        self.stats = dealer_stats
        self.lock = lock
        self.thread_id = thread_id

    def run(self):
        while True:
            self.semEmpty.acquire()
            with self.lock: #use a lock to protect data from being compromised by other threads
                car_to_sell = self.q.get() # remove item from queue
            if car_to_sell == None:
                break #end of production, end while loop
            self.stats[self.thread_id] += 1
            self.semMax.release()

            # Sleep a little - don't change.  This is the last line of the loop
            time.sleep(random.random() / (SLEEP_REDUCE_FACTOR))


def run_production(manufacturer_count, dealer_count):
    """ This function will do a production run with the number of
        manufacturers and dealerships passed in as arguments.
    """

    # Start a timer
    begin_time = time.perf_counter()

    semMax = threading.Semaphore(10) #create a lock that doesn't let it go past the limit
    semEmpty = threading.Semaphore(0)#create a lock to block it when empty
    q = QueueTwoFiftyOne()
    lock = threading.Lock()
    barrier = threading.Barrier(manufacturer_count)
    dcount = 0 #used for dealer thread_id
    mcount = 0 # used for manufacturer_id

    # This is used to track the number of cars receives by each dealer
    dealer_stats = list([0] * dealer_count)
    manufacturer_stats = list([0] * manufacturer_count)

    m_threads = []
    d_threads = []

    #  create your manufacturers, each manufacturer will create CARS_TO_CREATE_PER_MANUFACTURER
    for m in range(manufacturer_count):
        m = Manufacturer(semMax, semEmpty, q, barrier, manufacturer_stats, mcount, dealer_count)
        m_threads.append(m)
        mcount += 1 # increment the count for the id

    #  create your dealerships
    for d in range(dealer_count):
        d = Dealership(semMax, semEmpty, q, dealer_stats, lock, dcount)
        m_threads.append(d)
        dcount += 1

    #  Start all dealerships
    for d_thread in d_threads:
        d_thread.start()

    #  Start all manufacturers
    for m_thread in m_threads:
        m_thread.start()

    #  Wait for manufacturers and dealerships to complete
    for mt in m_threads:
        mt.join()
    for dt in d_threads:
        dt.join()

    run_time = time.perf_counter() - begin_time

    # This function must return the following - only change the variable names, if necessary.
    # manufacturer_stats: is a list of the number of cars produced by each manufacturer,
    #                collect this information after the manufacturers are finished.
    return (run_time, q.get_max_size(), dealer_stats, manufacturer_stats)


def main():
    """ Main function """

    # Use 1, 1 to get your code working like the previous assignment, then
    # try adding in different run amounts. You should be able to run the
    # full 7 run amounts.
    #runs = [(1, 1)]
    runs = [(1, 1), (1, 2), (2, 1), (2, 2), (2, 5), (5, 2), (10, 10)]
    for manufacturers, dealerships in runs:
        run_time, max_queue_size, dealer_stats, manufacturer_stats = run_production(
            manufacturers, dealerships)

        print(f'Manufacturers       : {manufacturers}')
        print(f'Dealerships         : {dealerships}')
        print(f'Run Time            : {run_time:.2f} sec')
        print(f'Max queue size      : {max_queue_size}')
        print(f'Manufacturer Stats  : {manufacturer_stats}')
        print(f'Dealer Stats        : {dealer_stats}')
        print('')

        # The number of cars produces needs to match the cars sold (this should pass)
        assert sum(dealer_stats) == sum(manufacturer_stats)


if __name__ == '__main__':
    main()
