import queue
import threading
import time

from virusApi import *

TOP_API_URL = 'http://127.0.0.1:8129'
NUMBER_GENERATIONS = 2  # set this to 2 as you are testing your code
NUMBER_THREADS = 2  # TODO use this to keep track of the number of threads you create

# -----------------------------------------------------------------------------

def create_family(family_id, q: queue.Queue, pandemic: Pandemic):
    if family_id is None:
        return

    family_response = requests.get(f'http://{hostName}:{serverPort}/family/{family_id}')
    if 'id' not in family_response.json():
        return

    family = Family.fromResponse(family_response.json())
    pandemic.add_family(family)

    any_more_parents = False

    virus1 = None
    virus2 = None

    if family.virus1 is not None:
        virus1_thread = Request_thread(f'http://{hostName}:{serverPort}/virus/{family.virus1}')
        virus1_thread.start()

    if family.virus2 is not None:
        virus2_thread = Request_thread(f'http://{hostName}:{serverPort}/virus/{family.virus2}')
        virus2_thread.start()

    offspring_threads = []
    for id in family.offspring:
        thread = Request_thread(f'http://{hostName}:{serverPort}/virus/{id}')
        offspring_threads.append(thread)
        thread.start()

    if family.virus1 is not None:
        virus1_thread.join()
        response = virus1_thread.response
        if response:
            virus1 = response.json()

    if family.virus2 is not None:
        virus2_thread.join()
        response = virus2_thread.response
        if response:
            virus2 = response.json()

    offspring = []
    for thread in offspring_threads:
        thread.join()
        response = thread.response
        if response:
            offspring.append(response.json())

    if virus1 is not None:
        v = Virus.createVirus(virus1)
        pandemic.add_virus(v)

        if v.parents is not None:
            q.put(v.parents)
            any_more_parents = True

    if virus2 is not None:
        v = Virus.createVirus(virus2)
        pandemic.add_virus(v)

        if v.parents is not None:
            q.put(v.parents)
            any_more_parents = True

    for o in offspring:
        v = Virus.createVirus(o)
        if not pandemic.does_virus_exist(v.id):
            pandemic.add_virus(v)

    if not any_more_parents:
        q.put("DONE")


def bfs(start_id, generations):
    pandemic = Pandemic(start_id)

    # tell server we are starting a new generation of viruses
    requests.get(f'{TOP_API_URL}/start/{generations}')

    # create a queue to store family ids
    q = queue.Queue()

    # put on the first family id
    q.put(start_id)

    threads = []

    # create threads to process family ids
    for i in range(NUMBER_THREADS):
        t = threading.Thread(target=create_family, args=(None, q, pandemic))
        threads.append(t)
        t.start()

    # wait for threads to complete
    for t in threads:
        t.join()

    requests.get(f'{TOP_API_URL}/end')

    print('')
    print(f'Total Viruses  : {pandemic.get_virus_count()}')
    print(f'Total Families : {pandemic.get_family_count()}')
    print(f'Generations    : {generations}')

    return pandemic.get_virus_count()


class Request_thread(threading.Thread):

    def __init__(self, url):
        # Call the Thread class's init function
        threading.Thread.__init__(self)
        self.url = url
        self.response = {}

    def run(self):
        response = requests.get(self.url)
        # Check the status code to see if the request succeeded.
        if response.status_code == 200:
            self.response = response.json()
        else:
            print('RESPONSE = ', response.status_code)

def main():
    # Start a timer
    begin_time = time.perf_counter()

    print(f'Pandemic starting...')
    print('#' * 60)

    response = requests.get(f'{TOP_API_URL}')
    jsonResponse = response.json()

    print(f'First Virus Family id: {jsonResponse["start_family_id"]}')
    start_id = jsonResponse['start_family_id']

    virus_count = bfs(start_id, NUMBER_GENERATIONS)

    total_time = time.perf_counter() - begin_time
    total_time_str = "{:.2f}".format(total_time)

    print(f'\nTotal time = {total_time_str} sec')
    print(f'Number of threads: {NUMBER_THREADS}')
    print(f'Performance: {round(virus_count / total_time, 2)} viruses/sec')


if __name__ == '__main__':
    main()
