import threading
import csv
from queue import Queue
from sys import exit

class ThreadHandler:
    def __init__(self, path: str):
        self.queue = Queue()
        self.threads = list()
        self.path = path


    def start_threads(self):
        print("[STARTING THREADS]")
        for thread in self.threads:
            thread.start()
        
        print("[STARTING QUEUE]")
        while threading.active_count() > 1 or not self.queue.empty():
            with open(self.path, "a", newline="", encoding="utf-8") as csv_file:
                try:
                    row = self.queue.get(timeout=60)
                    writer = csv.writer(csv_file, delimiter=";")
                    writer.writerow(row)
                except Exception as e:
                    print("EXCEPTION:", e.__repr__())
                    print(self.threads[0].join())
                    break
                    
        print("[QUEUE FINISHED]")
        print(threading.active_count())
        res = self.queue.get(timeout=1)
        print(res)

    def create_crawler_thread(self, target, links: list[str], depth: int, density: float, sleep_time: float):
        new_thread = threading.Thread(target=target, args=(links, depth, density, sleep_time, 1,))
        self.threads.append(new_thread)
    

# [Thread 1]: (depth_1) count/max_count | (depth_n) count/max_count | article
# [Stats]: Nodes = node_count | Edges = edge_count | File Size = file_size | Time Elapsed = time_elapsed
# https://www.mediawiki.org/wiki/API:Etiquette
# https://www.mediawiki.org/wiki/API:Links
# https://www.mediawiki.org/wiki/API:Linkshere
# https://www.mediawiki.org/wiki/Wikimedia_REST_API#Terms_and_conditions