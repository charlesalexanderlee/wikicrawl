from requests import get
from json import dumps
from queue import SimpleQueue
from time import time, sleep
from pprint import pprint

class Page:
    def __init__(self, title, depth, parent):
        self.title = title
        self.depth = depth
        self.parent = parent


def get_links(page: str, sleep_time: float) -> list[str]:
    '''
    Returns a list of links that point out of a given Wikipedia article.
    '''

    sleep(sleep_time)

    URL = "https://en.wikipedia.org/w/api.php"
    PARAMS = {
        "action": "query",
        "format": "json",
        "prop": "links",
        "titles": page,
        "pllimit": 500,
        "plnamespace": 0
    }
    HEADERS = {
        "User-Agent": f"WikiCrawl Bot (github.com/charlesalexanderlee/wikicrawl)"
    }
    RESPONSE = get(url=URL, params=PARAMS, headers=HEADERS).json()

    links = list()
    plcontinue = str()

    try:
        # Check if we need to continue making requests
        if list(RESPONSE.keys())[0] == "continue":
            plcontinue = RESPONSE["continue"]["plcontinue"]

        PAGE_ID = str(list(RESPONSE["query"]["pages"].keys())[0])
        LINKS = RESPONSE["query"]["pages"][PAGE_ID]["links"]

        for LINK in LINKS:
            if "identifier" not in LINK["title"]:
                links.append(LINK["title"].replace(" ", "_"))

        # If we aren't done making requests, then request the next batch until complete
        while list(RESPONSE.keys())[0] != "batchcomplete":
            sleep(sleep_time)
            
            PARAMS = {
                "action": "query",
                "format": "json",
                "prop": "links",
                "titles": page,
                "pllimit": 500,
                "plnamespace": 0,
                "plcontinue": plcontinue
            }
            RESPONSE = get(url=URL, params=PARAMS, headers=HEADERS).json()

            if list(RESPONSE.keys())[0] == "continue":
                plcontinue = RESPONSE["continue"]["plcontinue"]

            LINKS = RESPONSE["query"]["pages"][PAGE_ID]["links"]

            for LINK in LINKS:
                if "identifier" not in LINK["title"]:
                    links.append(LINK["title"].replace(" ", "_"))
        
        return links

    except KeyError:
        # Returns empty list if Wikipedia page does not exist
        print(f"[*] [get_links] {page} returned no links")
        return list()


def get_links_here(page: str, sleep_time: float) -> list[str]:
    '''
    Returns a list of links that point to a given Wikipedia article.
    '''

    sleep(sleep_time)

    URL = "https://en.wikipedia.org/w/api.php"
    PARAMS = {
        "action": "query",
        "format": "json",
        "prop": "linkshere",
        "titles": page,
        "lhlimit": 500,
        "lhnamespace": 0
    }
    HEADERS = {
        "User-Agent": f"WikiCrawl Bot (github.com/charlesalexanderlee/wikicrawl)"
    }
    RESPONSE = get(url=URL, params=PARAMS, headers=HEADERS).json()

    links_here = list()
    lhcontinue = str()

    try:
        # Check if we need to continue making requests
        if list(RESPONSE.keys())[0] == "continue":
            lhcontinue = RESPONSE["continue"]["lhcontinue"]

        # Get the page ID (seriously, why did they structure their responses like this?)
        PAGE_ID = str(list(RESPONSE["query"]["pages"].keys())[0])
        LINKS_HERE = RESPONSE["query"]["pages"][PAGE_ID]["linkshere"]

        # Add
        for LINK in LINKS_HERE:
            if "identifier" not in LINK["title"]:
                links_here.append(LINK["title"].replace(" ", "_"))

        # If we aren't done making requests, then request the next batch until complete
        while list(RESPONSE.keys())[0] != "batchcomplete":
            sleep(sleep_time)
            
            PARAMS = {
                "action": "query",
                "format": "json",
                "prop": "linkshere",
                "titles": page,
                "lhlimit": 500,
                "lhnamespace": 0,
                "lhcontinue": lhcontinue
            }
            RESPONSE = get(url=URL, params=PARAMS, headers=HEADERS).json()

            if list(RESPONSE.keys())[0] == "continue":
                lhcontinue = RESPONSE["continue"]["lhcontinue"]

            LINKS_HERE = RESPONSE["query"]["pages"][PAGE_ID]["linkshere"]

            for LINK in LINKS_HERE:
                if "identifier" not in LINK["title"]:
                    links_here.append(LINK["title"].replace(" ", "_"))

        return links_here

    except KeyError as err:
        # Returns empty list if Wikipedia page does not exist
        print(f"[*] [get_links_here] {page} returned no links")
        return list()


def find_paths(
    start_page: str,
    end_page: str, 
    max_depth: int, 
    max_paths: int, 
    sleep_time: float = 0.5) -> None:

    print("[STARTING PAGE]", start_page)
    print("[ENDING PAGE]", end_page)
    print("[MAX PATH LENGTH]", max_depth)
    print("[MAX PATH COUNT]", max_paths)
    print("[SLEEP TIME]", sleep_time, "secs" , end="\n\n")

    # Initialziation
    start_visited = dict()
    end_visited = dict()
    start_q = SimpleQueue()
    end_q = SimpleQueue()
    start_time = time()
    path_count = 0

    # Initalize starting page queue (works forwards)
    parent_page = Page(title=start_page, depth=0, parent=None)
    start_visited[start_page] = parent_page
    start_q.put(parent_page)

    # Initialize ending page queue (works backwards)
    parent_page = Page(title=end_page, depth=0, parent=None)
    end_visited[end_page] = parent_page
    end_q.put(parent_page)

    # Switch between both queues to work towards each other
    while not start_q.empty() and not end_q.empty():
        # Propagate in the forward direction
        parent_page = start_q.get()

        # what if keys get replaced by a new node with a different parent?

        for link in get_links(page=parent_page.title, sleep_time=sleep_time):
            if path_count >= max_paths:
                exit(0)

            try:
                # Checks if the forward direction reaches the end page
                if link == end_page:
                    path_count += 1
                    path = list()
                    path.insert(0, link)
                    current_page = parent_page

                    while current_page.parent != None:
                        path.insert(0, current_page.title)
                        current_page = current_page.parent
                    path.insert(0, current_page.title)

                    print(f"[#{path_count}] [{round(time() - start_time, 3)} secs] [A] [{len(path)}] {path}")

                # Checks if the forward direction reaches a link that has already been visited by the backward direction
                elif end_visited[link]:
                    path_count += 1
                    path = list()
                    path.insert(0, link)
                    current_page = parent_page
                    
                    while current_page.parent != None:
                        path.insert(0, current_page.title)
                        current_page = current_page.parent
                    path.insert(0, current_page.title)

                    current_page = end_visited[link].parent
                    
                    while current_page.parent != None:
                        path.append(current_page.title)
                        current_page = current_page.parent
                    path.append(current_page.title)

                    print(f"[#{path_count}] [{round(time() - start_time, 3)} secs] [B] [{len(path)}] {path}")

            except KeyError as err:
                pass

            child_page = Page(title=link, depth=parent_page.depth+1, parent=parent_page)
            start_visited[child_page.title] = child_page

            if child_page.depth <= max_depth:
                start_q.put(child_page)

        # Propagate in the backward direction
        parent_page = end_q.get()

        for link in get_links_here(page=parent_page.title, sleep_time=sleep_time):
            if path_count >= max_paths:
                exit(0)

            try:
                # Checks if the backward direction reaches the start page
                if link == start_page:
                    path_count += 1
                    path = list()
                    path.insert(0, link)
                    current_page = parent_page

                    while current_page.parent != None:
                        path.insert(0, current_page.title)
                        current_page = current_page.parent
                    path.insert(0, current_page.title)

                    print(f"[#{path_count}] [{round(time() - start_time, 3)} secs] [C] [{len(path)}] {path}")

                # Checks if backward direction visits a link that has already been visited by the forward direction
                elif start_visited[link]:
                    path_count += 1
                    path = list()
                    current_page = start_visited[link]
                    
                    while current_page.parent != None:
                        path.insert(0, current_page.title)
                        current_page = current_page.parent
                    path.insert(0, current_page.title)

                    current_page = parent_page
                    
                    while current_page.parent != None:
                        path.append(current_page.title)
                        current_page = current_page.parent
                    path.append(current_page.title)

                    print(f"[#{path_count}] [{round(time() - start_time, 3)} secs] [D] [{len(path)}] {path}")

            except KeyError as err:
                pass

            child_page = Page(title=link, depth=parent_page.depth+1, parent=parent_page)
            end_visited[child_page.title] = child_page

            if child_page.depth <= max_depth:
                end_q.put(child_page)


def main():
    # Starting parameters
    start_page = "Y_Combinator"
    end_page = "Central_Intelligence_Agency"
    max_depth = 5
    max_paths = 1000
    sleep_time = 0.25

    # Bi-directional search with double queue and double visited dictionary approach
    find_paths(
        start_page=start_page, 
        end_page=end_page, 
        max_depth=max_depth, 
        max_paths=max_paths, 
        sleep_time=sleep_time
    )

if __name__ == "__main__":
    main()
