from graph import build_graph
import argparse


def main() -> None:
    # Parse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--article", type=str)
    parser.add_argument("-d", "--depth", default=2, type=int)
    parser.add_argument("-s", "--sleep", default=0.5, type=float)
    parser.add_argument("-p", "--density", default=1.0, type=float)
    args = parser.parse_args()

    # Creates adjacency list CSV file
    build_graph (
        link=args.article, 
        depth=int(args.depth), 
        path=f"{args.article}_{args.depth}_{args.density}.csv", 
        sleep_time=float(args.sleep), 
        density=float(args.density)
    )


if __name__ == "__main__":
    main()
