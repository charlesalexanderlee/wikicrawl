from requests import get
from time import sleep
from random import sample
from json import dumps
import csv


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
            "Parameters": dumps({
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


    def split_links(self, links: list[str], n=1) -> list[list[str]]:
        '''
        Returns a list split into n lists.
        '''
        return [
            links[i*len(links)//n : (i+1)*len(links)//n] 
            for i in range(n)
        ]


    def crawl(
        self,
        links: list[str],
        path: str, 
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
        for idx, link in enumerate(links):
            # Prints current state of traversal
            print("  "*height, f"- [{idx+1}/{len(links)}] ({height}) {link}")

            if depth-1 > 0:
                # Recursive graph traversal
                row = self.crawl(
                    links=self.get_links(page=link),
                    path=path, 
                    depth=depth-1, 
                    density=density,
                    sleep_time=sleep_time,
                    height=height+1,
                )
                
                # Inserting parent article to beginning of list followed by it's links
                row.insert(0, link)

                # Appends the row to the CSV file
                with open(path, "a", newline="", encoding="utf-8") as csv_file:
                    writer = csv.writer(csv_file, delimiter=";")
                    writer.writerow(row)

        return links


    def start_crawler(self):
        # Get links for the input article
        links = self.get_links(page=self.page)
        
        # Grab a sample of the links specified by density
        links = sample(population=links, k=int(self.density*len(links)))

        # Start the crawler
        row = self.crawl(
            links = links, 
            path = self.path,
            depth = self.depth, 
            density = self.density,
            sleep_time = self.sleep_time
        )

        # Covers final edge case when we return to our initial recursive call
        with open(self.path, "a", newline="", encoding="utf-8") as csv_file:
            row.insert(0, self.page)
            writer = csv.writer(csv_file, delimiter=";")
            writer.writerow(row)


# [Thread 1]: (depth_1) count/max_count | (depth_n) count/max_count | article
# [Stats]: Nodes = node_count | Edges = edge_count | File Size = file_size | Time Elapsed = time_elapsed
# https://www.mediawiki.org/wiki/API:Etiquette
# https://www.mediawiki.org/wiki/API:Links
# https://www.mediawiki.org/wiki/API:Linkshere
# https://www.mediawiki.org/wiki/Wikimedia_REST_API#Terms_and_conditions
