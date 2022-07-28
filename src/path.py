from requests import get
from json import dumps
from queue import SimpleQueue
from time import time, sleep

class Page:
    def __init__(self, title, depth, parent):
        self.title = title
        self.depth = depth
        self.parent = parent


def get_random_page(sleep_time: float = 0.5):
    '''
    Returns a random Wikipedia article title
    '''

    sleep(sleep_time)

    URL = "https://en.wikipedia.org/w/api.php"
    PARAMS = {
        "action": "query",
        "format": "json",
        "list": "random",
        "rnnamespace": 0,
        "rnlimit": 1
    }
    HEADERS = {
        "User-Agent": f"WikiCrawl Bot (simulacrasimulation@protonmail.com)"
    }
    RESPONSE = get(url=URL, params=PARAMS, headers=HEADERS).json()

    return RESPONSE["query"]["random"][0]["title"].replace(" ", "_")


def get_links(page: str, prop: str, sleep_time: float = 0.5) -> list[str]:
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


def find_paths(
    start_page: str,
    end_page: str, 
    max_depth: int, 
    max_results: int, 
    sleep_time: float = 0.5) -> None:

    print("[STARTING PAGE]", start_page)
    print("[ENDING PAGE]", end_page)
    print("[MAX PATH LENGTH]", max_depth)
    print("[MAX RESULTS]", max_results)
    print("[WAIT TIME]", sleep_time, "secs" , end="\n\n")

    # Initialziation
    start_visited = dict()
    end_visited = dict()
    start_q = SimpleQueue()
    end_q = SimpleQueue()
    start_time = time()
    result_count = 0

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
        # Search in the forward direction
        parent_page = start_q.get()

        # what if keys get replaced by a new node with a different parent?

        for link in get_links(page=parent_page.title, prop="links", sleep_time=sleep_time):
            if result_count >= max_results:
                exit(0)

            try:
                # Checks if the forward direction reaches the end page [A]
                if link == end_page:
                    path = list()
                    path.insert(0, link)
                    current_page = parent_page

                    while current_page.parent != None:
                        path.insert(0, current_page.title)
                        current_page = current_page.parent
                    path.insert(0, current_page.title)

                    
                    result_count += 1
                    print(f"[#{result_count}] [{round(time() - start_time, 3)} secs] [A] [{len(path)}] {path}")

                # Checks if the forward direction reaches a link that has already been visited by the backward direction [B]
                elif end_visited[link]:
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

                    result_count += 1
                    print(f"[#{result_count}] [{round(time() - start_time, 3)} secs] [B] [{len(path)}] {path}")

            except KeyError as err:
                pass

            child_page = Page(title=link, depth=parent_page.depth+1, parent=parent_page)
            start_visited[child_page.title] = child_page

            if child_page.depth <= max_depth:
                start_q.put(child_page)

        # Search in the backward direction
        parent_page = end_q.get()

        for link in get_links(page=parent_page.title, prop="linkshere", sleep_time=sleep_time):
            if result_count >= max_results:
                exit(0)

            try:
                # Checks if the backward direction reaches the start page [C]
                if link == start_page:
                    path = list()
                    path.insert(0, link)
                    current_page = parent_page

                    while current_page.parent != None:
                        path.insert(0, current_page.title)
                        current_page = current_page.parent
                    path.insert(0, current_page.title)

                    result_count += 1
                    print(f"[#{result_count}] [{round(time() - start_time, 3)} secs] [C] [{len(path)}] {path}")

                # Checks if backward direction visits a link that has already been visited by the forward direction [D]
                elif start_visited[link]:
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

                    result_count += 1
                    print(f"[#{result_count}] [{round(time() - start_time, 3)} secs] [D] [{len(path)}] {path}")

            except KeyError as err:
                pass

            child_page = Page(title=link, depth=parent_page.depth+1, parent=parent_page)
            end_visited[child_page.title] = child_page

            if child_page.depth <= max_depth:
                end_q.put(child_page)


def main():
    '''
    Main function: change the parameters here to
    altert the behavior of the program.
    '''
    # start_page = get_random_page()
    # end_page = get_random_page()
    start_page = "Chikki_Panday"
    end_page = "Autism"                      
    max_depth = 5
    max_results = 25
    sleep_time = 0.1

    # Bi-directional BFS with double-queue and double-dictionary approach
    find_paths(
        start_page=start_page, 
        end_page=end_page, 
        max_depth=max_depth, 
        max_results=max_results, 
        sleep_time=sleep_time
    )

if __name__ == "__main__":
    main()
