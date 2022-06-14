from threads import ThreadHandler
from requests import get
from time import sleep
from random import sample
import json

class WikiCrawl:
    def __init__(
        self,
        page: str,
        path: str,
        depth: int = 2,
        density: float = 1.0,
        sleep_time: float = 0.5,
        thread_count: int = 10
    ):
        self.page = page
        self.path = path
        self.depth = depth
        self.density = density
        self.sleep_time = sleep_time
        self.thread_count = thread_count
        self.thread_handler = ThreadHandler()


    def get_links(self, page: str) -> list[str]:
        '''
        Returns a list of links for a given Wikipedia article.
        '''

        URL = "https://en.wikipedia.org/w/api.php"
        PARAMS = {
            "action": "parse",
            "format": "json",
            "page": page,
            "prop": "links"
        }
        HEADERS = {
            "User-Agent": f"WikiCrawl Bot (github.com/charlesalexanderlee/wikicrawl)",
            "Parameters": json.dumps({
                "Root-Article": self.page,
                "Thread-Count": 1,
                "Sleep-Time-(s)": self.sleep_time,
                "Density": self.density*100,
                "Python-Version": "3.10.4"
            })
        }
        RESPONSE = get(url=URL, params=PARAMS, headers=HEADERS).json()

        try:
            # Filter for links that are articles
            DATA = RESPONSE["parse"]["links"]
            
            links = list()
            for LINK in DATA:
                if LINK["ns"] == 0:
                    links.append(LINK["*"].replace(" ", "_"))
            return links

        except KeyError:
            # Returns empty list if Wikipedia page does not exist
            return list()


    def split_list(self, array: list[str], n=1) -> list[list[str]]:
        '''
        Returns a list split into n lists.
        '''
        return [
            array[i*len(array)//n : (i+1)*len(array)//n] 
            for i in range(n)
        ]


    def crawl(
        self,
        thread_num: int,
        links: list[str],
        depth: int, 
        density: float = 1.0,
        sleep_time: float = 0.5,
        height: int = 1) -> list[str]:
        '''
        Creates an adjacency list and writes it to a CSV file.
        '''

        # Rate limit to respect the API etiqutte
        sleep(sleep_time)
            
        # Grabs a certain percentage of random links from each page (specified by density parameter)  
        links = sample(population=links, k=int(len(links)*density))
        
        # Enumerate through each link and recursively visit it
        for link in links:
            # Prints current state of traversal
            # print("  "*height, f"- [{idx}/{len(links)}] ({height}) {link}")
            print(f"[Thread {thread_num}] {link}")

            if depth-1 > 0:
                # Recursive graph traversal, returns a list starting with parent followed by its links
                row = self.crawl(
                    thread_num=thread_num,
                    links=self.get_links(page=link),
                    depth=depth-1, 
                    density=density,
                    sleep_time=sleep_time,
                    height=height+1,
                )

                # Append parent to beginning of list
                row.insert(0, link)

                # print(row)
                # print("--putting to queue")
                self.thread_handler.queue.put(row)

        return links


    def start_crawler(self):
        # Get links for the input article
        links = self.get_links(page=self.page)
        
        # Grab a sample of the links specified by density
        links = sample(population=links, k=int(self.density*len(links)))
        
        # Split links into n lists for multi-threading
        split_links = self.split_list(array=links, n=self.thread_count)

        for thread_num, links in enumerate(split_links):
            self.thread_handler.create_thread(
                thread_num=thread_num,
                target=self.crawl,
                links=links,
                depth=self.depth,
                density=self.density,
                sleep_time=self.sleep_time
            )

        self.thread_handler.start_threads(path=self.path)
