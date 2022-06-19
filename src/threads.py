import threading
import csv
from queue import Queue, Empty
from time import sleep

class ThreadHandler:
    def __init__(self):
        self._queue = Queue()
        self.threads = list()
        self.running = False

    def writer(self, path: str):
        print("[WRITER THREAD STARTED]")
        sleep(5)
        try:
            with open(path, "a", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file, delimiter=";")

                while True:
                    try:
                        row = self._queue.get(timeout=5)
                        writer.writerow(row)
                        print(row[0])
                    except Empty as err:
                        break
                    except Exception as err:
                        print(err.__repr__())
                    

        except Exception as err:
            print(err.__repr__())        

    def start_writer_thread(self, path: str):
        print("[STARTING WRITER THREAD]")
        writer_thread = threading.Thread(target=self.writer, args=(path,))
        self.threads.append(writer_thread)
        writer_thread.start()


# [Thread 1]: (depth_1) count/max_count | (depth_n) count/max_count | article
# [Stats]: Nodes = node_count | Edges = edge_count | File Size = file_size | Time Elapsed = time_elapsed
# https://www.mediawiki.org/wiki/API:Etiquette
# https://www.mediawiki.org/wiki/API:Links
# https://www.mediawiki.org/wiki/API:Linkshere
# https://www.mediawiki.org/wiki/Wikimedia_REST_API#Terms_and_conditions