import threading
import csv
from queue import Queue

class ThreadHandler:
    def __init__(self):
        self.queue = Queue()
        self.threads = list()


    def start_threads(self, path):
        for idx, thread in enumerate(self.threads):
            print(f"Starting thread {idx}")
            thread.start()
        
        print("--STARTING QUEUE")
        while threading.activeCount() > 0 or not self.queue.empty():
            with open(path, "a", newline="", encoding="utf-8") as csv_file:
                try:
                    # print("--getting from queue")
                    row = self.queue.get(timeout=1)
                    # print(row)
                    # print("--writing")
                    writer = csv.writer(csv_file, delimiter=";")
                    writer.writerow(row)
                except Exception as e:
                    print("EXCEPTION:", e)
        print("--QUEUE FINISHED")


    def create_thread(self, target, links, depth, density, sleep_time, thread_num):
        new_thread = threading.Thread(target=target, args=(thread_num, links, depth, density, sleep_time, 1))
        self.threads.append(new_thread)
    

# [Thread 1]: (depth_1) count/max_count | (depth_n) count/max_count | article
# [Stats]: Nodes = node_count | Edges = edge_count | File Size = file_size | Time Elapsed = time_elapsed
# https://www.mediawiki.org/wiki/API:Etiquette
# https://www.mediawiki.org/wiki/API:Links
# https://www.mediawiki.org/wiki/API:Linkshere
# https://www.mediawiki.org/wiki/Wikimedia_REST_API#Terms_and_conditions