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
        sleep_time: float = 0.5
    ):
        self.page = page
        self.path = path
        self.depth = depth
        self.density = density
        self.sleep_time = sleep_time

    def get_links(self, page: str, prop: str, sleep_time: float = 0.5) -> list[str]:
    
        '''
        Returns a list of links that point out of or into a Wikipedia page.
        The `prop` parameter specifies whether to grab `links` or `linkshere`
        '''

        sleep(sleep_time)

        limit_type = str()
        namespace_type = str()
        continue_type = str()
        continue_value = str()
        links = list()
        
        if prop == "links":
            limit_type = "pllimit"
            namespace_type = "plnamespace"
            continue_type = "plcontinue"
        elif prop == "linkshere":
            limit_type = "lhlimit"
            namespace_type = "lhnamespace"
            continue_type = "lhcontinue"

        URL = "https://en.wikipedia.org/w/api.php"
        PARAMS = {
            "action": "query",
            "format": "json",
            "prop": prop,
            "titles": page,
            limit_type: 500,
            namespace_type: 0
        }
        HEADERS = {
            "User-Agent": f"WikiCrawl Bot (simulacrasimulation@protonmail.com)"
        }
        RESPONSE = get(url=URL, params=PARAMS, headers=HEADERS).json()

        try:
            # Check if we need to continue making requests
            if list(RESPONSE.keys())[0] == "continue":
                continue_value = RESPONSE["continue"][continue_type]

            PAGE_ID = str(list(RESPONSE["query"]["pages"].keys())[0])
            LINKS = RESPONSE["query"]["pages"][PAGE_ID][prop]

            for LINK in LINKS:
                if "identifier" not in LINK["title"]:
                    links.append(LINK["title"].replace(" ", "_"))

            # Make next request if there are more links to grab
            while list(RESPONSE.keys())[0] != "batchcomplete":
                sleep(sleep_time)
                
                PARAMS = {
                    "action": "query",
                    "format": "json",
                    "prop": prop,
                    "titles": page,
                    limit_type: 500,
                    namespace_type: 0,
                    continue_type: continue_value
                }
                RESPONSE = get(url=URL, params=PARAMS, headers=HEADERS).json()

                if list(RESPONSE.keys())[0] == "continue":
                    continue_value = RESPONSE["continue"][continue_type]

                LINKS = RESPONSE["query"]["pages"][PAGE_ID][prop]

                for LINK in LINKS:
                    if "identifier" not in LINK["title"]:
                        links.append(LINK["title"].replace(" ", "_"))
            
            return links

        except KeyError:
            # Returns empty list if Wikipedia page does not exist
            print(f"[*] [{prop}] {page} returned no links")
            return list()


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
                    links=self.get_links(page=link, prop="links", sleep_time=sleep_time),
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
        links = self.get_links(page=self.page, prop="links", sleep_time=self.sleep_time)
        
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
