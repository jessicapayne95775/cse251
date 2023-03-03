'''
Requirements
1. Write a multithreaded program that calls a local web server. The web server is 
   provided to you. It will return data about the Star Wars movies.
2. You will make 94 calls to the web server, using 94 threads to get the data.
3. Using a new thread each time, obtain a list of the characters, planets, 
   starships, vehicles, and species of the sixth Star War movie.
3. Use the provided print_film_details function to print out the data 
   (should look exactly like the "sample_output.txt file).
   
Questions:
1. Is this assignment an IO Bound or CPU Bound problem (see https://stackoverflow.com/questions/868568/what-do-the-terms-cpu-bound-and-i-o-bound-mean)?
    >it is io bound because it has to wait for the input from the website to continue processing.
2. Review dictionaries (see https://isaaccomputerscience.org/concepts/dsa_datastruct_dictionary). How could a dictionary be used on this assignment to improve performance?
    >by using a dictionary, a key can be used to get a value vs looping through everything. This reduces the time that is needed to run the program.
'''


from datetime import datetime, timedelta
import time
import requests
import json
import threading


# Const Values
TOP_API_URL = 'http://127.0.0.1:8790'

# Global Variables
call_count = 0

#TODO create a thread class that uses the 'requests' module
#     to call the server using an URL.
class Request_thread(threading.Thread):

    def __init__(self, url):
        # Call the Thread class's init function
        threading.Thread.__init__(self)
        self.url = url
        self.response = {}

    def run(self):
        global call_count
        #print(f"########{self.url}")
        response = requests.get(self.url)
        
        # Check the status code to see if the request succeeded.
        if response.status_code == 200:
            self.response = response.json()
        elif response.status_code == 404:
            print(f"error:{self.url}")
        else:
            print('RESPONSE = ', response.status_code)
        call_count += 1

def print_film_details(film, chars, planets, starships, vehicles, species):
    '''
    Print out the film details in a formatted way
    '''
    
    def display_names(title, name_list):
        print('')
        print(f'{title}: {len(name_list)}')
        names = sorted([item["name"] for item in name_list])
        print(str(names)[1:-1].replace("'", ""))


    print('-' * 40)
    print(f'Title   : {film["title"]}')
    print(f'Director: {film["director"]}')
    print(f'Producer: {film["producer"]}')
    print(f'Released: {film["release_date"]}')

    display_names('Characters', chars)
    display_names('Planets', planets)
    display_names('Starships', starships)
    display_names('Vehicles', vehicles)
    display_names('Species', species)


def main():
    #Start a timer
    begin_time = time.perf_counter()
    
    print('Starting to retrieve data from the server')

    # TODO Using your thread class, retrieve TOP_API_URL to get
    # the list of the urls for each of the categories in the form
    # of a dictionary (open your browser and go to http://127.0.0.1:8790
    # to see the json/dictionary). Note that these categories are for
    # all the Star Wars movies.
    req = Request_thread(TOP_API_URL)
    req.start()
    req.join()

    characters_t = []
    spaceships_t = []
    planets_t = []
    species_t = []
    vehicles_t = []

    chars_responses = []
    spaceships_responses = []
    planets_responses = []
    species_responses = []
    vehicles_responses = []

    url6 = req.response["films"] + "6"
    film6 = Request_thread(url6)
    film6.start()
    film6.join()

    for character in film6.response["characters"]:
        t = Request_thread(character)
        t.start()
        characters_t.append(t)
    
    for t in characters_t:
        t.join()
        chars_responses.append(t.response)

    for spaceship in film6.response["starships"]:
        t = Request_thread(spaceship)
        t.start()
        spaceships_t.append(t)
    
    for t in spaceships_t:
        t.join()
        spaceships_responses.append(t.response)

    for planet in film6.response["planets"]:
        t = Request_thread(planet)
        t.start()
        planets_t.append(t)
    
    for t in planets_t:
        t.join()
        planets_responses.append(t.response)

    for spec in film6.response["species"]:
        t = Request_thread(spec)
        t.start()
        species_t.append(t)
    
    for t in species_t:
        t.join()
        species_responses.append(t.response)

    for vehic in film6.response["vehicles"]:
        t = Request_thread(vehic)
        t.start()
        vehicles_t.append(t)
    
    for t in vehicles_t:
        t.join()
        vehicles_responses.append(t.response)
    
    print_film_details(film6.response, chars_responses, planets_responses, spaceships_responses, vehicles_responses, species_responses)

    print(f'\nThere were {call_count} calls to the server')
    total_time = time.perf_counter() - begin_time
    total_time_str = "{:.2f}".format(total_time)
    print(f'Total time = {total_time_str} sec\n')
    
    # If you do have a slow computer, then put a comment in your code about why you are changing
    # the total_time limit. Note: 90+ seconds means that you are not doing multithreading
    assert total_time < 15, "Unless you have a super slow computer, it should not take more than 15 seconds to get all the data."
    
    assert call_count == 94, "It should take exactly 94 threads to get all the data"
    

if __name__ == "__main__":
    main()
