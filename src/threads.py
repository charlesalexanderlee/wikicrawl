import threading
import csv
from queue import Queue, Empty

class ThreadHandler:
    '''
    Manages multi-threading capabilities for WikiCrawl.
    Currently only creates a separate thread dedicated to
    writing rows to a CSV file.
    '''
    def __init__(self):
        self.q = Queue()
        self.threads = list()

    def writer_thread(self, path: str):
        '''
        Writer thread responsible for writing data to file
        '''
        # print("[WRITER THREAD STARTED]")
        with open(path, "a", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file, delimiter=";")

            while True:
                try:
                    row = self.q.get(timeout=5)
                    writer.writerow(row)
                    # print(row[0])
                except Empty:
                    # print("[WRITER THREAD FINISHED]")
                    break
                except Exception as err:
                    print(err.__repr__()) 

    def start_writer_thread(self, path: str):
        '''
        Creates a writer thread and starts it
        '''
        # print("[STARTING WRITER THREAD]")
        writer_thread = threading.Thread(target=self.writer_thread, args=(path,))
        self.threads.append(writer_thread)
        writer_thread.start()
