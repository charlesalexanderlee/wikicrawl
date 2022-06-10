# WikiCrawl
#### A graph network visualization tool for Wikipedia articles

I created this tool to experiment with web crawlers and data visualization. Given a Wikipedia article and a depth, it recursively traverses each link and outputs an adjacency list CSV file.

### Usage

`python wikicrawl.py -a <article_name> -d <depth> -s <sleep_time> -p <density>`

`-a, --article` The Wikipedia article to create the adjacency list CSV file from (replace spaces in article name with underscores)

`-d, --depth` Maximum depth to explore links (default=2)

`-s, --sleep` Sleep time in seconds to wait between each API call (default=0.5)

`-p, --density` Percentage of links to grab from each page on a scale from 0.0-1.0. Recommended to lower density if depth is above 2 (default=1.0)

### Example
`python wikicrawl.py --article Recursion --depth 2`

<img src="https://i.imgur.com/2GfekPU.jpg" width=50% height=50%>

*Network visualization of Recursion imported in Gephi*

