import threading
'''
Requirements:
1. Create a class that extends the 'threading.Thread' class (see 
https://stackoverflow.com/questions/15526858/how-to-extend-a-class-in-python). This
means that the class IS a thread. 
   Any objects instantiated using this class ARE threads.
2. Instantiate this thread class that computes the sum of all numbers 
   between one and that number (exclusive)
Psuedocode:
1. In your class, write a constructor (in python a constructor is __init__) and 
allow a number
   to be passed in as a parameter.
2. The constructor should call the parent class's constructor:
   threading.Thread.__init__(self)
3. Create a local sum variable in your constructor.
4. A thread must have a run function, so create a run function that sums from one 
to the 
   passed in number (inclusive).
5. In the run function, set the sum on self.
6. In main, instantiate your thread class with the a value of 10.
7. Start the thread.
8. Wait for the thread to finish.
9. Assert that thread object's sum attribute is equal to the appropriate value (see
main).
10. Repeat steps 7 through 10 using a value of 13.
11. Repeat steps 7 through 10 using a value of 17.
Things to consider:
a. How do you instantiate a class and pass in arguments (see 
https://realpython.com/lessons/instantiating-classes/)?
b. How do you start a thread object (see this week's reading)?
c. How will you wait until the thread is done (see this week's reading)?
d. How do you get the value an object's attribute (see https://datagy.io/python-
print-objects-attributes/)?
'''
######################
# DO NOT USE GLOBALS #
######################
import threading
# TODO - Create a thread class
class Sum_thread(threading.Thread): #extends threading to class
      def __init__(self, number):   #constructs the class with itself and number as a parameter
         threading.Thread.__init__(self) #You must initiate the super class
         self.number = number          # defining parameter
         self.sum = 0                  #defining variable
      def run(self):                   #override the built-in run function; doing what we want it to
         for num in range(self.number):   #Loop all the numbers to the declared number
            self.sum += num            #add each number to the total sum until declared number
 
def main():
   # Instantiate your thread class and pass in 10.
   thread1 = Sum_thread(10) #store object in variable and pass 10 into the number slot in the class
   thread2 = Sum_thread(13) #store object in variable and pass 13 into the number slot in the class
   thread3 = Sum_thread(17) #store object in variable and pass 17 into the number slot in the class
   thread1.start()   #starts the thread. Do not use run().
   thread2.start()
   thread3.start()
   thread1.join()    #Ensures the thread finishes before moving on to the next set of code
   # Test (assert) if its sum attribute is equal to 45.
   assert thread1.sum == 45, f'The sum should equal 45 but instead was {thread1.sum}'
   thread2.join()
   # Repeat, passing in 13
   assert thread2.sum == 78, f'The sum should equal 78 but instead was {thread2}'
   thread3.join()
   # Repeat, passing in 17
   assert thread3.sum == 136, f'The sum should equal 136 but instead was {thread3}'
if __name__ == '__main__': #makes sure the file that is running is the main file.
    main()
    assert threading.active_count() == 1 #tests to see if there are 1 thread running actively
    print("DONE") #Shows that the program ran and finished without errors