from crawler import WikiCrawl
import argparse


def get_arguments() -> argparse.Namespace:
    '''
    Parse the command line arguments.
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--article", type=str)
    parser.add_argument("-d", "--depth", type=int, default=2)
    parser.add_argument("-s", "--sleep", type=float, default=0.5)
    parser.add_argument("-p", "--density", type=float, default=1.0)

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
    )

    # Start the crawling process and save an adjacency list to CSV file
    wc.start_crawler()


if __name__ == "__main__":
    main()
