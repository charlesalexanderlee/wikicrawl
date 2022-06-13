from crawler import WikiCrawl
import argparse


def get_arguments() -> argparse.ArgumentParser:
    # Parse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--article", type=str)
    parser.add_argument("-d", "--depth", default=2, type=int)
    parser.add_argument("-s", "--sleep", default=0.5, type=float)
    parser.add_argument("-p", "--density", default=1.0, type=float)
    parser.add_argument("-t", "--threads", default=10, type=int)
    
    return parser.parse_args()


def main() -> None:
    # Get the command line arguments
    args = get_arguments()

    # Instantiate the WikiCrawl class
    wc = WikiCrawl (
        page=args.article, 
        path=f"{args.article}_{args.depth}_{args.density}.csv", 
        depth=int(args.depth), 
        density=float(args.density),
        sleep_time=float(args.sleep), 
        thread_count=int(args.threads)
    )

    # Start the crawling process and save an adjacency list to CSV file
    wc.start_crawler()


if __name__ == "__main__":
    main()
