from graph import build_graph
import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--article", help="Article name")
    parser.add_argument("-d", "--depth", help="Depth", default=2)
    parser.add_argument("-s", "--sleep", help="Sleep time", default=0.5)
    parser.add_argument("-p", "--density", help="Density", default=1.0)
    
    args = parser.parse_args()

    # Begin recursive network graph creation
    row = build_graph (
        link=args.article, 
        depth=int(args.depth), 
        path=f"{args.article}_{args.depth}_{str(args.density)}.csv", 
        sleep_time=float(args.sleep), 
        density=float(args.density)
    )

    # Covers final edge case when we return to our initial recursive call
    with open(PATH, "a", newline="", encoding="utf-8") as csv_file:
        row.insert(0, STARTING_LINK)
        writer = csv.writer(csv_file, delimiter=";")
        writer.writerow(row)


if __name__ == "__main__":
    main()
