import argparse
from ..utils.io import processed_path, write_table, SCHEMAS

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    args = ap.parse_args()
    path = processed_path(args.country, "institutions.csv")
    write_table(path, SCHEMAS["institutions.csv"], [])
    print(f"Wrote {path}")