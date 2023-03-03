'''
Requirements
1. Write a multithreaded program that counts the number of prime numbers 
   between 10,000,000,000 and 10,000,110,003.
2. The program should be able to use a variable amount of threads.
3. Each thread should look over an approximately equal number of numbers.
   This means that you need to divise an algorithm that can divide up the
   110,003 numbers "fairly" based on a variable number of threads. 
   
Psuedocode: 
1. Create variable for the start number (10_000_000_000)
2. Create variable for range of numbers to examine (110_003)
3. Create variable for number of threads (start with 1 to get your program running,
   then increase to 5, then 10).
4. Determine an algorithm to partition the 110,003 numbers based on 
    the number of threads. Each thread should have approx. the same amount
    of numbers to examine. For example, if the number of threads is
    5, then the first 4 threads will examine 22,003 numbers, and the
    last thread will examine 22,003 numbers. Determine the start and
    end values of each partition.
5. Use these start and end values as arguments to a function.
6. Use a thread to call this function.
7. Create a function that loops from a start and end value, and checks
   if the value is prime using the isPrime function. Use the globals
   to keep track of the total numbers examined and the number of primes
   found. 

Questions:
1. Time to run using 1 thread = 16.82 sec
2. Time to run using 5 threads = 17.9 sec
3. Time to run using 10 threads = 17.68 sec
4. Based on your study of the GIL (see https://realpython.com/python-gil), 
   what conclusions can you draw about the similarity of the times (short answer)?
   >
   >
5. Is this assignment an IO Bound or CPU Bound problem (see https://stackoverflow.com/questions/868568/what-do-the-terms-cpu-bound-and-i-o-bound-mean)?
   >
'''

from datetime import datetime, timedelta
import math
import threading
import time

# Global count of the number of primes found
prime_count = 0

# Global count of the numbers examined
numbers_processed = 0


def is_prime(n: int):
    """
    Primality test using 6k+-1 optimization.
    From: https://en.wikipedia.org/wiki/Primality_test

    Returns
    -------
    bool
        True if ``n`` is prime.
    """

    if n <= 3:

        return n > 1
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i ** 2 <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def check_primes(thread_start, thread_end):
    #print(f'{threading.current_thread().name}: start={thread_start}, end={thread_end}\n', end="") #Debug Statement
    for n in range(int(thread_start), int(thread_end)):
        thread_results = is_prime(n)
        lock1.acquire()
        global numbers_processed 
        numbers_processed += 1
        lock1.release()
        if thread_results == True:
                lock2.acquire()
                global prime_count
                prime_count += 1
                lock2.release()

if __name__ == '__main__':
    # Start a timer
    begin_time = time.perf_counter()
    lock1 = threading.Lock()
    lock2 = threading.Lock()

    start_num = 10000000000
    num_range = 110003
    thread_num = 10

    divided_range = num_range // thread_num
    #print(f'{divided_range=}') #debug statement
    left_over = num_range % thread_num
    #print(f'{left_over=}') #debug statement

    thread_start = start_num
    thread_end = 10000000000 + divided_range + left_over

    threads = []

    if thread_num == 1:
        t1 = threading.Thread(target=check_primes, args=(thread_start,thread_end))
        t1.start()
        threads.append(t1)

    if thread_num > 1:
        t1 = threading.Thread(target=check_primes, args=(thread_start,thread_end))
        t1.start()
        threads.append(t1)

        for thread in range(2, thread_num + 1):
            thread_start = thread_end 
            thread_end += divided_range
            thread = threading.Thread(target=check_primes, args=(thread_start,thread_end))
            thread.start()
            threads.append(thread)

    for t in threads:
            t.join()

    # Use the below code to check and print your results
    assert numbers_processed == 110_003, f"Should check exactly 110,003 numbers but checked {numbers_processed}"
    assert prime_count == 4764, f"Should find exactly 4764 primes but found {prime_count}"

    print(f'Numbers processed = {numbers_processed}')
    print(f'Primes found = {prime_count}')
    total_time = "{:.2f}".format(time.perf_counter() - begin_time)
    print(f'Total time = {total_time} sec')
