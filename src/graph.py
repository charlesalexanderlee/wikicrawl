from io import TextIOWrapper
from requests import get
from pprint import pprint
from time import sleep
from random import sample
import csv


def get_links(page: str, depth: int, sleep_time: float, density: float) -> list[str]:
    '''
    Returns a list of links for a given Wikipedia article.
    https://www.mediawiki.org/wiki/API:Etiquette
    https://www.mediawiki.org/wiki/API:Links
    https://www.mediawiki.org/wiki/API:Linkshere
    https://www.mediawiki.org/wiki/Wikimedia_REST_API#Terms_and_conditions
    '''

    # Get all links for a page
    URL = "https://en.wikipedia.org/w/api.php"
    PARAMS = {
        "action": "parse",
        "format": "json",
        "page": page,
        "prop": "links"
    }
    HEADERS = {
        "User-Agent": f"WikiCrawl Visualization Bot (github.com/charlesalexanderlee/wikicrawl) (Threads/1 Max_Depth/{depth} Sleep/{sleep_time}s Density/{density*100}% Python/3.10.4)"
    }

    RESPONSE = get(url=URL, params=PARAMS, headers=HEADERS).json()

    try:
        DATA = RESPONSE["parse"]["links"]

        # Filter for links that are articles
        links = list()
        for LINK in DATA:
            if LINK["ns"] == 0:
                links.append(LINK["*"].replace(" ", "_"))
        return links

    # Returns empty list if Wikipedia page does not exist
    except KeyError:
        return list()


def build_graph (
    link: str, 
    depth: int, 
    path: str,
    height: int = 1,
    sleep_time: float = 0.5,
    density: float = 1.0
) -> list[str]:

    '''
    Creates an adjacency list and writes it to a CSV file.
    '''

    # Rate limit to respect the API etiqutte
    sleep(sleep_time)
    
    # Get a list of links for a given Wikipedia article
    links = get_links (
        page=link, 
        depth=depth+(height-1), 
        sleep_time=sleep_time, 
        density=density
    )
    
    # Grabs a certain percentage of random links from each page (specified by density parameter)  
    links = sample (
        population=links, 
        k=int(len(links)*density)
    )
    
    # Enumerate through each link and recursively visit it
    for idx, link in enumerate(links):
        # Prints current state of traversal
        print("  "*height, f"- [{idx+1}/{len(links)}] ({height}) {link}")

        if depth-1 > 0:
            # Recursive graph traversal
            row = build_graph (
                link=link, 
                depth=depth-1, 
                path=path,
                height=height+1,
                sleep_time=sleep_time,
                density=density
            )
            
            # Inserting parent article to beginning of list followed by it's links
            row.insert(0, link)

            # Appends the row to the CSV file
            with open(path, "a", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file, delimiter=";")
                writer.writerow(row)

    return links


# [Thread 1]: (depth_1) count/max_count | (depth_n) count/max_count | article
# [Stats]: Nodes = node_count | Edges = edge_count | File Size = file_size | Time Elapsed = time_elapsed
